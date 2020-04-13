#!/bin/bash
export path=/tmp/synced/data
rm -rf $path
mkdir -p $path
python3 minimal.py
