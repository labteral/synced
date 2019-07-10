#!/bin/bash
export path=/tmp/synced/data
rm -rf $path
mkdir -p $path
python minimal.py
