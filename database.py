from pymongo import MongoClient


def start_database():
    client=MongoClient()
    db=client.login_database    