POSTGRES_STATUS="$(service postgresql status)"
REDIS_STATUS="$(sudo service redis-server status)"

if  [[ $POSTGRES_STATUS =~ 'down' ]];
then
    sudo service postgresql start
fi

if  [[ $REDIS_STATUS =~ 'not running' ]];
then
    sudo service redis-server start
fi
source venv/bin/activate
./manage.py runserver
