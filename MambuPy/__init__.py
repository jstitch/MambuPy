"""*MambuPy*, an API library to access `Mambu <https://www.mambu.com/>`_ objects.

.. autosummary::
   :toctree: _autosummary

    MambuPy.mambuconfig
    MambuPy.mambuutil
    MambuPy.rest
    MambuPy.orm
    MambuPy.api
    MambuPy.api.connector
    MambuPy.rest1to2


Currently, there are two different ways to access Mambu objects:

1) Objects using `Mambu REST API
   <https://developer.mambu.com/customer/en/portal/articles/1162276-rest-apis-overview/>`_
   , they live at the :any:`MambuPy.rest` package

2) An ORM using a `DB backup retrieved from Mambu
   <https://support.mambu.com/docs/mambu-data-dictionary>`_
   , they live at the :any:`MambuPy.orm` package

.. note::

   The `Mambu Developers Center site <https://developer.mambu.com/>`_ holds the
   current documentation for the latest version of Mambu. *MambuPy* will try to
   keep up with what Mambu updates according to such information.

TODOS
=====

.. todo:: Unit testing of some modules is currently very basic. The purpose is
          to achive TDD when implementing features or correcting bugs.
"""

__version__ = "2.0.0b42"
"""The version of this module."""
