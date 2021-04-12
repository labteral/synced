#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .synced import DictStore
from collections.abc import Mapping, Iterable


class sdict(dict):
    def __init__(self, name, collection=None, path=None, **kwargs):
        if path is None:
            path = './synced-data'

        self._disk_store = DictStore(name, path)
        self._load_memory_store()

        if collection is not None:
            if not self._memory_store:
                self.update(collection)
            else:
                raise ValueError('already initialized, collection discarded')

    @property
    def dict(self):
        return dict(self._memory_store)

    def begin(self):
        self._disk_store.begin()

    def commit(self):
        self._disk_store.commit()

    def reload(self):
        self._disk_store.reload()
        self._load_memory_store()

    def update(self, collection):
        try:
            if isinstance(collection, Mapping):
                self._disk_store.begin()
                for key, value in collection.items():
                    self.__setitem__(key, value)
                self._disk_store.commit()
                return
            if isinstance(collection, Iterable):
                self._disk_store.begin()
                for item in collection:
                    self.__setitem__(item[0], item[1])
                self._disk_store.commit()
                return
        except Exception as error:
            self.reload()
            raise error

        raise TypeError

    def clear(self):
        self._disk_store.clear()
        self._memory_store = dict()

    def items(self):
        return self._memory_store.items()

    def pop(self, key, default=None):
        self._disk_store.delete(key)
        return self._memory_store.pop(key)

    def setdefault(self, key, default=None):
        self.__setitem__(key, default)

    def copy(self):
        raise NotImplementedError

    def popitem(self):
        raise NotImplementedError

    def _load_memory_store(self):
        self._memory_store = dict()
        for key, value in self._disk_store.get():
            self._memory_store[key] = value

    def __len__(self):
        return self._memory_store.__len__()

    def __setitem__(self, key, value):
        self._disk_store.put(key, value)
        self._memory_store[key] = value

    def __getitem__(self, key):
        return self._memory_store[key]

    def __delitem__(self, key):
        self._disk_store.delete(key)
        del self._memory_store[key]

    def __contains__(self, value):
        return self._memory_store.__contains__(value)

    def __eq__(self, other):
        return self._memory_store.__eq__(other)

    def __str__(self):
        return self._memory_store.__str__()

    def __repr__(self):
        return self._memory_store.__repr__()
