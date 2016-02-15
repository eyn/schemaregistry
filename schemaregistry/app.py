"""
    schema-registry.app
    ~~~~~~~~~~~~~~~~~~~

    This module implements the main Flask application

    :copyright: (c) by 2016 James Moore
    :license: BSD, see LICENSE for more details
"""

from flask import Flask, request, make_response
from flask.json import jsonify, dumps
import storage.rocksdb
import storage.error

app = Flask(__name__)
_datastore = None

def reinit_db():
    global _datastore
    _datastore = None

def get_datastore():
    global _datastore
    if _datastore is None:
        datapath = app.config.get('ROCKSDB_DATAFILE')
        if datapath is None:
            raise Exception('ROCKS_DATAFILE not set')

        _datastore = storage.rocksdb.RocksDB(datapath)

    return _datastore

@app.route('/schemas', methods=['GET'])
def get_schemas():
    """
    If id set in query string then search for just that schema otherwise return all schemas

    :return: a list of registered schema names and associated ids
    """
    id = request.args.get('id')

    if id is not None:
        schemas = get_datastore().get_schemas(ids=[id])
    else:
        schemas = get_datastore().get_schemas()

    retval = make_response((dumps(schemas), 200, dict(mimetype='application/json')))
    return retval

@app.route('/schemas/<name>', methods=['GET'])
def get_schema_versions(name):
    """
    :param name: the name of the schema to search for
    :return: the list of versions of the schema available
    """
    try:
        schema_versions = get_datastore().get_schema_versions(name)
    except storage.error.SchemaDoesNotExistError:
        return 'Schema does not exist', 404

    retval = make_response((dumps(schema_versions), 200, dict(mimetype='application/json')))
    return retval

@app.route('/schemas/<name>/latest', methods=['GET'])
def get_lastest_schema(name):
    """
    :param name: The name of the schema to search for
    :return: The latest version of that schema
    """
    try:
        schema = get_datastore().get_latest_schema(name)
    except storage.error.SchemaDoesNotExistError:
        return 'Schema does not exist', 404

    return schema, 200

@app.route('/schemas/<name>/<version>', methods=['GET'])
def get_schema_version(name, version):
    """
    Gets schema by name and version.

    If schema doesn't exist returns 404
    If schema exists returns 200 and schema is returned as body

    :param name: The name of the schema to search for
    :param version: The version of the schema to return
    """
    try:
        schema = get_datastore().get_schema_version(name, version)
    except storage.error.SchemaDoesNotExistError:
        return 'Schema does not exist', 404
    except storage.error.SchemaVersionDoesNotExistError:
        return 'Version does not exist', 404

    return schema, 200


@app.route('/schemas', methods=['POST'])
def create_schema():
    """
    Creates a schema from a post request
    :return: 409 if schema already exists. 201 if schema is created with schema id in return value
    """
    name = request.form['name']
    if name is None:
        return 'name not provided', 400

    try:
        schema = get_datastore().create_schema(name)
    except storage.error.SchemaExistsError:
        return 'Already exisits', 409

    return jsonify({'id': schema}), 201

@app.route('/schemas/<name>', methods=['POST'])
def create_schema_version(name):
    """
    Creates a schema version from a post request
    :return: 404 if schema does not exist. 201 if schema is created with schema version in return value
    """
    schema = request.data

    if not get_datastore().schema_exists(name):
        return 'Schema does not exist', 404

    version = get_datastore().create_schema_version(name, schema)
    return jsonify({'version': version}), 201

if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0')
