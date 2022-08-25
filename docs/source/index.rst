.. MambuPy documentation master file, created by
   sphinx-quickstart on Mon Jul 16 14:04:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MambuPy Docs!
=============

A python API for using Mambu.
-----------------------------

Allows accessing Mambu programatically.

Either using Mambu's REST API, or from within a Mambu's database
backup.

Mambu is a cloud platform which lets you rapidly build, integrate,
launch and service any lending portfolio into any market
(https://www.mambu.com).


MambuPy for REST API
--------------------

Mambu allows communicating via a RESTful API (documented at
https://support.mambu.com/docs/developer).

MambuPy includes a set of classes whose purpose is connecting to this
REST API and work with Mambu entities on your python scripts.

You must configure your Mambu account for allowing an API user to
connect with it for this functionality to work.

Look at :doc:`mambu_rest` for the documentation of this way of using
MambuPy.

Also, for more information, look at the MambuStruct class and all the
classes inheriting from it. MambuPy implements this at the
:py:mod:`MambuPy.rest` module.

MambuPy for Database Backup
---------------------------

Mambu also allows their users to download a dump of its database. It
is a MySQL schema, documented at
https://support.mambu.com/docs/mambu-data-dictionary

MambuPy includes a set of SQLAlchemy mappings that can connect to
this Mambu database dump.

You must download a valid dump of your Mambu database, and then
extract and restore on a local MySQL server of your own, and configure
the connection to it for this functionality to work.

Look at :doc:`mambu_orm` for the documentation of this way of using
MambuPy.

Also, for more information, look at the scripts in the
:py:mod:`MambuPy.orm` module.

Installation
------------

Currently MambuPy works on Python 2.7 and Python >3.7

You may install MambuPy by git-cloning this repository on your local
environment and making it available anywhere on your ``PYTHONPATH``.

You may also use ``pip install mambupy`` but please consider that you
must configure your installation before using it.

Configuration
-------------

You must configure your local MambuPy environment first so you can
correctly use this module.

Look at :py:mod:`MambuPy.mambuconfig` for more information.

Work in progress
----------------

MambuPy is a work in progress.

Currently it allows connection to some of the more important Mambu
entitites accessible via its REST API. We are also working on th
:doc:`mambu_rest_v2` that supports Mambu REST API v2.

On the ORM side, not all of the Mambu Database schemas are currently
mapped.

Finally, also note that Mambu itself delivers changes on a regular
basis that may include new functionality on its REST API, and changes
on its database tables. Currently MambuPy works with the last version
of Mambu but NOT ALL of its functionality is implemented. Making a
complete implementation of the REST API and the mapping of the
Database, and keeping them up to date with the latest version of
Mambu, is one of the main objectives of the MambuPy project.

Please consider supporting the project by forking, improving and
pull-requesting it.

TODOs
-----

TODO comments for hackers are included at:

* pydoc strings all around the code

Author
------

JNC
jstitch@gmail.com


Table of Contents
-----------------

.. toctree::
   :maxdepth: 3

   mambu_rest
   mambu_rest_v2
   mambu_orm
   mambupy
   CHANGELOG
   LICENSE


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
