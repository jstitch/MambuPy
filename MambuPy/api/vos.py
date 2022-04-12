"""Mambu Value Objects

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .mambustruct import MambuStruct


class MambuValueObject(MambuStruct):
    """A Mambu object with some schema but that you won't interact directly
    with in Mambu web, but through some entity."""


class MambuDocument(MambuValueObject):
    """Attached document"""


class MambuAddress(MambuValueObject):
    """Address"""


class MambuIDDocument(MambuValueObject):
    """ID Document"""
