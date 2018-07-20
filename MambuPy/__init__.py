"""*MambuPy*, an API library to access `Mambu <https://www.mambu.com/>`_ objects.

.. autosummary::
   :toctree: _autosummary

    MambuPy.mambustruct
    MambuPy.mambuclient
    MambuPy.mambugroup
    MambuPy.mambuloan
    MambuPy.mamburepayment
    MambuPy.mambutransaction
    MambuPy.mambuproduct
    MambuPy.mambubranch
    MambuPy.mambucentre
    MambuPy.mambuactivity
    MambuPy.mambutask
    MambuPy.mambuuser
    MambuPy.mamburoles
    MambuPy.mambuconfig
    MambuPy.mambuutil
    MambuPy.schema_orm
    MambuPy.schema_mambu
    MambuPy.schema_clients
    MambuPy.schema_groups
    MambuPy.schema_loans
    MambuPy.schema_users
    MambuPy.schema_branches
    MambuPy.schema_addresses
    MambuPy.schema_activities
    MambuPy.schema_customfields
    MambuPy.schema_dummies


Currently, there are two different ways to access Mambu objects:

1) Objects using `Mambu REST API
   <https://developer.mambu.com/customer/en/portal/articles/1162276-rest-apis-overview/>`_
2) An ORM using a `DB backup retrieved from Mambu
   <https://developer.mambu.com/customer/en/portal/articles/1162274-data-dictionary-and-api-standards>`_

.. note::

   The `Mambu Developers Center site <https://developer.mambu.com/>`_ holds the
   current documentation for the latest version of Mambu. *MambuPy* will try to
   keep up with what Mambu updates according to such information.

REST API
========

The REST API way is the currently most developed code on *MambuPy*.

It has a lot of objects which model some Mambu entity.

Every object inherits from the parent :any:`mambustruct.MambuStruct`
class. Start at the documentation there for more info on how it works.

.. todo:: Implement objects to make POST requests. The suggestion may be to use
          MambuStruct, to default the __init__ to make a POST request (via the data
          argument) and the attrs attribute to store the elements of the response that
          Mambu gives when a successful POST is achieved.
.. todo:: Implement a lot of other Mambu entities available through GET requests on
          Mambu.
.. todo:: Implement a lot of lacking GET filters on the currently available Mambu
          objects, inside the urlfuncs on the mambuutil module.
.. todo:: A lot of TODO comments are inserted inside the pydocs of the code
          itself. Please read them for suggestions on work need to be done.

DB ORM
======

On the DB way all schema modules must import :any:`schema_orm`, this module
holds basic `SQLAlchemy <http://www.sqlalchemy.org/>`_ global variables, such
as the :py:func:`Base <sqlalchemy.ext.declarative.declarative_base>` for all
tables (which needs to be the same one for everyone), or a default
:py:class:`session <sqlalchemy.orm.session.Session>`, created by importing any
of this modules. If you need to import all schemas at once, just import
:any:`schema_mambu`, which should hold them all. If, on the other hand, you
want to use a specific schema module, just be careful when dependencies happen,
for example if you use :any:`schema_groups` to get :any:`groups
<schema_groups.Group>`, a group can have :any:`loans
<schema_loans.LoanAccount>`, but, to get them you need to import
:any:`schema_loans` too.

You can think of the schema modules structured as follows:

..
 schema_orm  (holds an engine connection, the Base for all tables, and the default session)
           /           /          |           \\
       schema_loans  schema_clients  schema_groups ...
             (holds the ORM for each table)
           \           \          |           /
    schema_mambu (utility module to import *everything*)

.. image:: static/schemas_mambupy_diagram.png

.. todo:: Implement a lot of lacking fields on the currently available tables.
.. todo:: Implement a lot of lacking tables from the Mambu DB schema.

TODOS
=====

.. todo:: Unit testing is currently very basic.
.. todo:: The purpose is to achive TDD when implementing features or correcting
          bugs.
.. todo:: Please also read the TODO file for more suggestions
"""

__version__ = "0.8.4"
"""The version of this module."""
