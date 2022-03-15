"""MambuBranch entity: a MambuEntity struct for Branches.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuBranch
"""

from .mambustruct import MambuEntity


class MambuBranch(MambuEntity):
    """MambuBranch entity"""

    _prefix = "branches"
    """prefix constant for connections to Mambu"""

    _filter_keys = [
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "id",
        "name",
    ]
    """allowed fields for get_all sorting"""
