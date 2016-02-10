from flask import Flask, request
from flask.json import jsonify
import storage
"""
    schema-registry.app
    ~~~~~~~~~~~~~~~~~~~

    This module implements the main Flask application

    :copyright: (c) by 2016 James Moore
    :license: BSD, see LICENSE for more details
"""
app = Flask(__name__)

datastore = storage.Memory()


@app.route('/schemas/<name>/<version>', methods=['GET'])
def get_schema_version(name, version):
    """
    Gets schema by name and version.

    If schema doesn't exist returns 404
    If schema exists returns 200 and schema is returned as body

    :param name: The name of the schema to search for
    :param version: The version of the schema to return
    """
    schema = datastore.get_schema_version(name, version)

    if schema is None:
        return None, 404

    return schema, 200

@app.route('/schemas', methods=['GET'])
def get_schemas():
    """
    If id set in query string then search for just that schema otherwise return all schemas

    :return: a list of registered schema names and associated ids
    """
    id = request.args.get('id')

    if id is not None:
        schemas = datastore.get_schema_by_id(id)
    else:
        schemas = datastore.get_schemas()

    return jsonify(schemas), 200

@app.route('/schemas/<name>', methods=['GET'])
def get_schema_versions(name):
    """
    :param name: the name of the schema to search for
    :return: the list of versions of the schema available
    """
    schema_versions = datastore.get_schema_versions(name)

    if schema_versions is None:
        return None, 404

    return jsonify(schema_versions), 200

@app.route('/schemas/<name>/latest', methods=['GET'])
def get_lastest_schema(name):
    """
    :param name: The name of the schema to search for
    :return: The latest version of that schema
    """
    schema = datastore.get_latest_schema(name)

    if schema is None:
        return None, 404

    return schema, 200

@app.route('/schemas/', methods=['POST'])
def create_schema():
    """
    Creates a schema from a post request
    :return: 409 if schema already exists. 201 if schema is created with schema id in return value
    """
    name = request.form['name']
    if name is None:
        return 'name not provided', 400

    try:
        schema = datastore.create_schema(name)
    except storage.SchemaAlreadyExisitsError:
        return 'Already exisits', 409

    return jsonify(schema), 201

@app.route('/schemas/<name>', methods=['POST'])
def create_schema_version(name):
    """
    Creates a schema version from a post request
    :return: 404 if schema does not exist. 201 if schema is created with schema version in return value
    """
    schema = request.data

    if not datastore.schema_exists(name):
        return None, 404

    version = datastore.create_schema_version(name, schema)
    return jsonify(version), 201



if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0')
