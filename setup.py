import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arangomlFeatureStore",
    version="0.0.7.8",
    author="Rajiv Sambasivan",
    author_email="rajiv@arangodb.com",
    description="A python package to read and write ML features to ArangoDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rajivsam/arangomlFeatureStore",
    project_urls={
        "Bug Tracker": "https://github.com/rajivsam/arangomlFeatureStore",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"arangomlFeatureStore": "src/arangomlFeatureStore"},
    packages=setuptools.find_packages(where="src", include=['arangomlFeatureStore']),
    package_data={'config': ['config/arango_feature_store_config.yaml']},
    include_package_data=True,
    python_requires=">=3.6",
)