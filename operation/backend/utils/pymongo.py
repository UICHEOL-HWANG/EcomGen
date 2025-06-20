from pymongo import MongoClient
from model.settings import settings

def get_token_collection():
    client = MongoClient(settings.mongodb_uri)
    return client["ecomgen"]["refresh_tokens"]

