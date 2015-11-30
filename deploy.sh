npm install

echo "DATABASE"
dropdb textress
wait
createdb textress

# this is only ran in dev (not in build script)
# ./manage.py makemigrations account concierge contact main payment sms utils

./manage.py migrate

wait
cd textress
./manage.py collectstatic --noinput
