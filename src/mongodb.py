from pymongo import MongoClient
import os

# Add mongo uri to python mongo client
mongo_uri = os.environ.get('MONGO_URI')
mongo_client = MongoClient(mongo_uri)

# Get Mongo database
mongo = mongo_client.get_database('test')
account_table = mongo.get_collection('account')
