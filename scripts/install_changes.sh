git fetch origin
git rebase origin/master
pip install -r docs/requirements.pip
./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic
sudo crontab < docs/crontab.txt
sudo service gunicorn restart
