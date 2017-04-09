#! /bin/bash

rm -rf $(dirname $0)/user/migrations
rm -rf $(dirname $0)/game/migrations
rm -rf $(dirname $0)/logic/migrations

python3 $(dirname $0)/manage.py makemigrations user
python3 $(dirname $0)/manage.py makemigrations game
python3 $(dirname $0)/manage.py makemigrations logic

python3 $(dirname $0)/manage.py migrate
bash $(dirname $0)/load.sh