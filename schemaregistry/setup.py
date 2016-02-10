from setuptools import setup, find_packages
setup(
    name = "SchemaRegistry",
    version = "0.1",
    packages = find_packages(exclude=["tests"]),
    scripts = ['app.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    # install_requires = ['docutils>=0.3'],


    # metadata for upload to PyPI
    author = "James Moore",
    author_email = "james.moore@cantab.net",
    description = "Schema Registry package",
    license = "BSD",
    keywords = "",
    url = "",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)