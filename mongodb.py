from pymongo import MongoClient
from bson.objectid import ObjectId
import os


class MongoDatabase:

    def __init__(self, dbname, collection):
        self.dbname = dbname
        self.collection = collection
        self.connection_str = 'mongodb://%s:%s@%s:27017/' %\
                              (os.environ.get("MONGO_INITDB_ROOT_USERNAME", "root"),
                               os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "example"),
                               os.environ.get("MONGO_HOST", "localhost"))

    @staticmethod
    def _specific_record_exist(collection, **kwargs):
        record = collection.find_one(kwargs)
        if record and len(list(record)) > 0:
            return record['_id']
        return None

    def insert_record(self, **kwargs):
        with MongoClient(self.connection_str) as client:
            db = client.get_database(self.dbname)
            contacts = db.get_collection(self.collection)
            try:
                existing_id = self._specific_record_exist(contacts, **kwargs)
                if not existing_id:
                    new_record_id = contacts.insert_one(kwargs).inserted_id
                    return new_record_id
            except Exception as err:
                print(err)

    def update_record(self, contact_id, new_data):
        with MongoClient(self.connection_str) as client:
            db = client.get_database(self.dbname)
            contacts = db.get_collection(self.collection)

            if not isinstance(new_data, dict):
                new_data = dict(new_data)
            if new_data.get('_id'):
                new_data.pop('_id')
            try:
                contacts.update_one({"_id": ObjectId(contact_id)}, {"$set": new_data})
                return True
            except Exception as err:
                print('Contact updating error:\n',err)
                return False

    def delete_record(self, contact_id):
        with MongoClient(self.connection_str) as client:
            db = client.get_database(self.dbname)
            contacts = db.get_collection(self.collection)
            try:
                result = contacts.delete_one({"_id": ObjectId(contact_id)}).deleted_count
                return result
            except Exception as err:
                print(err)

    def select(self, contact_ids):
        with MongoClient(self.connection_str) as client:
            db = client.get_database(self.dbname)
            contacts = db.get_collection(self.collection)
            result = []
            for contact_id in contact_ids:
                if len(contact_id) > 0:
                    data = contacts.find_one({"_id": ObjectId(contact_id)})
                    if data:
                        result.append(data)
            return result or [{"message": "No contacts found"}]
