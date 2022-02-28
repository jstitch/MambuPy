"""Mambu Value Objects

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuValueObject
   MambuDocument
"""

from .classes import MambuMapObj


class MambuValueObject(MambuMapObj):
    """A Mambu object with some schema but that you won't interact directly
    with in Mambu web, but through some entity."""


class MambuDocument(MambuValueObject):
    """Attached document"""
