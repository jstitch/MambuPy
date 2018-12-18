"""*MambuPy*, an API library to access `Mambu <https://www.mambu.com/>`_ objects.

.. autosummary::
   :toctree: _autosummary

    MambuPy.mambuconfig
    MambuPy.mambuutil
    MambuPy.rest
    MambuPy.orm


Currently, there are two different ways to access Mambu objects:

1) Objects using `Mambu REST API
   <https://developer.mambu.com/customer/en/portal/articles/1162276-rest-apis-overview/>`_
   , they live at the :any:`MambuPy.rest` package

2) An ORM using a `DB backup retrieved from Mambu
   <https://developer.mambu.com/customer/en/portal/articles/1162274-data-dictionary-and-api-standards>`_
   , they live at the :any:`MambuPy.orm` package

.. note::

   The `Mambu Developers Center site <https://developer.mambu.com/>`_ holds the
   current documentation for the latest version of Mambu. *MambuPy* will try to
   keep up with what Mambu updates according to such information.

TODOS
=====

.. todo:: Unit testing is currently very basic. The purpose is to achive TDD
          when implementing features or correcting bugs.
.. todo:: Please also read the :any:`TODO` file for more suggestions
"""

__version__ = "1.1.1"
"""The version of this module."""
