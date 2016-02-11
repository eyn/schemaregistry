"""
    rocksdb.py
    ~~~~~~~~~

    This module implements a rocksdb storage module

    :copyright: (c) by 2016 James Moore
    :license: BSD, see LICENSE for more details
"""
from __future__ import absolute_import
import os
import gc
import pickle
import rocksdb
import shutil
import tempfile

from .basestorage import BaseStorage

class RocksDB(BaseStorage):
    """
    Implementation of storage mechanism that keeps everything in rocksdb

    Storage as follows:
        key: %s.%s, self.__reverse_prefix, id => name
        key: %s.info % id => version metadata

        version metadata is serialised ordered list of versions where each entry is key name for the schema (%s.%s, id, rand())

        key: %s.%s => schema_object

        id is used as a handle for schema

    """
    def __init__(self, datafile_name):
        self.__datafile_name = datafile_name
        self.__reverse_prefix = b'_reverse______________________32'

        opts = rocksdb.Options()
        opts.create_if_missing=True
        opts.prefix_extractor = StaticPrefix()
        opts.merge_operator = VersionMerger()
        self.__db = rocksdb.DB(self.__datafile_name, opts)

    def __get_info_key(self, id):
        return b'{0}.info'.format(id)

    def __get_reverse_key(self, id):
        return b'{0}.{1}'.format(self.__reverse_prefix, id)

    def __get_temp_filename(self):
        return tempfile.mkdtemp(prefix='schemaregistry')

    def _get_schema_by_id(self, id):
        info_key = self.__get_info_key(id)
        return id if self.__db.get(info_key) is not None else None

    def __get_version_list(self, schema):
        info_key = self.__get_info_key(schema)
        bytes = self.__db.get(info_key)
        return pickle.loads(bytes)

    def _get_version(self, schema, version):
        version_list = self.__get_version_list(schema)
        index = version - 1
        if index < 0 or index >= len(version_list):
            return None

        version_key = version_list[index]
        bytes = self.__db.get(version_key)
        return pickle.loads(bytes)

    def _id_to_name(self, id):
        key_name = self.__get_reverse_key(id)
        name = self.__db.get(key_name)
        return name.decode('utf-8')

    def _do_get_schema_ids(self):
        prefix = self.__reverse_prefix
        iterator = self.__db.iterkeys()
        iterator.seek(prefix)

        retval = list()

        for id in iterator:
            if not id.startswith(prefix):
                break

            retval.append(id[33:])

        return retval

    def _get_schema_versions(self, schema):
        version_list = self.__get_version_list(schema)
        return range(1, len(version_list) + 1)

    def _do_create_schema(self, name, id):
        reverse_key = self.__get_reverse_key(id)
        info_key = self.__get_info_key(id)
        self.__db.put(reverse_key, name.encode('utf-8'))
        self.__db.put(info_key, pickle.dumps(list()))

    def _do_create_schema_version(self, schema, new_version):
        version_key = b'{0}.{1}'.format(schema, os.urandom(24).encode('base-64').replace('\n', ''))
        info_key = self.__get_info_key(schema)

        self.__db.merge(info_key, pickle.dumps([version_key]))
        self.__db.put(version_key, pickle.dumps(new_version))

        listbytes = self.__db.get(info_key)
        list = pickle.loads(listbytes)

        return list.index(version_key) + 1

class VersionMerger(rocksdb.interfaces.AssociativeMergeOperator):
    def merge(self, key, existing_value, value):
        if existing_value:
            existing_list = pickle.loads(existing_value)
            new_list = pickle.loads(value)
            existing_list.extend(new_list)
            return (True, pickle.dumps(existing_list))
        return (True, value)

    def name(self):
        return b'VersionMerger'

class StaticPrefix(rocksdb.interfaces.SliceTransform):
    def name(self):
        return b'static'

    def transform(self, src):
        return (0, 32)

    def in_domain(self, src):
        return len(src) >= 32

    def in_range(self, dst):
        return len(dst) == 32
