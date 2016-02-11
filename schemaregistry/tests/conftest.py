from schemaregistry.storage.memory import Memory
from schemaregistry.storage.rocksdb import RocksDB
import pytest

def pytest_generate_tests(metafunc):
    if 'storageengine' in metafunc.fixturenames:
        metafunc.parametrize("storageengine", ['memory', 'rocksdb'], indirect=True)


@pytest.fixture
def storageengine(request, tmpdir_factory):
    if request.param == 'memory':
        return Memory()
    elif request.param == 'rocksdb':
        return RocksDB(str(tmpdir_factory.mktemp('schemaregistry', numbered=True)))
