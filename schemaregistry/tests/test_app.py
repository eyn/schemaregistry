"""
    tests.app
    ~~~~~~~~~~~~~~~~~~~

    Tests the Memory Storage container.

    :copyright: (c) 2016 by James Moore.
    :license: BSD, see LICENSE for more details.
"""
import json

from app import app

def test_get_schemas_is_empty_at_startup(tmpdir_factory):
    app.config['ROCKSDB_DATAFILE']  = str(tmpdir_factory.mktemp('schemaregistry', numbered=True))
    with app.test_client() as c:
        resp = c.get('/schemas')
        data = json.loads(resp.data)
        assert data == {}
