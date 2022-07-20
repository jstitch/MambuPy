"""MambuCentre entity: a MambuEntity struct for Centres.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import MambuEntity
from .interfaces import MambuOwner, MambuCommentable


class MambuCentre(MambuEntity, MambuCommentable, MambuOwner):
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

    _ownerType = "CENTRE"
    """owner type of this entity"""

    _vos = [("addresses", "MambuAddress")]
    """2-tuples of elements and Value Objects"""
