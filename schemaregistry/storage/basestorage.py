"""
    basestorage.py
    ~~~~~~~~~~~~~~

    This module implements the base storage object

    :copyright: (c) by 2016 James Moore
    :license: BSD, see LICENSE for more details
"""

import hashlib
from error import SchemaAlreadyExistsError, SchemaDoesNotExisitError

class BaseStorage(object):
    """
    Base object providing default implementations for storage subclasses
    """
    '''
    Default implementations
    '''
    def get_schemas(self):
        """
        Returns a list of known schemas
        :return: A list of schema names
        """
        return [self._id_to_name(k) for k in self._do_get_schema_ids()]

    def get_schema_versions(self, name):
        """
        Returns the list of known versions for a schema
        :param name: The name of the schema
        :return: List of versions
        """
        id = self._name_to_id(name)
        schema = self._get_schema_by_id(id)

        if schema is None:
            return None

        return self._get_schema_versions(schema)

    def get_schema_version(self, name, version):
        """
        Given a schema name and version returns that schema version. Throws SchemaDoesNotExist if schema does not exist.

        :param name: The name of the schema
        :param version: The version of the schema
        :return: None if schema version does not exist. Otherwise the schema version.
        """
        id = self._name_to_id(name)
        schema = self._get_schema_by_id(id)

        if schema is None:
            raise SchemaDoesNotExisitError()

        return self._get_version(schema, version)

    def get_latest_schema(self, name):
        """
        Returns the latest version of a schema
        :param name: the schema name
        :return: the latest version of the schema
        """
        id = self._name_to_id(name)
        schema = self._get_schema_by_id(id)

        if schema is None:
            return None

        version_number = self._get_schema_latest_version_number(schema)
        return self.get_schema_version(name, version_number)

    def create_schema(self, name):
        """
        Creates a schema. Throws SchemaAlreadyExistsError if schema already exists
        :param name: The name of the schema
        """
        if self.schema_exists(name):
            raise SchemaAlreadyExistsError()

        id = self._name_to_id(name)
        self._do_create_schema(name, id)

    def schema_exists(self, name):
        """
        Checks if a schema exists
        :param name: The name of the schema
        :return: True if schema exists, false otherwise
        """
        id = self._name_to_id(name)
        return self._get_schema_by_id(id) is not None

    def create_schema_version(self, name, new_schema):
        """
        Creates a new version of a schema
        :param name: the name of the schema
        :param new_schema: the new version of the schema
        :return: the new version number
        """
        if not self.schema_exists(name):
            raise SchemaDoesNotExisitError()

        id = self._name_to_id(name)
        schema = self._get_schema_by_id(id)
        return self._do_create_schema_version(schema, new_schema)

    def _get_schema_latest_version_number(self, schema):
        """
        Returns latest version of a schema
        :param schema: The name of the schema
        :return: The latest version number
        """
        return max(self._get_schema_versions(schema))

    def _name_to_id(self, name):
        """
        Converts a schema name to a schema id
        :param name: The name of the schema
        :return: the schema's id
        """
        return hashlib.sha256(name).hexdigest()

    '''
    Abstract methods
    '''
    def _get_schema_by_id(self, id):
        """
        Converts a schema id into a schema
        :param id: The schema's id
        :return: the schema. None if schema does not exist
        """
        pass

    def _get_version(self, schema, version):
        """
        Returns a schema version
        :param schema: The schema
        :param version: The version required
        :return: The schema version or None if schema version doesn't exist
        """
        pass

    def _id_to_name(self, id):
        """
        Converts schema id into a schema name
        :param id: The id of the schema
        :return: The name of the schema
        """
        pass

    def _do_get_schema_ids(self):
        """
        Returns a list of schema ids
        :return: list containing schema ids
        """
        pass

    def _do_create_schema(self, name, id):
        """
        Creates a new schema
        :param name: The name of the schema
        :param id: The id of the schema
        """
        pass

    def _do_create_schema_version(self, schema, new_version):
        """
        Creates a new schema version
        :param schema: The schema
        :param new_version: The new schema version
        :return: The new version number
        """
        pass

    def _get_schema_versions(self, schema):
        """
        Returns a list of known versions of a schema
        :param schema: The schema
        :return: A list of versions for the schema
        """
        pass

