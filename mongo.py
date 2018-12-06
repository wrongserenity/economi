from pymongo import MongoClient


# TODO: write try:.. except.. wrappers
class MongoConnection(object):
    def __init__(self, db_name, col_name, **mongo_configs):
        self.client = MongoClient(**mongo_configs)
        self.db = self.client[db_name]
        self.collection = self.db[col_name]
    
    def get_unit(self, unit_id):
        return self.collection.find_one({"unit_id": unit_id})
    
    def set_unit(self, unit_obj):
        self.collection.insert_one(unit_obj.to_dict())
    
    def count_units(self, owner_id):
        return self.collection.count_documents({"owner_id": owner_id})
    
    def update_unit(self, unit_id, updates):
        self.collection.update_one({"unit_id": unit_id}, {"$set": updates})
        
    def close_connection(self):
        self.client.close()

    def get_units(self, uid):
        return self.collection.find({"owner_id": uid})

        
