from schemaregistry.storage.memory import Memory

def pytest_generate_tests(metafunc):
    if 'storageengine' in metafunc.fixturenames:
        metafunc.parametrize("storageengine", [Memory()])