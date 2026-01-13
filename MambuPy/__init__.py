"""*MambuPy*, an API library to access `Mambu <https://www.mambu.com/>`_ objects.

.. autosummary::
   :toctree: _autosummary

    MambuPy.mambuconfig
    MambuPy.mambuutil
    MambuPy.api
    MambuPy.api.connector
    MambuPy.orm


Currently, there are two different ways to access Mambu objects:

1) Objects using `Mambu REST API
   <https://developer.mambu.com/customer/en/portal/articles/1162276-rest-apis-overview/>`_
   , they live at the :any:`MambuPy.api` package

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

import sys
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location

__version__ = "2.1.1"
"""The version of this module."""


class CaseInsensitiveFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.lower() == "mambupy":
            # Get the actual module file location
            return spec_from_file_location(fullname, __file__)
        return None


# Register the finder
sys.meta_path.insert(0, CaseInsensitiveFinder())
