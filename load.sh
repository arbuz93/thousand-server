#! /bin/bash

python3 $(dirname $0)/manage.py loaddata $(dirname $0)/logic/data.json
