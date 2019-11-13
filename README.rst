=============
ckanext-solr-sqs
=============

CKAN Extension to synchronize SOLR indices between multiple CKAN instances
sharing same database using AWS SQS.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-solr-sqs:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-solr-sqs Python package into your virtual environment::

     pip install ckanext-solr-sqs

3. Add ``solr-sqs`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    ckanext.solr-sqs.some_setting = some_default_value


------------------------
Development Installation
------------------------

To install ckanext-solr-sqs for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/open-data-toronto/ckanext-solr-sqs.git
    cd ckanext-solr-sqs
    python setup.py develop
    pip install -r dev-requirements.txt
