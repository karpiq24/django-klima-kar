git stash
git fetch origin
git rebase origin/master
git stash pop
pip install -r docs/requirements.pip
./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic --noinput
sudo crontab < docs/crontab.txt
sudo service gunicorn restart
sudo service redis restart
sudo service rqworker restart
