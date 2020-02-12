# django-klima-kar
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/karpiq24/django-klima-kar/blob/master/LICENSE)

Django project used in my family buisness. It provides warehouse management, invoicing and commission tracking with advanced statistics.


## Features
- Warehouse management
    - wares, suppliers and purchase invoices
    - export data to multiple formats
    - generate inventory report
    - automatically load data from suppliers using APIs or web scraping
- Invoicing
    - contractors, sale invoices and default services
    - multiple invoice forms (VAT, WDT, Pro forma, Corrective)
    - download contractor data from REGON API
    - export invoice to PDF
    - print invoice
    - email invoice to contractor
    - validate contractor VAT payer status
- Commissions
    - commissions, vehicles, components
    - decode AZTEC code from registration papers to get vehicle information
    - export commission to PDF
    - print commission
    - email commission to contractor
    - generate invoice based on commission
    - handle file uploads using WD My Cloud Home API
    - Send SMS notifications to contractors
- Advanced statistics
    - rich interactive charts and metrics
    - detect purchased ware price changes
    - weekly, monthly and yearly reports
- Other
    - advanced filtering of all models
    - filtering and paginating tables using ajax
    - JSON dump and SQL dump backup with upload to dropbox and WD My Cloud Home
    - 2-step email authentication
    - login from remote location only for managers and admins
    - create audit logs for creating, modyfing and deleteing objects
    - Full text search using Solr and django-haystack

## Requirements
1. [WeasyPrint dependecies](https://weasyprint.readthedocs.io/en/latest/install.html)
    ```
    sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
    ```
2. Install pip and virtualenv
    ```
    sudo apt install virtualenv python3-pip
    ```
3. Install Postgres and configure
    ```
    sudo apt install libpq-dev postgresql postgresql-contrib
    sudo service postgresql start
    sudo -u postgres psql
    CREATE DATABASE klimakar;
    CREATE USER admin WITH PASSWORD '';
    ALTER ROLE admin SET client_encoding TO 'utf8';
    ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
    ALTER ROLE admin SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE klimakar TO admin;
    ```
4. Install Redis
    ```
    sudo apt-get install redis-server
    sudo systemctl enable redis-server.service
    ```
5. Install Solr
   ```
   sudo apt install openjdk-8-jdk openjdk-8-jre
   curl -O https://archive.apache.org/dist/lucene/solr/6.6.6/solr-6.6.6.tgz
   tar xvf solr-6.6.6.tgz
   sudo ./solr-6.6.6/bin/install_solr_service.sh solr-6.6.6.tgz
   sudo su solr
   /opt/solr-6.6.6/bin/solr create -c klimakar -n basic_config
   sudo venv/bin/python manage.py build_solr_schema --configure-directory=/var/solr/data/klimakar/conf --reload-core klimakar
   ```
6. Create and activate virtual envoirment
    ```
    virtualenv -p python3 venv
    source venv/bin/activate
    ```
7. Install python requirements
   ```
   pip install -r docs/requirements.pip
   ```
8. Install fonts
   ```
   sudo cp KlimaKar/static/fonts/* /usr/local/share/fonts/
   sudo fc-cache -fv
   ```
9. Compile aztec code decoder
   ```
   g++ -o scripts/aztec scripts/aztec.cpp
   ```
10.  Prepare settings
    ```
    cp docs/settings_local.py KlimaKar
    ```
11. Migrate database, create superuser and run local server
    ```
    ./manage.py makemigrations
    ./manage.py makemigrations commission
    ./manage.py makemigrations invoicing
    ./manage.py makemigrations settings
    ./manage.py makemigrations stats
    ./manage.py makemigrations warehouse
    ./manage.py makemigrations KlimaKar
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver
    ```
