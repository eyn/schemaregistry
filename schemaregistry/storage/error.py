"""
    error.py
    ~~~~~~~~

    This module contains errors to be thrown by storage modules

    :copyright: (c) by 2016 James Moore
    :license: BSD, see LICENSE for more details
"""

class SchemaExistsError(Exception):
    """
    Thrown when a schema already exists
    """
    pass

class SchemaDoesNotExistError(Exception):
    """
    Thrown when a schema does not exist
    """
    pass

class SchemaHasNoVersionsError(Exception):
    """
    Thrown when a schema does not have any versions
    """
    pass

class SchemaVersionDoesNotExistError(Exception):
    """
    Thrown when a schema version does not exist
    """
    pass