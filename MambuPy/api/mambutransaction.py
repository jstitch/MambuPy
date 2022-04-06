"""MambuTransaction entity: a MambuEntity struct for credit Transactions.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import (MambuEntity, MambuEntitySearchable)


class MambuTransaction(
    MambuEntity,
    MambuEntitySearchable
):
    """MambuTransaction entity"""

    _prefix = "loans/transactions"
    """prefix constant for connections to Mambu"""

    _filter_keys = [
    ]
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
    ]
    """allowed fields for get_all sorting"""

    @classmethod
    def get_all(
        cls,
        loanAccountId,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC"
    ):
        """get_all, several transactions, filtering allowed

        Args:
          loanAccountId (str): the id or encodedkey of the loan account
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not

        Returns:
          list of instances of a transaction with data from Mambu
        """
        return super().get_all(
            filters=None,
            offset=offset, limit=limit,
            paginationDetails=paginationDetails, detailsLevel=detailsLevel,
            sortBy=None,
            **{"prefix": "loans/{}/transactions".format(loanAccountId)})
