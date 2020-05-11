# -*- coding: utf-8 -*-
from pymongo import MongoClient


class MongoDBConnector():

    def __init__(self, db_name, db_user='', db_password: str='', address: str='localhost', port: int=27017, using_auth: bool=True):
        if using_auth:
            self.client = MongoClient(
                address,
                port,
                username=db_user,
                password=db_password,
                authSource=db_name,
                authMechanism = 'SCRAM-SHA-256'
            )
        else:
            self.client = MongoClient(
                address,
                port
            )
        self.db = self.client.get_database(db_name)
        # Fir checking auth.
        self.db.list_collection_names()