# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.database import Database


class MongoDBConnector():

    def __init__(self, db_name, db_user='', db_password: str= '', host: str= 'localhost', port: int=27017, using_auth: bool=True):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.host = host
        self.port = port
        self.using_auth = using_auth

    def connect(self) -> MongoClient:
        if self.using_auth:
            client = MongoClient(
                self.host,
                self.port,
                username=self.db_user,
                password=self.db_password,
                authSource=self.db_name,
                authMechanism = 'SCRAM-SHA-256'
            )
        else:
            client = MongoClient(
                self.host,
                self.port
            )
        return client

    def connect_and_get_db(self) -> Database:
        client = self.connect()
        # Check auth
        client[self.db_name].list_collections()
        return client[self.db_name]
