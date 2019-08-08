# -*- coding: utf-8 -*-
"""
Created on 2019/8/7 23:31
@file: EMongoUtil.py
@author: Matt
"""
import pymongo


class MongoClient:
    def __init__(self, _host='localhost', _port=27017):
        self.client = pymongo.MongoClient(host=_host, port=_port)

    def get_documents(self, _db_name, _collection_name, _query=None):
        if _query is None:
            _query = {}
        collection = self.client[_db_name][_collection_name]
        return collection.find(_query)

    def get_one_document(self, _db_name, _collection_name):
        collection = self.client[_db_name][_collection_name]
        return collection.find_one()

    def get_collection_names(self, _db_name):
        db = self.client[_db_name]
        return db.list_collection_names()

    def insert_many_documents(self, _db_name, _collection_name, _data):
        collection = self.client[_db_name][_collection_name]
        collection.insert_many(_data)
        print('insert "%s" finished' % _collection_name)

    def drop_collection(self, _db_name, _collection_name):
        self.client[_db_name][_collection_name].drop()
        print('drop "%s" finished' % _collection_name)
