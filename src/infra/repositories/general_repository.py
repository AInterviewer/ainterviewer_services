from pymongo import MongoClient

from constants import MONGO_CONNECTION

AINTERVIEWER_CLIENT = MongoClient(MONGO_CONNECTION).ainterviewer


def ainterview_database_exists() -> bool:
    return len(AINTERVIEWER_CLIENT.list_collection_names()) > 0
