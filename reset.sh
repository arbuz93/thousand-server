#! /bin/bash

python3 $(dirname $0)/manage.py makemigrations user

python3 $(dirname $0)/manage.py migrate
bash $(dirname $0)/load.sh