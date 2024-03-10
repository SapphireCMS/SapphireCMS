import bson
from pymongo.mongo_client import MongoClient

class MongoDB:
    def __init__(self, uri, database, factories):
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self.models = {k: v(self) for k,v in factories.items()}
        for _, item in factories.items():
            v = item(self)
            k = v.__name__
            setattr(self, k, v)

    def commit(self):
        pass

    def save(self, object):
        _obj = object.to_dict()
        if '_id' in _obj.keys():
            if type(_obj['_id']) != bson.ObjectId:
                _obj['_id'] = bson.ObjectId(_obj['_id'])
        else:
            _obj['_id'] = bson.ObjectId()
        original = self.db[object.__dataset_name__].find_one({"_id": _obj['_id']})
        for key, value in _obj.items():
            if key == '_id':
                pass
            if key in object.__relationships__.keys():
                if value is None:
                    continue
                relation = object.__relationships__[key]
                if relation[1].split('-')[0] == 'many' and relation[1].split('-')[2] == 'many':
                    relatives = []
                    for item in value:
                        if self.exists(item):
                            self.db[relation[0]].update_one({"_id": bson.ObjectId(item._id)}, {"$push": {relation[2]: bson.DBRef(object.__dataset_name__, _obj['_id'])}})
                        else:
                            if bson.DBRef(object.__dataset_name__, _obj['_id']) not in getattr(item, relation[2]):
                                getattr(item, relation[2]).append(bson.DBRef(object.__dataset_name__, _obj['_id']))
                            item.save()
                        if bson.DBRef(relation[0], bson.ObjectId(item._id)) not in getattr(object, relation[2]):
                            getattr(item, relation[2]).append(bson.DBRef(relation[0], bson.ObjectId(item._id)))
                            item.save()
                        relatives.append(bson.DBRef(relation[0], bson.ObjectId(item._id)))
                    _obj[key] = relatives
                elif relation[1].split('-')[0] == 'one' and relation[1].split('-')[2] == 'one':
                    if self.exists(value):
                        self.db[relation[0]].update_one({"_id": bson.ObjectId(_obj['_id'])}, {"$set": {relation[2]: bson.DBRef(object.__dataset_name__, _obj['_id'])}})
                    else:
                        _obj[key].save()
                    _obj[key] = bson.DBRef(relation[0], bson.ObjectId(_obj[key]._id))
                elif relation[1].split('-')[0] == 'many' and relation[1].split('-')[2] == 'one':
                    if self.exists(value):
                        # Add reference to the list of references in the related object
                        self.db[relation[0]].update_one({"_id": bson.ObjectId(value._id)}, {"$push": {relation[2]: bson.DBRef(object.__dataset_name__, _obj['_id'])}})
                    else:
                        value.save()
                    _obj[key] = bson.DBRef(relation[0], bson.ObjectId(value._id))
                elif relation[1].split('-')[0] == 'one' and relation[1].split('-')[2] == 'many':
                    relatives = []
                    for item in value:
                        if type(item) == bson.DBRef:
                            item = self.resolve_relation(item)
                        if self.exists(item):
                            self.db[relation[0]].update_one({"_id": bson.ObjectId(item._id)}, {"$set": {relation[2]: bson.DBRef(object.__dataset_name__, object._id)}})
                        else:
                            setattr(item, relation[2], bson.DBRef(object.__dataset_name__, object._id))
                            item.save()
                        relatives.append(bson.DBRef(relation[0], bson.ObjectId(item._id)))
                    _obj[key] = relatives
        if self.exists(object):
            self.db[object.__dataset_name__].update_one({"_id": _obj['_id']}, {"$set": _obj})
            return self.get(object.__class__, bson.ObjectId(_obj['_id']))
        else:
            return self.get(object.__class__, bson.ObjectId(self.db[object.__dataset_name__].insert_one(_obj).inserted_id))
                
    def delete(self, object):
        self.db[object.__dataset_name__].delete_one({"_id": object._id})
        
    def all(self, model):
        return [model(**item) for item in self.db[model.__dataset_name__].find()]
    
    def get(self, model, _id):
        obj = self.db[model.__dataset_name__].find_one({"_id": _id})
        if obj is not None:
            return model.from_dict(obj)
        return None
    
    def resolve_relation(self, obj):
        if type(obj) == bson.DBRef:
            _obj = self.db[obj.collection].find_one({"_id": obj.id})
            if obj is not None:
                return self.models[obj.collection].from_dict(_obj)
            return None
        elif type(obj) == list and len(obj) > 0 and type(obj[0]) == bson.DBRef:
            return [self.resolve_relation(item) for item in obj]
        elif type(obj) == list and len(obj) == 0:
            return []
    
    def exists(self, object):
        return getattr(object, '_id', None) is not None and self.get(object.__class__, object._id) is not None
    
    def count(self, model):
        return self.db[model.__dataset_name__].count_documents({})
    
    def filter(self, model, **kwargs):
        filter = {}
        if 'sort_key' and 'sort_order' in kwargs:
            sort_key = kwargs.pop('sort_key')
            sort_order = kwargs.pop('sort_order')
            filter['sort'] = [(sort_key, sort_order)]
        for key, value in kwargs.items():
            filter[key] = value
        return [model(**item) for item in self.db[model.__dataset_name__].find(kwargs)]
    
    def collection_exists(self, model):
        return model.__dataset_name__ in self.db.list_collection_names()
    
    def close(self):
        self.client.close()