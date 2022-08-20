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

    def __repr__(self):
        """Prints class and name of role"""
        try:
            return self.__class__.__name__ + " - name: %s" % self._attrs["name"]
        except Exception:
            return super().__repr__()
