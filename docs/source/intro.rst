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
https://api.mambu.com).

MambuPy includes a set of classes whose purpose is connecting to this
REST API and work with Mambu entities on your python scripts.

You must configure your Mambu account for allowing an API user to
connect with it for this functionality to work.

Look at :doc:`mambu_rest_v2` for the documentation of this way of using
MambuPy.


MambuPy for Database Backup
---------------------------

Mambu also allows their users to download a dump of its database. It
is a MySQL schema, documented at
https://support.mambu.com/docs/mambu-data-dictionary

MambuPy includes in its full flavor a set of SQLAlchemy mappings that
can connect to this Mambu database dump.

You must download a valid dump of your Mambu database, and then
extract and restore on a local MySQL server of your own, and configure
the connection to it for this functionality to work.

Look at :doc:`mambu_orm` for the documentation of this way of using
MambuPy.

Also, for more information, look at the scripts in the
:py:mod:`MambuPy.orm` module.

Work in progress
----------------

MambuPy is a work in progress.

Currently it allows connection to some of the more important Mambu
entitites accessible via its REST API. We are currently working on the
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
