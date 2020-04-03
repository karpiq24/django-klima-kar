git fetch origin
git rebase origin/master
pip install -r docs/requirements.pip
./manage.py makemigrations
./manage.py migrate
cd tiles/
npm ci
npm run build
cd ..
./manage.py collectstatic --noinput
sudo crontab < docs/crontab.txt
sudo service gunicorn restart
sudo service redis restart
sudo service rqworker restart
