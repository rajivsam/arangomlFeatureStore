import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arangomlFeatureStore-rajivsam",
    version="0.0.1",
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
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)