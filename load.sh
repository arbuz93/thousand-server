#! /bin/bash

python3 $(dirname $0)/manage.py loaddata $(dirname $0)/logic/data.json
python3 $(dirname $0)/manage.py loaddata $(dirname $0)/user/data.json
