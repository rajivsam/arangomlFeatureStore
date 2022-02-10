
import logging
from . import oasis
import os
import yaml
import time
from arangomlFeatureStore.feature_store import FeatureStore
from arangomlFeatureStore.managed_service_conn_parameters import ManagedServiceConnParam
from arango import ArangoClient
# create logger with 'spam_application'
logger = logging.getLogger('arango_featurestore_logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('../arango_featurestore_logger.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
mscp = ManagedServiceConnParam()

class FeatureStoreAdmin():

    def __init__(self, conn_config=None):
        if conn_config is not None:
            logger.info("Connection information specified: " + str(conn_config))
            self.db_name = conn_config[mscp.DB_NAME]
            self.username  = conn_config[mscp.DB_USER_NAME]
            self.hostname = conn_config[mscp.OASIS_HOST]
            self.protocol = conn_config[mscp.OASIS_CONN_PROTOCOL]
            self.password = conn_config[mscp.DB_PASSWORD]
            self.port = conn_config[mscp.OASIS_PORT]
            self.db = self.connect_to_db()
            heart_beat_check = self.heartbeat(conn_config[mscp.OASIS_FS_GRAPH])
            if not heart_beat_check:
                logger.info("The connection information you specified is not valid, check and try again.")
                return
            self.feature_graph = self.db.graph(conn_config[mscp.OASIS_FS_GRAPH])
            self.cfg = self.write_connection_info()

        else:
            self.cfg = self.read_data()
            logger.info("CFG:" + str(self.cfg))
            if self.connection_info_in_config():
                self.hostname = self.cfg['arangodb'][mscp.OASIS_HOST]
                self.protocol = self.cfg['arangodb'][mscp.OASIS_CONN_PROTOCOL]
                self.port = self.cfg['arangodb'][mscp.OASIS_PORT]
                self.username = self.cfg['arangodb'][mscp.DB_USER_NAME]
                self.password = self.cfg['arangodb'][mscp.DB_PASSWORD]
                self.db_name = self.cfg['arangodb'][mscp.DB_NAME]
                logger.info("Using connection information in config file: " + str(self.cfg))
                self.db = self.connect_to_db()
                heart_beat_check = self.heartbeat(self.cfg['arangodb'][mscp.OASIS_FS_GRAPH])
                if not heart_beat_check:
                    logger.info("The connection information is stale, getting a new connection.")
                    self.db = self.get_new_oasis_db()
                    logger.info("Provisioning Graph...")
                    self.feature_graph = self.create_feature_store_db()
                    self.cfg = self.write_connection_info()
            else:
                con = oasis.getTempCredentials()
                logger.info("No connection information in config file, got credentials from Oasis" + str(con))
                self.hostname = con[mscp.OASIS_HOST]
                self.protocol = "https"
                self.port = con[mscp.OASIS_PORT]
                self.username = con[mscp.DB_USER_NAME]
                self.password = con[mscp.DB_PASSWORD]
                self.db_name = con[mscp.DB_NAME]
                self.db = self.get_new_oasis_db()
                logger.info("Connected to DB, writing connection information to disk for next session!")
                logger.info("Provisioning Graph...")
                self.feature_graph = self.create_feature_store_db()
                self.cfg = self.write_connection_info()



        return

    def connect_to_db(self):
        url = self.protocol + "://" + self.hostname + ":" + str(self.port)
        client = ArangoClient(hosts=url)
        db = client.db(self.db_name, username=self.username, password=self.password)
        return db

    def heartbeat(self, graph_name):
        try:
            heart_beat_check = self.db.has_graph(graph_name)
        except :
            heart_beat_check = False
            logger.info("Heart beat check failed, get a new db")
        return heart_beat_check


    def write_connection_info(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 "config/arango_feature_store_config.yaml")
        with open(file_name, "r") as file_descriptor:
            cfg = yaml.load(file_descriptor, Loader=yaml.FullLoader)
        logger.info("config file before write:" + str(cfg))
        cfg['arangodb'][mscp.DB_NAME] = self.db_name
        cfg['arangodb'][mscp.DB_USER_NAME] = self.username
        cfg['arangodb'][mscp.DB_PASSWORD] = self.password
        cfg['arangodb'][mscp.OASIS_HOST] = self.hostname
        cfg['arangodb'][mscp.OASIS_CONN_PROTOCOL] = self.protocol
        cfg['arangodb'][mscp.OASIS_PORT] = self.port

        with open(file_name, "w") as file_descriptor:
            wcfg = yaml.dump(cfg, file_descriptor)
            logger.info("Config file after write: " + str(cfg))

        return cfg

    def read_data(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 "config/arango_feature_store_config.yaml")
        with open(file_name, "r") as file_descriptor:
            cfg = yaml.load(file_descriptor, Loader=yaml.FullLoader)

        return cfg

    def connection_info_in_config(self):
        connection_info_list = [mscp.OASIS_HOST, mscp.OASIS_CONN_PROTOCOL, mscp.OASIS_PORT, mscp.DB_USER_NAME, mscp.DB_PASSWORD, mscp.DB_NAME]
        info_specified = []
        for cs in connection_info_list:
            info_specified.append(cs in self.cfg['arangodb'])
        return all(info_specified)



    def delete_entity(self, criteria):
        return

    def get_feature_store(self, user = {'username':'username', 'password':'password'}):
        return FeatureStore(self.db, self.cfg)


    def create_feature_store_db(self):
        # The names of the graph are string literals now, can be made configurable in a subsequent iteration
        GRAPH_NAME = self.cfg['arangodb']['graph_name']
        if not self.db.has_graph(GRAPH_NAME):
            self.db.create_graph(GRAPH_NAME)
            txt = "{gname} is not provisioned in the database, creating it! ".format(gname=GRAPH_NAME)
            logger.info(txt)
        ENTITY_COLL = self.cfg['arangodb']['entity_col']
        REPLICATION_FACTOR = int(self.cfg['arangodb']['replication_factor'])
        if not self.db.has_collection(ENTITY_COLL):
            self.db.create_collection(ENTITY_COLL, REPLICATION_FACTOR)
            txt = "{colname} is not a provisioned collection, creating it! ".format(colname=ENTITY_COLL)
            logger.info(txt)
        FEATURE_VALUE_COLL= self.cfg['arangodb']['feature_value_col']
        if not self.db.has_collection(FEATURE_VALUE_COLL):
            self.db.create_collection(FEATURE_VALUE_COLL, REPLICATION_FACTOR)
            txt = "{colname} is not a provisioned collection, creating it! ".format(colname=FEATURE_VALUE_COLL)
            logger.info(txt)
        feature_store_graph = self.db.graph(GRAPH_NAME)
        EDGE_COLL = self.cfg['arangodb']['edge_col']
        if not self.db.has_collection(EDGE_COLL):
            self.db.create_collection(EDGE_COLL, REPLICATION_FACTOR, edge=True)
            txt = "{ename} is not provisioned in the database, creating it! ".format(ename=EDGE_COLL)
            logger.info(txt)
        if not feature_store_graph.has_edge_definition(EDGE_COLL):
            entity_feature_value = feature_store_graph.create_edge_definition(
                edge_collection=EDGE_COLL,
                from_vertex_collections=[ENTITY_COLL],
                to_vertex_collections=[FEATURE_VALUE_COLL]
            )
            txt = "{ename} edge definition is not provisioned in the database, creating it! ".format(ename=EDGE_COLL)
            logger.info(txt)


        return feature_store_graph


    def get_new_oasis_db(self):
        url = self.protocol + "://" + self.hostname + ":" + str(self.port)
        client = ArangoClient(hosts=url)
        try:
            con = oasis.getTempCredentials()
            db = client.db(con[mscp.DB_NAME], username=con[mscp.DB_USER_NAME], password=con[mscp.DB_PASSWORD])
            logger.info("Got new Oasis Connection, connection information: " + str(con))
            self.hostname = con[mscp.OASIS_HOST]
            self.port = con[mscp.OASIS_PORT]
            self.db_name = con[mscp.DB_NAME]
            self.password = con[mscp.DB_PASSWORD]
        except :
            logger.info("Could not use the old connection information, requesting a new Oasis Connection...")
            time.sleep(1)

        #logging.info("Oasis DB is " + str(db))
        return db



