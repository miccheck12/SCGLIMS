Installation
============
Requirements
--------------

* Python 2.7+
* Django 1.6.1
* Local: https://github.com/BILS/SCGLIMS/blob/master/lims_project/requirements/local.txt
* Development: https://github.com/BILS/SCGLIMS/blob/master/lims_project/requirements/development.txt

Installation
--------------

Clone the repository to your computer:

::
    
    git clone https://github.com/BILS/SCGLIMS

Local installation:

::
    
    pip install -r lims_project/requirements/local.txt


Running SCGLIMS
----------------

Locally
********

Without example data:

::
        
    cd lims_project
    python manage.py syncdb --settings=lims_project.settings.local && \
    python manage.py runserver 127.0.0.1:8000 --settings=lims_project.settings.local

With example data:
 
::
     
    cd lims_project
    python manage.py syncdb --settings=lims_project.settings.local && \
    python manage.py loaddata example --settings=lims_project.settings.local && \
    python manage.py runserver 127.0.0.1:8000 --settings=lims_project.settings.local
