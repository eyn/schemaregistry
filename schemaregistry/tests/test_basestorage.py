"""
    tests.memorystorage
    ~~~~~~~~~~~~~~~~~~~

    Tests the Memory Storage container.

    :copyright: (c) 2016 by James Moore.
    :license: BSD, see LICENSE for more details.
"""

import pytest
from schemaregistry.storage.error import SchemaDoesNotExistError, SchemaExistsError

def test_create_schema(storageengine):
    storageengine.create_schema('test')
    schemas = storageengine.get_schemas()
    assert 'test' in schemas

def test_cannot_create_already_exisiting_schema(storageengine):
    storageengine.create_schema('test')

    with pytest.raises(SchemaExistsError):
        storageengine.create_schema('test')

def test_reports_created_schema_exists(storageengine):
    storageengine.create_schema('test')

    assert storageengine.schema_exists('test')

def test_create_schema_version(storageengine):
    storageengine.create_schema('test')
    version_number = storageengine.create_schema_version('test', 'new schema version')
    schema = storageengine.get_schema_version('test', version_number)

    assert 'new schema version' == schema

def test_cannot_create_schema_version_on_non_exisitant_schema(storageengine):
    with pytest.raises(SchemaDoesNotExistError):
        storageengine.create_schema_version('non_existiant_schema', 'new schema version')

def test_reports_correct_schema_versions(storageengine):
    versions = []
    storageengine.create_schema('test')
    versions += [storageengine.create_schema_version('test', 'new schema version')]
    versions += [storageengine.create_schema_version('test', 'new schema version 2')]
    versions += [storageengine.create_schema_version('test', 'new schema version 3')]

    assert storageengine.get_schema_versions('test') == versions

def test_returns_correct_schema_for_version(storageengine):
    storageengine.create_schema('test')
    version_number = storageengine.create_schema_version('test', 'new schema version')
    version_number_2 = storageengine.create_schema_version('test', 'new schema version 2')
    version_number_3 = storageengine.create_schema_version('test', 'new schema version 3')

    schema = storageengine.get_schema_version('test', version_number_2)
    assert 'new schema version 2' == schema

def test_throws_error_if_schema_version_requested_for_unknown_schema(storageengine):
    with pytest.raises(SchemaDoesNotExistError):
        storageengine.create_schema_version('non_existiant_schema', 'new schema version')