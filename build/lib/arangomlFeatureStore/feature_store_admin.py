
import logging
from . import oasis
import os
import yaml
from arangomlFeatureStore.feature_store import FeatureStore
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

class FeatureStoreAdmin():

    def __init__(self):
        self.db = self.get_oasis_db()
        self.cfg = self.read_data()
        self.feature_graph = self.create_feature_store_db()


        return

    def read_data(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 "config/arango_feature_store_config.yaml")
        with open(file_name, "r") as file_descriptor:
            cfg = yaml.load(file_descriptor, Loader=yaml.FullLoader)
        return cfg



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

    def get_oasis_db(self):
        con = oasis.getTempCredentials()
        db = oasis.connect_python_arango(con)
        logger.info("Connection information: " + str(con))
        #logging.info("Oasis DB is " + str(db))
        return db



