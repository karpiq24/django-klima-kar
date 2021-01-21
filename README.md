# django-klima-kar

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/karpiq24/django-klima-kar/blob/master/LICENSE)

Django project used in my family buisness. It provides warehouse management, invoicing and commission tracking with advanced statistics.

## Features

-   Warehouse management
    -   wares, suppliers and purchase invoices
    -   export data to multiple formats
    -   generate inventory report
    -   automatically load data from suppliers using APIs or web scraping
-   Invoicing
    -   contractors, sale invoices and default services
    -   multiple invoice forms (VAT, WDT, Pro forma, Corrective)
    -   download contractor data from REGON API
    -   export invoice to PDF
    -   print invoice
    -   email invoice to contractor
    -   validate contractor VAT payer status
-   Commissions
    -   commissions, vehicles, components
    -   decode AZTEC code from registration papers to get vehicle information
    -   export commission to PDF
    -   print commission
    -   email commission to contractor
    -   generate invoice based on commission
    -   handle file uploads using WD My Cloud Home API
    -   Send SMS notifications to contractors
    -   React SPA for large touchscreen monitors
-   Advanced statistics
    -   rich interactive charts and metrics
    -   detect purchased ware price changes
    -   weekly, monthly and yearly reports
-   Wiki module
    - articles with Markdown syntax
    - hashtags
    - file uploads using WD My Cloud Home API
    - image gallery
-   Other
    -   advanced filtering of all models
    -   filtering and paginating tables using ajax
    -   JSON dump and SQL dump backup with upload to dropbox and WD My Cloud Home
    -   2-step email authentication
    -   login from remote location only for managers and admins
    -   create audit logs for creating, modyfing and deleteing objects
    -   Full text search using Solr and django-haystack
    -   GraphQL API

## Installation

1. Install system dependecies
    ```
    sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info virtualenv libpq-dev postgresql postgresql-contrib redis-server poppler-utils
    ```
2. Enable and configure Postgres
    ```
    sudo service postgresql start
    sudo -u postgres psql
    CREATE DATABASE klimakar;
    CREATE USER admin WITH PASSWORD '';
    ALTER ROLE admin SUPERUSER;
    ALTER ROLE admin SET client_encoding TO 'utf8';
    ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
    ALTER ROLE admin SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE klimakar TO admin;
    ```
    Restoring SQL dump data:
    ```
    sudo su postgres
    psql klimakar < /path/to/dump.sql
    ```
3. Enable Redis server
    ```
    sudo systemctl enable redis-server.service
    ```
4. Create and activate virtual envoirment
    ```
    virtualenv -p python3 venv
    source venv/bin/activate
    ```
5. Install python requirements
    ```
    pip install -r docs/requirements.pip
    ```
6. Install fonts
    ```
    sudo cp KlimaKar/static/fonts/* /usr/local/share/fonts/
    sudo fc-cache -fv
    ```
7. Compile aztec code decoder
    ```
    g++ -o scripts/aztec scripts/aztec.cpp
    ```
8. Prepare settings
    ```
    cp docs/settings_local.py KlimaKar
    ```
9. Build React frontend
    ```
    cd tiles/
    npm install
    npm run build
    ```
10. Migrating database
    ```
    ./manage.py makemigrations
    ./manage.py makemigrations search --empty
    ```
    In empty search app migration paste contents of migration file located in /docs/search_migration.py
    ```
    ./manage migrate
    ```
11. Build search index, create superuser and run local server
    ```
    ./manage.py rebuild_index
    ./manage.py createsuperuser
    ./manage.py runserver
    ```
