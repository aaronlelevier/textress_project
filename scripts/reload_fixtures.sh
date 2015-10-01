cd textress
dropdb textress
createdb textress
./manage.py migrate
wait
./manage.py loaddata account/fixtures/pricing.json