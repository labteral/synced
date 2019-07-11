#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .synced import DiskStore
import logging
from collections.abc import Iterable


class svalue:

    COLL_TYPE = 'value'

    def __init__(self, name, path=None):
        if len(name) > DiskStore.MAX_KEY_LENGTH:
            raise ValueError
        self._disk_store = DiskStore(path)
        self._name = name
        self._memory_store = self._disk_store.get_value(self._name)

    def __eq__(self, other):
        return self._memory_store.__eq__(other)

    def __str__(self):
        return self._memory_store.__str__()

    def __repr__(self):
        return self._memory_store.__repr__()

    def set(self, value):
        self._disk_store.set_value(value, self._name)
        self._memory_store = value

    def delete(self):
        self._disk_store.delete(None, self._name, svalue.COLL_TYPE)
        self._memory_store = None