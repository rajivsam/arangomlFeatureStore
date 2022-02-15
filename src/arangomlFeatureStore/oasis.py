import json
import requests
import sys
import time
import logging
logger = logging.getLogger('arango_featurestore_logger')
from pyArango.connection import Connection
from arango import ArangoClient


# retrieving credentials from ArangoDB tutorial service
def getTempCredentials(
    tutorialName=None,
    credentialProvider="https://tutorials.arangodb.cloud:8529/_db/_system/tutorialDB/tutorialDB",
):
    body = {"tutorialName": tutorialName} if tutorialName else "{}"
    x = requests.post(credentialProvider, data=json.dumps(body))
    if x.status_code != 200:
        print("Error retrieving login data.")
        sys.exit()
    time.sleep(5)
    logger.info("New credentials obtained from Oasis.")
    return json.loads(x.text)


# Connect against an oasis DB and return pyarango connection
def connect(login: dict):
    url = "https://" + login["hostname"] + ":" + str(login["port"])
    return Connection(
        arangoURL=url, username=login["username"], password=login["password"]
    )


# Connect against an oasis DB and return python-arango connection
def connect_python_arango(login: dict):
    url = "https://" + login["hostname"] + ":" + str(login["port"])
    logger.info("Python-arango Connection made to: " + str(url))
    return ArangoClient(hosts=url).db(
        login["dbName"],
        username=login["username"],
        password=login["password"],
        verify=True,
    )
