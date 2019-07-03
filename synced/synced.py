#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rocksdb
from . import utils
from rocksdb import DB, Options, WriteBatch


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DiskStore(metaclass=Singleton):
    def __init__(self, chain_dir):
        self._db = DB(f'{chain_dir}', Options(create_if_missing=True))

    def put(self, key, value, name, coll_type, write_batch=None):
        if type(key) is not str:
            raise TypeError
        key_bytes = utils.get_key_bytes(key, name, coll_type)
        value_bytes = utils.to_bytes(value)

        if write_batch is not None:
            write_batch.put(key_bytes, value_bytes)
        else:
            self._db.put(key_bytes, value_bytes, sync=True)

        return

    def get(self, key, name, coll_type):
        key_bytes = utils.get_key_bytes(key, name, coll_type)
        value_bytes = self._db.get(key_bytes)
        if value_bytes is not None:
            return utils.to_object(value_bytes)
        return

    def delete(self, key, name, coll_type):
        key_bytes = utils.get_key_bytes(key, name, coll_type)
        self._db.delete(key_bytes, sync=True)

    def delete_all(self, name, coll_type):
        for key, _ in self._get_all(name, coll_type):
            self.delete(key, name, coll_type)

    def _get_all(self, name, coll_type):
        prefix = utils.str_to_bytes(f'{name}_{coll_type}_')
        iterator = self._db.iterkeys()
        iterator.seek(prefix)

        for key_bytes in iterator:
            key = utils.bytes_to_str(key_bytes.split(prefix)[1])
            value_bytes = self._db.get(key_bytes)
            value = utils.to_object(value_bytes)
            yield key, value

    def get_all(self, name, coll_type):
        for key, value in self._get_all(name, coll_type):
            if coll_type == 'list':
                if key != 'length':
                    yield value
            elif coll_type == 'dict':
                yield key, value

    def append(self, value, name, coll_type):
        if coll_type != 'list':
            raise ValueError

        length = self.get_length(name, coll_type)

        write_batch = WriteBatch()
        self.put('length', length, name, coll_type, write_batch=write_batch)
        self.put(f'{length - 1}', value, name, coll_type, write_batch=write_batch)
        self._db.write(write_batch, sync=True)

    def get_length(self, name, coll_type):
        if coll_type != 'list':
            raise NotImplementedError

        length = self.get('length', name, coll_type)
        if length is None:
            length = 0
        length += 1
        return length