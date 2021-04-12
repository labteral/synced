#!/bin/bash
python3 setup.py install && for test in tests/*.py; do python3 "$test"; done
