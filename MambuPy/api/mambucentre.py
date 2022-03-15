"""MambuCentre entity: a MambuEntity struct for Centres.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuCentre
"""

from .mambustruct import MambuEntity


class MambuCentre(MambuEntity):
    """MambuCentre entity"""

    _prefix = "centres"
    """prefix constant for connections to Mambu"""

    _filter_keys = [
        "branchId",
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "id",
        "name",
    ]
    """allowed fields for get_all sorting"""
