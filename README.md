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

### Author

JNC
jstitch@gmail.com
