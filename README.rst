====================
SCGLIMS
====================

.. image:: https://travis-ci.org/BILS/SCGLIMS.svg?branch=master   :target: https://travis-ci.org/BILS/SCGLIMS

SCGLIMS is a Single Cell Genomics Lab Information Management System developed
for the `Ettema Lab`_ by `BILS`_. A presentation of the system can be found at
`<http://ino.pm/outreach/presentations/2014/03/lims-presentation/>`_

The database implements the workflow of the Ettema Lab:

.. image:: http://raw.githubusercontent.com/BILS/SCGLIMS/master/docs/images/flowchartlab.png

If your lab has a similar workflow you might be able to use the SCGLIMS as is.
Otherwise an amout of tweaking might be required in which case I would
recommend forking the repository.

.. * Documentation: Not yet available
* GitHub: https://github.com/BILS/SCGLIMS/
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
    python manage.py run test1 --settings=lims_project.settings.local \
    python manage.py runserver 127.0.0.1:8000 --settings=lims_project.settings.local


Contribute
----------

Contributions are greatly appreciated, please read the `contribution instructions`_.

.. _`contribution instructions`: https://github.com/BILS/SCGLIMS/blob/master/CONTRIBUTORS.md
