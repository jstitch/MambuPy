"""MambuUser entity: a MambuEntity struct for Users.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import (MambuEntity, MambuEntityWritable,
                       MambuEntityAttachable,
                       MambuEntityCommentable,
                       MambuPyError)
from .interfaces import MambuOwner


class MambuUser(
        MambuEntity,
        MambuEntityWritable,
        MambuEntityAttachable,
        MambuEntityCommentable,
        MambuOwner
):
    """MambuUser entity"""

    _prefix = "users"
    """prefix constant for connections to Mambu"""

    _filter_keys = [
        "branchId",
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
    ]
    """allowed fields for get_all sorting"""

    _ownerType = "USER"
    """owner type of this entity"""

    _vos = [("role", "MambuUserRole")]
    """2-tuples of elements and Value Objects"""

    _entities = [
        ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch")]
    """3-tuples of elements and Mambu Entities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}

    @classmethod
    def get_all(
        cls,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None,
        branchIdType=None,
    ):
        """get_all, several entities, filtering allowed

        Args:
          filters (dict): key-value filters, dependes on each entity
                          (keys must be one of the _filter_keys)
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
          sortBy (str): ``field1:ASC,field2:DESC``, sorting criteria for
                        results (fields must be one of the _sortBy_fields)
          branchIdType (str ASSIGNED/MANAGE): search assigned users or also
                       those who can manage a branch

        Returns:
          list of instances of an entity with data from Mambu
        """
        if branchIdType and (not filters or "branchId" not in filters):
            raise MambuPyError("branchIdType not allowed if branchId not provided")
        if branchIdType and branchIdType not in ["ASSIGNED", "MANAGE"]:
            raise MambuPyError("Invalid branchIdType: {}".format(branchIdType))

        params = {}
        if branchIdType:
            params["branchIdType"] = branchIdType

        return super().get_all(
            filters,
            offset, limit,
            paginationDetails, detailsLevel,
            sortBy,
            **params)
