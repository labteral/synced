#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .synced import ValueStore


class svalue:
    def __init__(self, name, path=None):
        if path is None:
            path = './synced-data'

        self._disk_store = ValueStore(name, path)
        self._load_memory_store()

    def reload(self):
        self._disk_store.reload()
        self._load_memory_store()

    @property
    def value(self):
        return self._memory_store

    def get(self):
        return self._memory_store

    def set(self, value):
        self._disk_store.set(value)
        self._memory_store = value

    def clear(self):
        self._disk_store.delete()
        self._memory_store = None

    def delete(self):
        print('[WARNING] delete method is deprecated: use clear instead')
        self.clear()

    def _load_memory_store(self):
        self._memory_store = self._disk_store.get()

    def __eq__(self, other):
        return self._memory_store.__eq__(other)

    def __str__(self):
        return self._memory_store.__str__()

    def __repr__(self):
        return self._memory_store.__repr__()
