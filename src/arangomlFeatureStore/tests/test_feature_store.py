import pytest
import logging
import uuid
logger = logging.getLogger('arango_featurestore_logger')



from arangomlFeatureStore.feature_store_admin import FeatureStoreAdmin
from arango.database import StandardDatabase

@pytest.fixture
def conn_params():
    fa = FeatureStoreAdmin()
    db = fa.db
    return {'db':db, 'feature_store_admin': fa, 'config':fa.cfg}

def test_db_creation(conn_params):
    db = conn_params['db']
    db_type_match = isinstance(db, StandardDatabase)
    #err_msg = "Database Creation in Oasis failed!"
    assert db_type_match == True

def test_add_entity(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    test_entity = {'_key': 'test_entity', 'attribute': 'some value'}
    metadata = fs.add_entity(test_entity)
    cfg = conn_params['config']
    ENTITY_COLL = cfg['arangodb']['entity_col']
    assert metadata['_id'] == ENTITY_COLL + '/' + 'test_entity'
    assert metadata['_key'] == 'test_entity'

def test_add_value(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    test_value = {'_key': 'test_value', 'attribute': [0.1234, 0.1234, 0.1234]}
    metadata = fs.add_value(test_value)
    cfg = conn_params['config']
    FEATURE_VAL_COLL = cfg['arangodb']['feature_value_col']
    assert metadata['_id'] == FEATURE_VAL_COLL + '/' + 'test_value'
    assert metadata['_key'] == 'test_value'

def test_link_entity_feature_value(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    cfg = conn_params['config']
    test_value = {'_key': 'test_value' + str(uuid.uuid4()), 'attribute': [0.1234, 0.1234, 0.1234], 'tag': 'featureset-1'}
    value_info = fs.add_value(test_value)
    test_entity = {'_key': 'test_entity' + str(uuid.uuid4()), 'attribute': 'some value'}
    edge_info = fs.add_entity(test_entity)
    #edge_key = edge_info['_key'] + '-' + value_info['_key']
    edoc = {'_from': edge_info['_key'],'_to': value_info['_key'], 'tag': 'model-xyz'}
    metadata = fs.link_entity_feature_value(edoc)
    EDGE_COLL = cfg['arangodb']['edge_col']
    edge_id = EDGE_COLL + '/' + edge_info['_key'] + '-' + value_info['_key']
    assert metadata['_id'] == edge_id



def test_find_entity(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    test_entity = {'_key': 'test_find_entity', 'attribute': 'some value'}
    metadata = fs.add_entity(test_entity)
    cfg = conn_params['config']
    ENTITY_COLL = cfg['arangodb']['entity_col']
    emd = fs.find_entity(attrib_name='_key', attrib_value='test_find_entity')
    logger.info("Found entity: " + str(emd))
    assert (True == True)

def create_edges(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    cfg = conn_params['config']

    EDGE_COLL = cfg['arangodb']['edge_col']
    test_value_1 = {'_key': 'test_value' + str(uuid.uuid4()), 'attribute': [0.1234, 0.1234, 0.1234], 'tag': 'featureset-test'}
    value_info = fs.add_value(test_value_1)
    test_entity_1 = {'_key': 'test_entity' + str(uuid.uuid4()), 'attribute': 'some value'}
    edge_info = fs.add_entity(test_entity_1)
    edoc = {'_from': edge_info['_key'], '_to': value_info['_key'], 'created-by': 'model-xyz'}
    metadata = fs.link_entity_feature_value(edoc)
    edge_id = EDGE_COLL + '/' + edge_info['_key'] + '-' + value_info['_key']

    test_value_2 = {'_key': 'test_value' + str(uuid.uuid4()), 'attribute': [0.1234, 0.1234, 0.1234], 'tag': 'featureset-test'}
    value_info = fs.add_value(test_value_2)
    test_entity_2 = {'_key': 'test_entity' + str(uuid.uuid4()), 'attribute': 'some value'}
    edge_info = fs.add_entity(test_entity_2)
    edoc = {'_from': edge_info['_key'], '_to': value_info['_key'], 'created-by': 'model-xyz'}
    metadata = fs.link_entity_feature_value(edoc)


def test_tag_featureset_by_criteria(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    cfg = conn_params['config']
    logger.info("Adding two test entities and values...")
    create_edges(conn_params)
    logger.info("Updating added entities...")
    fs.tag_featureset_by_criteria('created-by', 'model-xyz', 'tag', 'modelABC')
    logger.info("Done!")

def test_get_featureset_by_tag(conn_params):
    fa = conn_params['feature_store_admin']
    fs = fa.get_feature_store()
    cfg = conn_params['config']
    logger.info("Adding two test entities and values...")
    create_edges(conn_params)
    logger.info("Updating added entities...")
    fs.tag_featureset_by_criteria('created-by', 'model-xyz', 'tag', 'modelABC')
    logger.info("Getting featureset with tag modelABC")
    res = fs.get_featureset_with_tag('tag', 'modelABC')
    logger.info("Results: " + str(res))







