git fetch origin
git rebase origin/master
pip install --upgrade pip
pip install -r docs/requirements.pip
./manage.py makemigrations
./manage.py migrate
if [ "$1" == "npm" ]; then
    cd tiles/
    npm ci
    npm run build
    cd ..
fi
./manage.py collectstatic --noinput
sudo crontab < docs/crontab.txt
sudo service gunicorn restart
sudo service redis restart
sudo service rqworker restart
