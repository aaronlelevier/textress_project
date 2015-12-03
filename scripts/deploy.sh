#!/bin/bash -lx

echo "START BUILD"


npm install


cd textress
echo "DATABASE"
./manage.py migrate
wait


echo "LOAD FIXTURES"
echo "default pricing and transaction types"
./manage.py loaddata pricing.json
./manage.py loaddata trans_type.json

echo "system auto replies and trigger types"
./manage.py loaddata reply.json
./manage.py loaddata trigger_type.json

echo "index.html fixtures"
./manage.py loaddata topic.json
./manage.py loaddata qa.json

echo "guest+user profile icons"
./manage.py loaddata icons.json

echo "Stripe card images"
./manage.py loaddata card_images.json


echo "COLLECT STATIC ASSETS"
wait
rm -rf static/*
wait
./manage.py collectstatic --noinput
