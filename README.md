# django-klima-kar
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/karpiq24/django-klima-kar/blob/master/LICENSE)

Django project used in my family buisness. It provides warehouse management and invoicing with advanced statistics.


## Features
- Warehouse management
  - wares, suppliers and purchase invoices
  - export data to multiple formats
  - generate inventory report
  - automatically load data from suppliers using APIs or web crawling
- Invoicing
  - contractors, sale invoices and default services
  - multiple invoice forms (VAT, WDT, Pro forma, Corrective)
  - download contractor data from REGON API
  - export invoice to PDF
  - print invoice
  - email invoice to contractor
- Advanced statistics
<<<<<<< HEAD
  - rich interactive charts and metrics
=======
  - rich interactive charts
>>>>>>> 8c61c4aba8b70187e3199ba960808a8ee5ae2790
  - detect purchased ware price changes
  - weekly, monthly and yearly reports
- Other
  - advanced filtering of all models
  - filtering and paginating tables using ajax
  - automatic dropbox backup

<<<<<<< HEAD
## Requirements
=======
## Requirments
>>>>>>> 8c61c4aba8b70187e3199ba960808a8ee5ae2790
1. docs/requirements.pip
   ```
   pip install -r docs/requirements.pip
   ```
2. [WeasyPrint dependecies](https://weasyprint.readthedocs.io/en/latest/install.html)
    ```
    sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
    ```
