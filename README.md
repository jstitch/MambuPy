[![Build Status](https://travis-ci.org/jstitch/MambuPy.svg?branch=master)](https://travis-ci.org/jstitch/MambuPy)
# MambuPy

## A python API for using Mambu.

Allows accessing Mambu via its REST API. Also includes SQLAlchemy
mappings to a backup of its DataBase.

Mambu is a cloud platform which lets you rapidly build, integrate,
launch and service any lending portfolio into any market
(https://www.mambu.com).


### Mambu REST API

Mambu allows communicating via a RESTful API (documented at
https://developer.mambu.com/).

MambuPy includes a set of classes whose purpose is connecting to this
REST Api and work with Mambu entities on your python scripts.

You must configure your Mambu account for allowing an API user to
connect with it for this functionality to work.

For more information, look at the MambuStruct class and all the
classes inheriting from it. MambuPy implements this at all the scripts
named ``mambu*.py``

### Mambu Database Backup

Mambu also allows their users to download a dump of its database. It
is a MySQL schema, documented at https://developer.mambu.com.

MambuPy includes a set of SQLAlchemy mappings that can connect to
the Mambu database dump.

You must download a valid dump of your Mambu database, and then
extract and restore on a local MySQL server of your own for this
functionality to work.

For more information, look at the scripts named ``schema*.py``

### Installation

Currently MambuPy works on Python 2.7 and Python 3.6

You may install MambuPy by git-cloning this repository on your local
environment and making it available anywhere on your ``PYTHONPATH``.

You may also use ``pip install mambupy`` but please consider that you
must configure your installation before using it.

### Configuration

You must configure your local MambuPy environment first so you can
correctly use this module.

Look at ``mambuconfig.py`` for more information.

### Work in progress

MambuPy is a work in progress, on a very early stage of its
development.

Currently it allows a limited connection to some of the more important
Mambu entitites accessible via its REST API.

Also, not all of the Mambu Database schema is currently mapped.

Finally, also note that Mambu itself delivers changes on a regular
basis that may include new functionality on its REST API, and changes
on its database tables. Currently MambuPy works with the last version
of Mambu but NOT ALL of its functionality is implemented. Making a
complete implementation of the REST API and the mapping of the
Database, and keeping them up to date with the last version of Mambu,
is one of the main objectives of the MambuPy project.

Please consider supporting the project by forking, improving and
pull-requesting it.

#### TODOs

TODO comments for hackers are included at:

* TODO file
* pydoc string at ``__init__.py``
* pydoc strings all around the code

#### Release Notes
* v0.8 first release notes 2018-04-20
  - implementation of PATCH request method on MambuStruct
  - implementation of MambuTask entity and MambuTasks iterable
  - v0.8.1 and v0.8.2 are identical to v0.8.1
* v0.8.3 2018-05-22
  - MambuStruct convertDict2Attrs constantFields added 'email'
  - mambuuser unittests
  - mamburoles module
  - MambuUser setRoles() method
  - MambuTask close() method
* v0.8.4 2018-07-18
  - Sphinx documentation and ReadTheDocs site
* v0.9.0 2018-08-06
  - reallocation of modules in packages according to functionality
* v1.0.0 2018-08-31
  - support for Python 3 ready!
* v1.1.0 2018-12-16
  - config parsers for a better configuration of MambuPy
* v1.1.1 2018-12-17
  - argparse to override configuration of MambuPy from command line
* v1.2.0 2019-01-21
  - MambuStruct now holds a copy of the args and kwargs originally
    passed to the constructor, so they may be reused on future calls
    of connect() method
* v1.2.1 2019-02-18
  - MambuStruct catches correctly requests errors and throws
    MambuCommError only on that cases. Any other exception is
    re-raised again.
* v1.2.2 2019-02-19
  - gettasksurl now support limit and offset params
* v1.3.0 2019-03-06
  - orm schema_tasks script added.
  - rest added properties to each Mambmu entity to support
    instantiation of attributes with a default related-entity class,
    allowing overriding this with your own related-entity classes.
* v1.3.1 2019-03-15
  - bugfix on MambuStruct.__init__, urlfunc parameter should be
    treated almost at the end
* v1.3.2 2019-03-27
  - get method for dict-like MambuStructs
* v1.3.3 2019-05-01
  - AllMambuProducts singleton py3 compatibility
* v1.3.4 2019-05-16
  - add support for DELETE method on MambuStruct connect()
* v1.3.5 2019-05-28
  - add Mambu Savings related entities (unit test still TODO)
* v1.3.6 2019-06-11
  - MambuStruct convertDict2Attrs constantFields added 'description'
* v1.3.7 2019-07-30
  - Auth paramos for backup_db func were incorrectly set
* v1.3.8 2019-08-26
  - change import builtins for unicode to a more generic way of
    importing it
* v1.3.9 2019-10-30
  - MambuGroup support one address via preprocess
* v1.3.10 2019-12-09
  - MambuStruct support to update info via PATCH and POST
* v1.3.11 2019-12-10
  - MambuGroups support to create Group entities in Mambu
* v1.3.12 2019-12-11
  - MamguGroups support to update Group entities in Mambu
* v1.3.13 2019-12-13
  - MambuClient support to update Client entities in Mambu
* v1.3.14 2020-01-09
  - MambuGroup method addMembers
* v1.3.14b 2020-01-09
  - MambuGroup method addMembers update MambuGroup once members are added
* v1.3.15 2020-01-24
  - mambuutil.backup_db GET call to Mambu needs application/json headers
* v1.4 2020-01-30
  - ORM gets Centre table
* v1.5 2020-02-20
  - URL function for loan accounts' custom information
* v1.6 2020-02-24
  - setHolder getRoles=True instantiates Clients with fullDetails=True
* v1.7 2020-03-05
  - Accept Headers for all requests, using v1 API Accept Header
* v1.7.1 2020-04-03
  - Update method comes from parent class MambuStruct, it connects to
    Mambu to refresh info of updated data in the internal structures
    of MambuPy
* v1.8 2020-05-04
  - Implement __contains__ in MambuStruct so that you can use in operator
* v1.8.1 2020-05-11
  - init method tries to initialize the entid property
* v1.8.2 2020-07-03
  - Use of items() instead of iteritems in dictionaries
  - Atribute rescheduledAccountKey was added to orm LoanAccount
  - gitlab CI coverage tests
* v1.8.3 2020-09-05
  - Classes CustomFieldSet and CustomFieldSelection were added for ORM
  - New setBranch method MambuUser

### Author

JNC
jstitch@gmail.com
