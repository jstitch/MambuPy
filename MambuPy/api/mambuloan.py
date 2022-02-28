"""MambuLoan entity: a MambuEntity struct for credit Loans.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuLoan
"""

from MambuPy.mambuutil import MambuPyError
from .mambustruct import (
    MambuEntity,
    MambuEntityAttachable,
    MambuEntitySearchable,
    )


class MambuLoan(
    MambuEntity,
    MambuEntityAttachable,
    MambuEntitySearchable
    ):
    """MambuLoan entity"""

    _prefix = "loans"
    """prefix constant for connections to Mambu"""

    _filter_keys = [
        "branchId",
        "centreId",
        "accountState",
        "accountHolderType",
        "accountHolderId"]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "id",
        "loanName",
        ]
    """allowed fields for get_all sorting"""

    _ownerType = "LOAN_ACCOUNT"
    """attachments owner type of this entity"""

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
        sortBy=None
    ):
        """get_all, several MambuLoans, filtering allowed

        This child method pre-validates data, then calls the super version for
        actual get_all functionality.

        Args:
          filters (dict) - key-value filters
                                         (keys must be one of the _filter_keys)
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not
          sortBy (str field:ASC,field2:DESC) - sorting criteria for results
                                     (fields must be one of the _sortBy_fields)

        Returns:
          list of instances of a MambuLoan with data from Mambu
        """
        if filters and isinstance(filters, dict):
            for filter_k in filters.keys():
                if filter_k not in cls._filter_keys:
                    raise MambuPyError(
                        "key {} not in allowed _filterkeys: {}".format(
                            filter_k, cls._filter_keys))

        if sortBy and isinstance(sortBy, str):
            for sort in sortBy.split(","):
                for num, part in enumerate(sort.split(":")):
                    if num == 0 and part not in cls._sortBy_fields:
                        raise MambuPyError(
                            "field {} not in allowed _sortBy_fields: {}".format(
                                part, cls._sortBy_fields))

        return super().get_all(
            filters, offset, limit, paginationDetails, detailsLevel, sortBy)
