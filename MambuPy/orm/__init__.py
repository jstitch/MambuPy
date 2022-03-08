""" MambuPy's ORM package.

A `SQLAlchemy <http://www.sqlalchemy.org/>`_ ORM using a `DB backup retrieved from Mambu
<https://developer.mambu.com/customer/en/portal/articles/1162274-data-dictionary-and-api-standards>`_

.. autosummary::
   :toctree: _autosummary

    MambuPy.orm.schema_orm
    MambuPy.orm.schema_mambu
    MambuPy.orm.schema_clients
    MambuPy.orm.schema_groups
    MambuPy.orm.schema_loans
    MambuPy.orm.schema_users
    MambuPy.orm.schema_branches
    MambuPy.orm.schema_addresses
    MambuPy.orm.schema_activities
    MambuPy.orm.schema_customfields
    MambuPy.orm.schema_dummies


Lives under the :any:`MambuPy.orm` package

All schema modules must import :any:`schema_orm`, this module holds basic
`SQLAlchemy <http://www.sqlalchemy.org/>`_ global variables, such as the
:py:func:`Base <sqlalchemy.ext.declarative.declarative_base>` for all tables
(which needs to be the same one for everyone), or a default :py:class:`session
<sqlalchemy.orm.session.Session>`, created by importing any of this modules. If
you need to import all schemas at once, just import :any:`schema_mambu`, which
should hold them all. If, on the other hand, you want to use a specific schema
module, just be careful when dependencies happen, for example if you use
:any:`schema_groups` to get :any:`groups <schema_groups.Group>`, a group can
have :any:`loans <schema_loans.LoanAccount>`, but, to get them you need to
import :any:`schema_loans` too.

You can think of the schema modules structured as follows:

..
 schema_orm  (holds an engine connection, the Base for all tables, and the default session)
           /           /          |           \\
       schema_loans  schema_clients  schema_groups ...
             (holds the ORM for each table)
           \           \          |           /
    schema_mambu (utility module to import *everything*)

.. image:: /_static/schemas_mambupy_diagram.png

.. todo:: Implement a lot of lacking fields on the currently available tables.
.. todo:: Implement a lot of lacking tables from the Mambu DB schema.
"""

from .. import mambuconfig, mambuutil
