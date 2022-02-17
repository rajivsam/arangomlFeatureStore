# ArangoML FeatureStore

This is a simple package that provides machine learning applications the following capabilities:

1. Write machine learning features to an ArangoDB feature store
2. Read machine learning features from an ArangoDB feature store


# Illustrative Examples
Please see the examples folder for a set of notebooks that illustrate the utility of `arangomlFeatureStore` in the enterprise. The ideas illustrated in the examples are as follows:

1. `arangomlFeatureStoreDemo.ipynb`: This notebook provides an overview of the functionality of the API. The intent is to communicate the API provided and the functionality fulfilled by each API.

2. `feature_store_producer_DS.ipynb`: This notebook provides an overview of how an application that generates embeddings, such as a notebook produced by a data scientist, can invoke the feature store API to store the embeddings it generates.

3. `feature_store_consumer_application.ipynb`: This notebook provides an overview of how an application, such as an application that makes recommendations, can invoke the feature store API to provide recommendations.


4. `feature_store_consumer_data_analyst.ipynb`: This notebook provides an overview of how a data analyst can use the feature store API to investigate consumer preferences or perform an ad-hoc analysis using similarity search.




# Build Package
Execute the following from the directory containing the `setup.py` 

1. `python3 setup.py sdist bdist_wheel`

2. `python3 -m twine upload --repository testpypi dist/*` and then provide the user name and password to upload package to testpypi


