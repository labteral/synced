#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rocksdb
from easyrocks import DB, Options, WriteBatch, utils


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


COLL_TYPES = set(['list', 'dict'])


class DiskStore(metaclass=Singleton):

    MAX_KEY_LENGTH = 20

    def __init__(self, path=None):
        if path is None:
            path = './synced-data'
        opts = {'create_if_missing': True}
        self._db = DB(f'{path}', opts)

    # COMMON ##########################################################################################################

    @staticmethod
    def _get_real_key(name, coll_type, key=None):
        prefix = DiskStore._get_prefix(name, coll_type)
        if key is None:
            return prefix[:-1]
        real_key = f'{prefix}{key}'
        return real_key

    @staticmethod
    def _get_prefix(name, coll_type):
        return f'{name}_{coll_type}_'

    def commit(self, write_batch):
        self._db.commit(write_batch)

    def delete(self, key, name, coll_type):
        real_key = DiskStore._get_real_key(name, coll_type, key)
        self._db.delete(real_key)

    # VALUE ###########################################################################################################

    def set_value(self, value, name):
        coll_type = 'value'
        real_key = DiskStore._get_real_key(name, coll_type)
        self._db.put(real_key, value)

    def get_value(self, name):
        coll_type = 'value'
        real_key = DiskStore._get_real_key(name, coll_type)
        return self._db.get(real_key)

    # DICT ############################################################################################################

    def put_dict(self, key, value, name, write_batch=None):
        coll_type = 'dict'
        real_key = DiskStore._get_real_key(name, coll_type, key)
        self._db.put(real_key, value, write_batch=write_batch)

    # COLLECTIONS #####################################################################################################

    def delete_coll(self, name, coll_type):
        if coll_type not in COLL_TYPES:
            raise TypeError

        prefix = DiskStore._get_prefix(name, coll_type)
        for key, _ in self._db.scan(prefix):
            self._db.delete(key)

    def get_coll(self, name, coll_type):
        if coll_type not in COLL_TYPES:
            raise TypeError

        prefix = DiskStore._get_prefix(name, coll_type)
        for key, value in self._db.scan(prefix):
            if coll_type == 'list':
                if key != DiskStore._get_real_key(name, coll_type, 'length'):
                    yield value
            elif coll_type == 'dict':
                original_key = key.split(DiskStore._get_prefix(name, coll_type))[1]
                yield original_key, value

    # LIST ############################################################################################################

    def append_list(self, value, name):
        coll_type = 'list'

        write_batch = WriteBatch()

        length = self._get_list_length(name)
        real_key = DiskStore._get_real_key(name, coll_type, 'length')
        self._db.put(real_key, length, write_batch=write_batch)

        key = utils.get_padded_int(length)
        real_key = DiskStore._get_real_key(name, coll_type, key)
        self._db.put(real_key, value, write_batch=write_batch)

        self._db.commit(write_batch)

    def _get_list_length(self, name):
        coll_type = 'list'

        real_key = DiskStore._get_real_key(name, coll_type, 'length')
        length = self._db.get(real_key)

        if length is None:
            length = 0
        length += 1

        return length