git fetch origin
git rebase origin/master
pip install -r docs/requirements.pip
./manage.py makemigrations
./manage.py makemigrations KlimaKar
./manage.py makemigrations commission
./manage.py makemigrations invoicing
./manage.py makemigrations settings
./manage.py makemigrations stats
./manage.py makemigrations warehouse
./manage.py migrate
./manage.py collectstatic --noinput
sudo crontab < docs/crontab.txt
sudo service gunicorn restart
sudo service redis restart
sudo service rqworker restart
