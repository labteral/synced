#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .synced import ListStore
import logging
from collections.abc import Iterable


class slist(list):
    def __init__(self, name, collection=None, path=None, **kwargs):
        if path is None:
            path = './synced-data'

        self._disk_store = ListStore(name, path)
        self._load_memory_store()

        if collection is not None:
            if not self._memory_store:
                self.update(collection)
            else:
                logging.warn('already initialized, collection discarded')

    @property
    def list(self):
        return list(self._memory_store)

    def begin(self):
        self._disk_store.begin()

    def commit(self):
        self._disk_store.commit()

    def reload(self):
        self._disk_store.reload()
        self._load_memory_store()

    def update(self, collection):
        if not isinstance(collection, str) and isinstance(collection, Iterable):
            self.extend(collection)
            return
        raise TypeError

    def append(self, value):
        try:
            self._disk_store.append(value)
            self._memory_store.append(value)
        except Exception as error:
            self.reload()
            raise error

    def extend(self, iterable):
        try:
            self._disk_store.extend(iterable)
            self._memory_store.extend(iterable)
        except Exception as error:
            self.reload()
            raise error

    def clear(self):
        self._disk_store.clear()
        self._memory_store = list()

    def count(self, value):
        return self._memory_store.count(value)

    def index(self, index, start=None, end=None):
        return self._memory_store.index(index, start, end)

    def pop(self, index=None):
        raise NotImplementedError

    def remove(self, value):
        raise NotImplementedError

    def sort(self, key=None, reverse=False):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def _load_memory_store(self):
        self._memory_store = list()
        for value in self._disk_store.get():
            self._memory_store.append(value)

    def __eq__(self, other):
        return self._memory_store.__eq__(other)

    def __str__(self):
        return self._memory_store.__str__()

    def __repr__(self):
        return self._memory_store.__repr__()

    def __len__(self):
        return self._memory_store.__len__()

    def __iter__(self):
        return self._memory_store.__iter__()

    def __getitem__(self, index):
        return self._memory_store.__getitem__(index)

    def __delitem__(self, index):
        self._disk_store.delete(index)
        del self._memory_store[index]

    def __setitem__(self, index, item):
        self._disk_store.put(index, item)
        self._memory_store[index] = item
