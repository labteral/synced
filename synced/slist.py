#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .synced import DiskStore
import logging
from collections.abc import Iterable


class slist(list):

    COLL_TYPE = 'list'

    def __init__(self, name, collection=None, path=None, **kwargs):
        if len(name) > DiskStore.MAX_KEY_LENGTH:
            raise ValueError
        self._memory_store = list()
        self._disk_store = DiskStore(path)
        self._name = name

        for value in self._disk_store.get_coll(self._name, slist.COLL_TYPE):
            self._memory_store.append(value)

        if collection is not None:
            if not self._memory_store:
                self.update(collection)
            else:
                logging.warn('already initialized, collection discarded')

    def __eq__(self, other):
        return self._memory_store.__eq__(other)

    def __str__(self):
        return self._memory_store.__str__()

    def __repr__(self):
        return self._memory_store.__repr__()

    def update(self, collection):
        if not isinstance(collection, str) and isinstance(collection, Iterable):
            for item in collection:
                self.append(item)
            return
        raise TypeError

    def append(self, value):
        self._disk_store.append_list(value, self._name)
        self._memory_store.append(value)

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def __len__(self):
        return self._memory_store.__len__()

    def __iter__(self):
        return self._memory_store.__iter__()

    def __getitem__(self, index):
        return self._memory_store.__getitem__(index)

    def __delitem__(self, index):
        self._disk_store.delete(str(index), self._name, slist.COLL_TYPE)
        del self._memory_store[index]

    def __setitem__(self, index, item):
        self._disk_store.put(str(index), item, self._name, slist.COLL_TYPE)
        self._memory_store[index] = item

    def clear(self):
        self._disk_store.delete_coll(self._name, slist.COLL_TYPE)
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