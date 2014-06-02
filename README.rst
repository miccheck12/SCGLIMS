====================
SCGLIMS
====================

.. image:: https://travis-ci.org/BILS/SCGLIMS.svg?branch=master
  :target: https://travis-ci.org/BILS/SCGLIMS

.. image:: https://coveralls.io/repos/BILS/SCGLIMS/badge.png?branch=master
  :target: https://coveralls.io/r/BILS/SCGLIMS?branch=master


SCGLIMS is a Lab Information Management System developed for the `Ettema Lab`_
by `BILS`_.

The database implements the workflow of the Ettema Lab:

.. image:: http://raw.githubusercontent.com/BILS/SCGLIMS/master/docs/images/flowchartlab.png

If your lab has a similar workflow you might be able to use the SCGLIMS as is.
Otherwise an amout of tweaking might be required in which case we would
recommend forking the repository and only using certain elements.


* Crappy Documentation: `<http://scglims.rtfd.org>`_
* Demo: `<http://bit.ly/scglims-heroku>`_ (for admin user/pass inodb)
* Presentation: `<http://bit.ly/limstalk>`_
* GitHub: `<https://github.com/BILS/SCGLIMS/>`_
* Free software: GPLv3 License
.. * PyPI: Not yet available

.. _`Ettema Lab`: http://ettemalab.org
.. _`BILS`: http://bils.se

Requirements
-----------

* Python 2.7+
* Django 1.6.1
* Local: https://github.com/BILS/SCGLIMS/blob/master/lims_project/requirements/local.txt
* Development: https://github.com/BILS/SCGLIMS/blob/master/lims_project/requirements/development.txt

Installation
-------------

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


Contribute
----------

Contributions are greatly appreciated, please read the `contribution instructions`_.

.. _`contribution instructions`: https://github.com/BILS/SCGLIMS/blob/master/CONTRIBUTORS.md
