""" MambuPy's ORM package.

A `SQLAlchemy <http://www.sqlalchemy.org/>`_ ORM using a `DB backup retrieved from Mambu
<https://support.mambu.com/docs/mambu-data-dictionary>`_

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


Lives under the :py:mod:`MambuPy.orm` package

.. todo:: Implement a lot of lacking fields on the currently available tables.
.. todo:: Implement a lot of lacking tables from the Mambu DB schema.
"""

from .. import mambuconfig, mambuutil
