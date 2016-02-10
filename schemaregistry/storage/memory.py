"""
    memory.py
    ~~~~~~~~~

    This module implements an in memory storage module.

    THIS MODULE SHOULD NOT BE USED OTHER THAN FOR TESTING

    :copyright: (c) by 2016 James Moore
    :license: BSD, see LICENSE for more details
"""

from basestorage import BaseStorage

class Memory(BaseStorage):
    """
    Implementation of storage mechanism that keeps everything in memory
    """
    def __init__(self):
        self.__data = dict()
        self.__reverse_map = dict()

    def _get_schema_by_id(self, id):
        return self.__data.get(id)

    def _get_version(self, schema, version):
        return schema.get(version)

    def _id_to_name(self, id):
        return self.__reverse_map.get(id)

    def _do_get_schema_ids(self):
        return [k for k in self.__data]

    def _get_schema_versions(self, schema):
        return [k for k in schema]

    def _do_create_schema(self, name, id):
        self.__data[id] = dict()
        self.__reverse_map[id] = name

    def _do_create_schema_version(self, schema, new_version):
        new_version_number = self.__get_next_schema_version(schema)
        schema[new_version_number] = new_version
        return new_version_number

    def __get_next_schema_version(self, schema):
        return len(schema) + 1