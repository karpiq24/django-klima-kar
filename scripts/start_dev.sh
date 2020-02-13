POSTGRES_STATUS="$(service postgresql status)"
REDIS_STATUS="$(sudo service redis-server status)"
SOLR_STATUS="$(sudo service solr status)"

if  [[ $POSTGRES_STATUS =~ 'down' ]];
then
    sudo service postgresql start
fi

if  [[ $REDIS_STATUS =~ 'not running' ]];
then
    sudo service redis-server start
fi

if  [[ $SOLR_STATUS =~ 'No Solr nodes are running.' ]];
then
    sudo service solr start
fi

source venv/bin/activate
./manage.py runserver
