from pymongo import MongoClient
from src.constant.config import MONGODB_URI

# Add mongo uri to python mongo client
mongo_uri = MONGODB_URI
mongo_client = MongoClient(mongo_uri)

# Get Mongo database
mongo = mongo_client.get_database('test')
ACCOUNT_TABLE = mongo.get_collection('account')
BOOKING_TABLE = mongo.get_collection('bookings')
