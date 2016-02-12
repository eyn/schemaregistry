"""
    tests.basestorage
    ~~~~~~~~~~~~~~~~~~~

    Tests Storage containers.

    :copyright: (c) 2016 by James Moore.
    :license: BSD, see LICENSE for more details.
"""

import pytest
from schemaregistry.storage.error import SchemaDoesNotExistError, SchemaExistsError

values = {
    'default_schema_name': 'test',
    'default_schema_v1': 'new schema version',
    'default_schema_v2': 'new schema version 2',
    'default_schema_v3': 'new schema version 3',
    'non_existant_schema': 'non_existant_schema',
    'additional_schema_name_1': 'schema_1',
    'additional_schema_name_2': 'schema_2'
}

def v(name):
    return values[name]


def test_create_schema(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    schemas = storageengine.get_schemas()
    assert v('default_schema_name') in schemas


def test_cannot_create_already_exisiting_schema(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    with pytest.raises(SchemaExistsError):
        storageengine.create_schema(v('default_schema_name'))


def test_create_multiple_schemas(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    storageengine.create_schema(v('additional_schema_name_1'))
    storageengine.create_schema(v('additional_schema_name_2'))

    schemas = storageengine.get_schemas()
    assert False not in [x in schemas for x in [v('default_schema_name'), v('additional_schema_name_1'), v('additional_schema_name_2')]]

def test_create_schema_version(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    version_number = storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v1'))
    schema = storageengine.get_schema_version(v('default_schema_name'), version_number)
    assert v('default_schema_v1') == schema


def test_cannot_create_schema_version_on_non_exisitant_schema(storageengine):
    with pytest.raises(SchemaDoesNotExistError):
        storageengine.create_schema_version(v('non_existant_schema'), v('default_schema_v1'))


def test_reports_correct_schema_versions(storageengine):
    versions = []
    storageengine.create_schema(v('default_schema_name'))
    versions += [storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v1'))]
    versions += [storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v2'))]
    versions += [storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v3'))]
    assert storageengine.get_schema_versions(v('default_schema_name')) == versions


def test_get_schema_versions_throws_on_non_existant_schema(storageengine):
    with pytest.raises(SchemaDoesNotExistError):
        storageengine.get_schema_versions(v('non_existant_schema'))


def test_returns_correct_schema_for_version(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    version_number = storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v1'))
    version_number_2 = storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v2'))
    version_number_3 = storageengine.create_schema_version(v('default_schema_name'),  v('default_schema_v3'))

    schema = storageengine.get_schema_version(v('default_schema_name'), version_number_2)
    assert v('default_schema_v2') == schema


def test_throws_error_if_schema_version_requested_for_unknown_schema(storageengine):
    with pytest.raises(SchemaDoesNotExistError):
        storageengine.get_schema_version(v('non_existant_schema'), '')


def test_get_latest_schema(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    version_number = storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v1'))
    version_number_2 = storageengine.create_schema_version(v('default_schema_name'), v('default_schema_v2'))
    version_number_3 = storageengine.create_schema_version(v('default_schema_name'),  v('default_schema_v3'))

    latest_version = storageengine.get_latest_schema(v('default_schema_name'))

    assert v('default_schema_v3') == latest_version


def test_get_latest_schema_returns_none_when_no_versions_of_schema(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    latest_version = storageengine.get_latest_schema(v('default_schema_name'))
    assert latest_version is None


def test_get_latest_schema_throws_for_non_exisitant_schema(storageengine):
    with pytest.raises(SchemaDoesNotExistError):
        storageengine.get_latest_schema(v('non_existant_schema'))


def test_reports_created_schema_exists(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    assert storageengine.schema_exists(v('default_schema_name'))


def test_reports_missing_schema_does_not_exist(storageengine):
    storageengine.create_schema(v('default_schema_name'))
    assert False == storageengine.schema_exists(v('non_existant_schema'))
