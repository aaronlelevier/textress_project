#!/bin/bash -lx

echo "Only for loading reloading database data, not a full deploy script."

echo "MUST BE AT './manage.py' DIR LEVEL!"

dropdb textress
wait
createdb textress
wait
./manage.py migrate

wait
echo "Icons required for User profiles"
./manage.py loaddata icons.json

wait
echo "Hotel groups and Superuser"
./manage.py create_initial_user_and_groups

wait
echo "Other fixtures"

echo "default pricing and transaction types"
./manage.py loaddata pricing.json
./manage.py loaddata trans_type.json

echo "system auto replies and trigger types"
./manage.py loaddata reply.json
./manage.py loaddata trigger_type.json

echo "index.html fixtures"
./manage.py loaddata topic.json
./manage.py loaddata qa.json

echo "Stripe card images"
./manage.py loaddata card_images.json