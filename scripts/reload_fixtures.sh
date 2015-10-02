echo "MUST BE AT './manage.py' DIR LEVEL!"
dropdb textress
createdb textress
./manage.py migrate
wait
./manage.py loaddata fixtures/startup.json
