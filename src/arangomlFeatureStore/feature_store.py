import logging

logger = logging.getLogger('arango_featurestore_logger')


class FeatureStore:

    def __init__(self, db, cfg):
        self.db = db
        self.cfg = cfg
        return

    def add_entity(self, doc):
        ENTITY_COLL = self.cfg['arangodb']['entity_col']
        entity_col = self.db.collection(ENTITY_COLL)
        metadata = entity_col.insert(doc)
        return metadata

    def add_entity_bulk(self, doc_list, batch_size=500, poverwrite=False):
        import json

        batch = []
        batch_idx = 1
        collection = self.db.collection(self.cfg['arangodb']['entity_col'])
        for index, doc in enumerate(doc_list):
            batch.append(doc)
            last_record = (index == (len(doc_list) - 1))
            if (index + 1) % batch_size == 0:
                logger.info("Batch insert of entities, inserting batch %d" % (batch_idx))
                batch_idx += 1
                collection.import_bulk(batch,  on_duplicate="update", overwrite=poverwrite)
                batch = []
            if last_record and (len(batch) > 0):
                logger.info("Batch insert of entities, inserting batch the last batch!")
                collection.import_bulk(batch, on_duplicate="update", overwrite=poverwrite)

    def add_value(self, doc):
        FEATURE_VAL_COLL = self.cfg['arangodb']['feature_value_col']
        feature_val_col = self.db.collection(FEATURE_VAL_COLL)
        metadata = feature_val_col.insert(doc)
        return metadata

    def add_value_bulk(self, doc_list, batch_size=500, poverwrite=False):
        import json
        batch = []
        batch_idx = 1
        collection = self.db.collection(self.cfg['arangodb']['feature_value_col'])
        for index, doc in enumerate(doc_list):
            batch.append(doc)
            last_record = (index == (len(doc_list) - 1))
            if (index + 1) % batch_size == 0:
                logger.info("Batch insert of values, inserting batch %d" % (batch_idx))
                batch_idx += 1
                collection.import_bulk(batch,  on_duplicate="update", overwrite=poverwrite)
                batch = []
            if last_record and (len(batch) > 0):
                #logger.info(f"Batch size: {len(batch)}")
                logger.info("Batch insert of values, inserting batch the last batch!")
                collection.import_bulk(batch, on_duplicate="update", overwrite=poverwrite)


    def link_entity_feature_value_bulk(self, doc_list, batch_size=500, poverwrite=False):
        import json
        FEATURE_VAL_COLL = self.cfg['arangodb']['feature_value_col']
        ENTITY_COLL = self.cfg['arangodb']['entity_col']
        batch = []
        batch_idx = 1
        collection = self.db.collection(self.cfg['arangodb']['edge_col'])
        for index, doc in enumerate(doc_list):
            from_id = ENTITY_COLL + '/' + doc['_from']
            to_id = FEATURE_VAL_COLL + '/' + doc['_to']
            edge_key = doc['_from'] + '-' + doc['_to']
            doc['_key'] = edge_key
            doc['_from'] = from_id
            doc['_to'] = to_id
            # insert_doc2 = {"_from": e[1], "_to": e[0]}
            batch.append(doc)
            last_record = (index == (len(doc_list) - 1))
            if (index + 1) % batch_size == 0:
                logger.info("Batch insert of links, inserting batch %d" % (batch_idx))
                batch_idx += 1
                collection.import_bulk(batch,  on_duplicate="update", overwrite=poverwrite)
                batch = []
            if last_record and (len(batch) > 0):
                logger.info("Batch insert of links, inserting batch the last batch!")
                collection.import_bulk(batch, on_duplicate="update", overwrite=poverwrite)

    def link_entity_feature_value(self, doc):
        FEATURE_VAL_COLL = self.cfg['arangodb']['feature_value_col']
        ENTITY_COLL = self.cfg['arangodb']['entity_col']
        from_id = ENTITY_COLL + '/' + doc['_from']
        to_id = FEATURE_VAL_COLL + '/' + doc['_to']
        edge_key = doc['_from'] + '-' + doc['_to']
        doc['_key'] = edge_key
        doc['_from'] = from_id
        doc['_to'] = to_id
        logger.info("Edge Key: " + str(doc))
        ec = self.db.collection(self.cfg['arangodb']['edge_col'])
        metadata = ec.insert(doc, overwrite=True)
        return metadata

    def find_entity(self, attrib_name, attrib_value):
        "Return the feature values that match the criteria provided in filter"
        ENTITY_COLL = self.cfg['arangodb']['entity_col']
        aql = 'FOR doc IN %s FILTER doc.%s == @value RETURN doc' % (
            ENTITY_COLL, attrib_name)
        cursor = self.db.aql.execute(aql, bind_vars={'value': attrib_value})
        assets = [doc for doc in cursor]

        if len(assets) == 0:
            msg = "Asset %s with %s = %s was not found!" % (
                ENTITY_COLL, attrib_name, attrib_value)
            logger.info(msg)

        return assets

    def tag_featureset_by_criteria(self, filter_attrib_name, attrib_value, tag_name, tag_value):
        EDGE_COLL = self.cfg['arangodb']['edge_col']
        aql = f'FOR doc IN `{EDGE_COLL}` FILTER doc.`{filter_attrib_name}` == \"{attrib_value}\"  UPDATE doc WITH {{ {tag_name} : \"{tag_value}\" }} IN `{EDGE_COLL}`'

        logger.info("AQL:" + str(aql))
        cursor = self.db.aql.execute(aql)
        assets = [doc for doc in cursor]

        if len(assets) == 0:
            msg = "No records to update in %s with %s = %s !" % (EDGE_COLL, filter_attrib_name, attrib_value)
            logger.info(msg)
        else:
            msg = "%d records updated in %s " % (len(assets), EDGE_COLL)
            logger.info(msg)

        return

    def get_featureset_with_tag(self, tag_name, tag_value):
        EDGE_COLL = self.cfg['arangodb']['edge_col']
        FEATURE_VAL_COLL = self.cfg['arangodb']['feature_value_col']
        aql = f"FOR doc IN `{EDGE_COLL}`  FILTER doc.`{tag_name}` == \"{tag_value}\" FOR fv in `{FEATURE_VAL_COLL}` FILTER fv._id == doc._to RETURN fv "

        logger.info("AQL:" + str(aql))
        cursor = self.db.aql.execute(aql)
        assets = [doc for doc in cursor]

        if len(assets) == 0:
            msg = "No records were found with feature tag"
            logger.info(msg)
        else:
            msg = "%d records returned with feature set tag specified." % (len(assets))
            logger.info(msg)

        return assets

    def update_entity(self, entity_key, new_feature_values):
        "Criteria must match a single entity"
        return

    def bulk_update(self, idlist, new_feature_value_list):
        "Update each id in the idlist with the corresponding entry in the new_feature_values list"
        return
