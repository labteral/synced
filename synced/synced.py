#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rocksdb
from . import utils
from easyrocks import DB, Options, WriteBatch


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DiskStore(metaclass=Singleton):
    def __init__(self, path=None):
        if path is None:
            path = './synced-data'
        opts = {'create_if_missing': True}
        self._db = DB(f'{path}', opts)

    @staticmethod
    def _get_real_key(name, coll_type, key):
        return f'{name}_{coll_type}_{key}'

    @staticmethod
    def _get_prefix(name, coll_type):
        return f'{name}_{coll_type}_'

    def put(self, key, value, name, write_batch=None):
        coll_type = 'dict'
        real_key = DiskStore._get_real_key(name, coll_type, key)
        self._db.put(real_key, value, write_batch=write_batch)

    def commit(self, write_batch):
        self._db.commit(write_batch)

    def get(self, key, name, coll_type):
        real_key = DiskStore._get_real_key(name, coll_type, key)
        return self._db.get(real_key)

    def delete(self, key, name, coll_type):
        real_key = DiskStore._get_real_key(name, coll_type, key)
        self._db.delete(real_key, sync=True)

    def delete_all(self, name, coll_type):
        prefix = DiskStore._get_prefix(name, coll_type)
        for key, _ in self._db.scan(prefix):
            self.delete(key, name, coll_type)

    def get_all(self, name, coll_type):
        prefix = DiskStore._get_prefix(name, coll_type)
        for key, value in self._db.scan(prefix):
            if coll_type == 'list':
                if key != DiskStore._get_real_key(name, coll_type, 'length'):
                    yield value
            elif coll_type == 'dict':
                yield key, value

    def append(self, value, name):
        coll_type = 'list'

        write_batch = WriteBatch()

        length = self.get_length(name)
        real_key = DiskStore._get_real_key(name, coll_type, 'length')
        self._db.put(real_key, length, write_batch=write_batch)

        key = utils.get_padded_int(length)
        real_key = DiskStore._get_real_key(name, coll_type, key)
        self._db.put(real_key, value, write_batch=write_batch)

        self._db.commit(write_batch)

    def get_length(self, name):
        coll_type = 'list'

        real_key = DiskStore._get_real_key(name, coll_type, 'length')
        length = self._db.get(real_key)

        if length is None:
            length = 0
        length += 1

        return length