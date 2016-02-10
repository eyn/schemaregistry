"""
    tests.memorystorage
    ~~~~~~~~~~~~~~~~~~~

    Tests the Memory Storage container.

    :copyright: (c) 2016 by James Moore.
    :license: BSD, see LICENSE for more details.
"""

import pytest
from schemaregistry.storage.error import SchemaDoesNotExisitError, SchemaExistsError

def test_create_schema(storageengine):
    storageengine.create_schema('test')
    schemas = storageengine.get_schemas()
    assert 'test' in schemas

def test_cannot_create_already_exisiting_schema(storageengine):
    storageengine.create_schema('test')

    with pytest.raises(SchemaExistsError):
        storageengine.create_schema('test')

def test_create_schema_version(storageengine):
    storageengine.create_schema('test')
    version_number = storageengine.create_schema_version('test', 'new schema version')
    schema = storageengine.get_schema_version('test', version_number)

    assert 'new schema version' == schema


def test_cannot_create_schema_version_on_non_exisitant_schema(storageengine):
    with pytest.raises(SchemaDoesNotExisitError):
        storageengine.create_schema_version('non_existiant_schema', 'new schema version')


def test_reports_correct_schema_versions():
    pass