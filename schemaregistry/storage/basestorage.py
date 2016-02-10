
class BaseStorage(object):
    def get_schema_version(self, name, version):
        pass

    def get_schema_by_id(self, id):
        pass

    def get_schemas(self):
        pass

    def get_schema_versions(self, name):
        pass

    def get_latest_schema(self, name):
        pass

    def create_schema(self, name):
        pass

    def schema_exists(self, name):
        pass

    def create_schema_version(self, name, schema):
        pass