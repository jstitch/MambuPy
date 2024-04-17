"""MambuGroup entity: a MambuEntity struct for Groups of clients.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import (
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntitySearchable,
    MambuEntityCommentable,
)
from .interfaces import MambuHolder


class MambuGroup(
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntitySearchable,
    MambuEntityCommentable,
    MambuHolder,
):
    """MambuGroup entity"""

    _prefix = "groups"
    """prefix constant for connections to Mambu"""

    _default_tzattrs = {
        "addresses": [{}],
        "groupMembers": [],
    }

    _filter_keys = ["branchId", "centreId", "creditOfficerUsername"]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "groupName",
    ]
    """allowed fields for get_all sorting"""

    _ownerType = "GROUP"
    """owner type of this entity"""

    _vos = [("addresses", "MambuAddress"), ("groupMembers", "MambuGroupMember")]
    """2-tuples of elements and Value Objects"""

    _entities = [
        ("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
        ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
        ("assignedCentreKey", "mambucentre.MambuCentre", "assignedCentre"),
    ]
    """3-tuples of elements and Mambu Entities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}
