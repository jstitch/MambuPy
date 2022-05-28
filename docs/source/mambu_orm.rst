.. _mambu_orm:

MambuPy for ORM
===============

ORM module of MambuPy implements communication with a Mambu database
backup living at some server of your choice. Mambu lets you download
its database schema, an MySQL database you can restore anywhere you
want.

MambuPy ORM uses `SQLAlchemy mappings
<https://www.sqlalchemy.org/>`_. The Data Dictionary of Mambu database
can be consulted here.

As all modules in MambuPy, ORM module must be configured with a
read-only connection to a Mambu database backup.

How MambuPy ORM module works
----------------------------

Since all the module consists of SQLAlchemy mappings, you basically
use it creating `SQLAlchemy's queries
<https://docs.sqlalchemy.org/en/14/orm/query.html>`_.

You may import each of :py:mod:`MambuPy.orm`'s modules, but also for
convienience, there is :py:mod:`MambuPy.orm.schema_mambu` which in
itself imports everything inside the other modules. This means every
ORM mapping inside them.

All schema modules must import :py:mod:`MambuPy.orm.schema_orm`, this
module holds basic `SQLAlchemy <http://www.sqlalchemy.org/>`_ global
variables, such as the `Base
<https://docs.sqlalchemy.org/en/14/orm/mapping_api.html?highlight=base#sqlalchemy.orm.declarative_base>`_
for all tables (which needs to be the same one for everyone), or a
default :py:class:`session <sqlalchemy.orm.session.Session>`, created
by importing any of this modules. If you need to import all schemas at
once, just import :py:mod:`MambuPy.orm.schema_mambu`, which should
hold them all. If, on the other hand, you want to use a specific
schema module, just be careful when dependencies happen, for example
if you use :py:mod:`MambuPy.orm.schema_groups` to get :py:mod:`groups
<MambuPy.orm.schema_groups.Group>`, a group can have :py:mod:`loans
<MambuPy.orm.schema_loans.LoanAccount>`, but, to get them you need to
import :py:mod:`MambuPy.orm.schema_loans` too.

You can think of the schema modules structured as follows:

..
 schema_orm  (holds an engine connection, the Base for all tables, and the default session)
           /           /          |           \\
       schema_loans  schema_clients  schema_groups ...
             (holds the ORM for each table)
           \           \          |           /
    schema_mambu (utility module to import *everything*)

.. image:: /_static/schemas_mambupy_diagram.png

Configuration
+++++++++++++

As you may read at :py:mod:`MambuPy.mambuconfig`, ORM configuration
consists of the following options:

* :py:obj:`MambuPy.mambuconfig.dbname` - the name of the database holding the Mambu DB backup
* :py:obj:`MambuPy.mambuconfig.dbuser` - the username with read permissions to ``dbname``
* :py:obj:`MambuPy.mambuconfig.dbpwd` - the password of the user
* :py:obj:`MambuPy.mambuconfig.dbhost` - the host to access the DB
* :py:obj:`MambuPy.mambuconfig.dbport` - the port for connecting to the host
* :py:obj:`MambuPy.mambuconfig.dbeng` - the DB engine, MySQL by default

As :py:mod:`MambuPy.mambuconfig` documentation tells, you can set
these on ``/etc/mambupyrc``, ``$HOME/.mambupy.rc``, on an `ini-format
<https://en.wikipedia.org/wiki/INI_file>`_ style. Home directory RC
file overrides what ``/etc`` file says.

You can also set the environment variables: ``MAMBUPY_DBNAME``,
``MAMBUPY_DBUSER``, ``MAMBUPY_DBPWD``, ``MAMBUPY_DBHOST``,
``MAMBUPY_DBPORT`` and ``MAMBUPY_DBENG``, which override what RC files
say.

Examples
--------

API Docs
--------
