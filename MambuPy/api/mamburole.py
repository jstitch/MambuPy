"""MambuRole entity: a MambuEntity struct for User Roles.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import MambuEntity, MambuEntityWritable


class MambuRole(MambuEntity, MambuEntityWritable):
    """MambuRole entity"""

    _prefix = "userroles"
    """prefix constant for connections to Mambu"""
