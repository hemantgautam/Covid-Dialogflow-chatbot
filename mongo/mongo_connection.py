from pymongo import MongoClient
from config_reader import ConfigReader


class DatabaseConnect():
    def __init__(self):

        # Initialization ConfigReader class
        self.config_reader = ConfigReader()

        # read_config method call
        self.configuration = self.config_reader.read_config()

        # storing mongodb connection url in mongo_connection variable
        self.mongo_connection = self.configuration['MONGO_CONNECTION']

        # Call for Mongo db connection
        cluster = MongoClient(self.mongo_connection)

        # mentioned collection name, in our case its covid
        db = cluster['covid']
        collection = db['covid']
        self.collection = collection

    def add_user_data(self, session_id, user_details):

        # Storing user's session id as primary key and user details in python dict
        user_dict = {"_id": session_id, "user_details": user_details}

        # Storing data to Mongo DB
        self.collection.insert_one(user_dict)
        print("Data Stored in DB")
