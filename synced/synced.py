#!/usr/bin/env python
# -*- coding: utf-8 -*-

from easyrocks import (
    RocksDB,
    WriteBatch,
    CompressionType,
    utils,
)
import os
from typing import List, Generator

UINT_BYTES = 5
MAX_UINT = 2**(UINT_BYTES * 8) - 1


class DiskStore:
    def __init__(self, path: str = None):
        if not os.path.exists(path):
            os.makedirs(path)

        opts = {
            'create_if_missing': True,
            'compression': CompressionType.lz4_compression,
            'use_fsync': True,
            'paranoid_checks': True,
            'compaction_options_universal': {
                'compression_size_percent': 100,
            }
        }
        self._db = RocksDB(path=path, opts=opts)
        self._write_batch = None

    def reload(self):
        self._db.reload()
        self._write_batch = None

    def begin(self):
        if self._write_batch is None:
            self._write_batch = WriteBatch()

    def commit(self):
        self._db.commit(self._write_batch)
        self._write_batch = None


class CollectionStore(DiskStore):
    def __init__(self, path: str = None):
        super().__init__(path)

    def clear(self):
        for key, _ in self._db.scan():
            self._db.delete(key, write_batch=self._write_batch)


class ListStore(CollectionStore):
    LENGTH_KEY = b'\x00'

    def __init__(self, name: str, path: str):
        super().__init__(f'{path}/list/{name}')
        self._write_batch_index = 0

    @property
    def length(self) -> int:
        real_length = self._db.get(self.LENGTH_KEY)
        real_length = real_length if real_length is not None else 0
        return real_length + self._write_batch_index

    def commit(self):
        super().commit()
        self._write_batch_index = 0

    def get(self) -> Generator:
        for key, value in self._db.scan():
            if key != self.LENGTH_KEY:
                yield value

    def clear(self):
        super().clear()

    def extend(self, iterable):
        current_length = self.length
        is_write_batch_new = self._write_batch is None

        if is_write_batch_new:
            self.begin()

        self._increment_length()

        for index, value in enumerate(iterable):
            key_bytes = self._get_key(current_length + index)
            self._db.put(key_bytes, value, write_batch=self._write_batch)

        if is_write_batch_new:
            self.commit()

    def append(self, value):
        current_length = self.length
        is_write_batch_new = self._write_batch is None

        if is_write_batch_new:
            self.begin()

        self._increment_length()
        key_bytes = self._get_key(current_length)
        self._db.put(key_bytes, value, write_batch=self._write_batch)

        if is_write_batch_new:
            self.commit()

    def delete(self, index: int):
        key_bytes = self._get_key(index)
        self._db.delete(key_bytes, write_batch=self._write_batch)

    def put(self, index, value):
        key_bytes = self._get_key(index)
        self._db.put(key_bytes, value, write_batch=self._write_batch)

    @staticmethod
    def _get_key(index: int) -> bytes:
        if isinstance(index, int):
            return utils.int_to_padded_bytes(index, UINT_BYTES)
        raise TypeError

    def _increment_length(self):
        if self._write_batch:
            self._write_batch_index += 1
        new_length = self.length
        if new_length > MAX_UINT:
            raise ValueError(f'{new_length} > {MAX_UINT}')
        self._db.put(self.LENGTH_KEY, new_length, write_batch=self._write_batch)


class DictStore(CollectionStore):
    def __init__(self, name: str, path: str):
        super().__init__(f'{path}/dict/{name}')

    def get(self) -> Generator:
        for key, value in self._db.scan():
            yield key.decode('utf-8'), value

    def clear(self):
        super().clear()

    def delete(self, key: str):
        key_bytes = self._get_key(key)
        self._db.delete(key_bytes, write_batch=self._write_batch)

    def put(self, key: str, value):
        key_bytes = self._get_key(key)
        self._db.put(key_bytes, value, write_batch=self._write_batch)

    @staticmethod
    def _get_key(key) -> bytes:
        if not isinstance(key, str):
            raise TypeError(f'sdict keys must be strings')
        return bytes(key, 'utf-8')


class ValueStore(DiskStore):
    VALUE_KEY = b'\x00'

    def __init__(self, name: str, path: str):
        super().__init__(f'{path}/value/{name}')

    def set(self, value):
        self._db.put(self.VALUE_KEY, value)

    def get(self):
        return self._db.get(self.VALUE_KEY)

    def delete(self):
        self._db.delete(self.VALUE_KEY)
