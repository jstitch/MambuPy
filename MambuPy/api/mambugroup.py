"""MambuGroup entity: a MambuEntity struct for Groups of clients.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .mambustruct import (MambuEntity, MambuEntityAttachable,
                          MambuEntitySearchable)


class MambuGroup(MambuEntity, MambuEntityAttachable, MambuEntitySearchable):
    """MambuGroup entity"""

    _prefix = "groups"
    """prefix constant for connections to Mambu"""

    _filter_keys = ["branchId", "centreId", "creditOfficerUsername"]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "groupName",
    ]
    """allowed fields for get_all sorting"""

    _ownerType = "GROUP"
    """attachments owner type of this entity"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}
