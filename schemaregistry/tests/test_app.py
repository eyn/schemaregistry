"""
    tests.app
    ~~~~~~~~~~~~~~~~~~~

    Tests the Memory Storage container.

    :copyright: (c) 2016 by James Moore.
    :license: BSD, see LICENSE for more details.
"""
import json
import pytest

from app import app, reinit_db

'''
HELPER FUNCTIONS
'''
def create_schema(c, name, status_code=201):
    postresp = c.post('/schemas', data=dict(name=name))
    assert postresp.status_code == status_code

    if status_code == 201:
        return json.loads(postresp.data)['id']
    else:
        return postresp.data

def create_version(c, schema_name, version):
    schemaurl = '/schemas/{0}'.format(schema_name)
    verresp = c.post(schemaurl, data=version)
    assert verresp.status_code == 201
    return json.loads(verresp.data)['version']

'''
TEST FIXTURES
'''
@pytest.fixture()
def emptydb(tmpdir_factory):
    app.config['ROCKSDB_DATAFILE']  = str(tmpdir_factory.mktemp('schemaregistry', numbered=True))
    reinit_db()

'''
Test GET /schemas
'''
test_get_schemas_testparams = [
    ([], [], 200),                                                  # get schemas works when no schemas defined
    (['test'], ['test'], 200),                                      # get schemas works when schema defined
    (['test', dict(name='test', status_code=409)], ['test'], 200),  # cannot define same schema twice
    (['test', 'test2'], ['test', 'test2'], 200),                    # get schemas works when multiple schemas defined

]
@pytest.mark.usefixtures("emptydb")
@pytest.mark.parametrize("schemas,retval,status_code", test_get_schemas_testparams)
def test_get_schemas(schemas, retval, status_code):
    with app.test_client() as c:
        for schema in schemas:
            if(isinstance(schema, dict)):
                create_schema(c, **schema)
            else:
                create_schema(c, schema)

        resp = c.get('/schemas')
        data = json.loads(resp.data)
        assert set(data) == set(retval) #order not important
        assert resp.status_code == status_code

'''
Test GET /schemas?id=.....
'''
test_get_schema_by_id_testparams = [
    (['test', 'test2'], '/schemas?id={1}', ['test2'], 200), # retrieve second item by id
    (['test', 'test2'], '/schemas?id={0}', ['test'], 200),  # first item by id
    (['test', 'test2'], '/schemas?id=Unknown', [], 200),    # handle unknown ids
]
@pytest.mark.usefixtures("emptydb")
@pytest.mark.parametrize("schemas, get_url, retval, status_code", test_get_schema_by_id_testparams)
def test_get_schema_by_id(schemas, get_url, retval, status_code):
    with app.test_client() as c:
        ids = []

        for schema in schemas:
            ids.append(create_schema(c, schema))

        url = get_url.format(*ids)
        resp = c.get(url)
        list = json.loads(resp.data)
        assert retval == list
        assert resp.status_code == status_code

'''
GET /schemas/<name>/<version>
'''
test_get_schema_versions_testparams = [
    # non-existant schema returns 404
    ([],[], '/schemas/non_existant', dict(status_code=404, data='Schema does not exist', use_collected_versions=False)),

    # schema with no version returns empty list
    (['test'], [], '/schemas/test', dict(status_code=200, use_collected_versions=True)),

    # schema with one version returns it in its list
    (['test'], ['new schema'], '/schemas/test', dict(status_code=200, use_collected_versions=True)),

    # schema with multiple versions returns them in its list
    (['test'], ['new schema','new schema 2', 'new schema 3'],
            '/schemas/test', dict(status_code=200, use_collected_versions=True)),
]
@pytest.mark.usefixtures("emptydb")
@pytest.mark.parametrize("schemas,versions,get_url,expected_response", test_get_schema_versions_testparams)
def test_get_schema_version(schemas,versions,get_url,expected_response):
    with app.test_client() as c:
        version_list = list()

        if len(schemas) == 1:
            schema = schemas[0]
            create_schema(c, schema)

            for version in versions:
                version_list.append(create_version(c, schema, version))

        elif len(schemas) == 0:
            pass
        else:
            raise Exception('Multiple schemas not supported for this test')

        resp = c.get(get_url)
        assert resp.status_code == expected_response['status_code']

        if not expected_response.get('use_collected_versions'):
            assert resp.data == expected_response['data']
        else:
            data = json.loads(resp.data)
            assert set(data) == set(version_list) #order not important

'''
GET /schemas/<name>/latest
'''
test_get_latest_schema_testparams = [
    # non existant schema returns 404
    ([], [], '/schemas/non_existant/latest', dict(status_code=404, data='Schema does not exist')),

    # item with single version returns that single version
    (['test'], ['new schema'], '/schemas/test/latest', dict(status_code=200,data='new schema')),

    # item with multiple versions returns newest version
    (['test'], ['new schema', 'new schema 2', 'new schema 3'],
                                '/schemas/test/latest', dict(status_code=200,data='new schema 3'))


]
@pytest.mark.usefixtures("emptydb")
@pytest.mark.parametrize("schemas,versions,get_url,expected_response", test_get_latest_schema_testparams)
def test_get_latest_schema_multi_version_schema(schemas,versions,get_url,expected_response):
    with app.test_client() as c:
        for schema in schemas:
            postresp = c.post('/schemas', data=dict(name=schema))
            assert postresp.status_code == 201

            schemaurl = '/schemas/{0}'.format(schema)
            for version in versions:
                verresp = c.post(schemaurl, data=version)
                assert verresp.status_code == 201

        resp = c.get(get_url)

        assert resp.status_code == expected_response['status_code']
        assert resp.data == expected_response['data']

test_get_non_existant_version_testparams = [
    ([],                [],           '/schemas/non_existant/1',    404),  # non existant schema, numeric version
    ([],                [],           '/schemas/non_existant/abc',  404),  # non existant schema, invalid version
    (['test'],          [],           '/schemas/test/1',            404),  # schema with no version
    (['test', 'test2'], [],           '/schemas/test/1',            404),  # multiple schemas with no version
    (['test'],          ['v1'],       '/schemas/test/2',            404),  # schema with version, ask for higher one
    (['test'],          ['v1', 'v2'], '/schemas/test/3',            404),  # schema with versions, ask for higher one
    (['test'],          ['v1'],       '/schemas/test/abc',          404),  # schema with version, invalid version
    (['test'],          ['v1', 'v2'], '/schemas/test/abc',          404),  # schema with versions, invalid version
]

@pytest.mark.usefixtures("emptydb")
@pytest.mark.parametrize("schemas,versions,get_url,response", test_get_non_existant_version_testparams)
def test_get_non_existant_version(schemas,versions,get_url, response):
    with app.test_client() as c:
        for schema in schemas:
            postresp = c.post('/schemas', data=dict(name=schema))
            assert postresp.status_code == 201

            schemaurl = '/schemas/{0}'.format(schema)
            for version in versions:
                verresp = c.post(schemaurl, data=version)
                assert verresp.status_code == 201


        resp = c.get(get_url)
        assert resp.status_code == response