# -*- coding: utf-8 -*-
from pymongo import MongoClient


class MongoDBConnector():

    # TODO: Implement auth.
    def __init__(self, db_name, db_password: str='', address: str='localhost', port: int=27017):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.get_database(db_name)
