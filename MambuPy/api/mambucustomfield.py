"""MambuCustomField entity: a MambuEntity struct for Custom Fields.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import MambuEntity


class MambuCustomField(MambuEntity):
    """MambuCustomField entity"""

    _prefix = "customfields"
    """prefix constant for connections to Mambu"""
