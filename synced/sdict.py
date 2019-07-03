#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import utils
from .synced import DiskStore
import logging
from collections.abc import Mapping, Iterable


class sdict(dict):
    def __init__(self, name, collection=None, chain_dir='./synced-data', **kwargs):
        self._memory_store = dict()
        self._disk_store = DiskStore(chain_dir)
        self._name = name

        for key, value in self._disk_store.get_all(self._name, 'dict'):
            self._memory_store[key] = value

        if collection is not None:
            self.update(collection)

    def __str__(self):
        return self._memory_store.__str__()

    __repr__ = __str__

    def update(self, collection):
        if isinstance(collection, Mapping):
            for key, value in collection.items():
                self.__setitem__(key, value)
            return
        if isinstance(collection, Iterable):
            for item in collection:
                self.__setitem__(item[0], item[1])
            return
        raise TypeError

    def clear(self):
        self._disk_store.delete_all(self._name, 'dict')
        self._memory_store = dict()

    def get_dict(self):
        return dict(self._memory_store)

    def pop(self, key, default=None):
        self._disk_store.delete(key, self._name, 'dict')
        return self._memory_store.pop(key)

    def setdefault(self, key, default=None):
        self.__setitem__(key, default)

    def __len__(self):
        return self._memory_store.__len__()

    def __setitem__(self, key, value):
        self._disk_store.put(key, value, self._name, 'dict')
        self._memory_store[key] = value

    def __getitem__(self, key):
        return self._memory_store[key]

    def __delitem__(self, key):
        self._disk_store.delete(key, self._name, 'dict')
        del self._memory_store[key]

    def copy(self):
        raise NotImplementedError

    def popitem(self):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError