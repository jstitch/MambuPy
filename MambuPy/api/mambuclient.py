"""MambuClient entity: a MambuEntity struct for Clients.

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


class MambuClient(
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntitySearchable,
    MambuEntityCommentable,
    MambuHolder,
):
    """MambuClient entity"""

    _prefix = "clients"
    """prefix constant for connections to Mambu"""

    _default_tzattrs = {
        "birthDate": None,
        "groupKeys": [None],
        "addresses": [{}],
        "idDocuments": [{}],
    }

    _filter_keys = [
        "branchId",
        "centreId",
        "creditOfficerUsername",
        "firstName",
        "lastName",
        "idNumber",
        "state",
        "birthDate",
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "firstName",
        "lastName",
    ]
    """allowed fields for get_all sorting"""

    _ownerType = "CLIENT"
    """owner type of this entity"""

    _vos = [("addresses", "MambuAddress"), ("idDocuments", "MambuIDDocument")]
    """2-tuples of elements and Value Objects"""

    _entities = [
        ("groupKeys", "mambugroup.MambuGroup", "groups"),
        ("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
        ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
        ("assignedCentreKey", "mambucentre.MambuCentre", "assignedCentre"),
    ]
    """3-tuples of elements and Mambu Entities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}

    def _delete_for_creation(self):
        """Deletes extra fields from Mambu unusable for entity
        creation."""
        try:
            del self._attrs["approvedDate"]
        except KeyError:
            pass
