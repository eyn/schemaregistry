from schemaregistry.storage.memory import Memory
from schemaregistry.storage.rocksdb import RocksDB

def pytest_generate_tests(metafunc):
    if 'storageengine' in metafunc.fixturenames:
        metafunc.parametrize("storageengine", [Memory(), RocksDB()])