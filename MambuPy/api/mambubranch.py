"""MambuBranch entity: a MambuEntity struct for Branches.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import MambuEntity, MambuEntityCommentable
from .interfaces import MambuOwner


class MambuBranch(MambuEntity, MambuEntityCommentable, MambuOwner):
    """MambuBranch entity"""

    _prefix = "branches"
    """prefix constant for connections to Mambu"""

    _filter_keys = []
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "id",
        "name",
    ]
    """allowed fields for get_all sorting"""

    _ownerType = "BRANCH"
    """owner type of this entity"""

    _vos = [("addresses", "MambuAddress")]
    """2-tuples of elements and Value Objects"""
