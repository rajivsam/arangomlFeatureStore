# ArangoML FeatureStore

This is a simple package that provides machine learning applications the following capabilities:

1. Write machine learning features to an ArangoDB feature store
2. Read machine learning features from an ArangoDB feature store


# Build Package
Execute the following from the directory containing the `setup.py` 

1. `python3 setup.py sdist bdist_wheel`

2. `python3 -m twine upload --repository testpypi dist/*` and then provide the user name and password to upload package to testpypi


