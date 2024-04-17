"""MambuCustomField entity: a MambuEntity struct for Custom Fields.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import MambuEntity
from MambuPy.mambuutil import MambuPyError


class MambuCustomField(MambuEntity):
    """MambuCustomField entity"""

    _prefix = "customfields"
    """prefix constant for connections to Mambu"""


class MambuCustomFieldSet(MambuEntity):
    """MambuCustomFieldSet entity"""

    _prefix = "customfieldsets"
    """prefix constant for connections to Mambu"""

    _availableFor = [
        "CLIENT",
        "GROUP",
        "CREDIT_ARRANGEMENT",
        "LOAN_ACCOUNT",
        "GUARANTOR",
        "ASSET",
        "DEPOSIT_ACCOUNT",
        "DEPOSIT_PRODUCT",
        "TRANSACTION_CHANNEL",
        "TRANSACTION_TYPE",
        "BRANCH",
        "CENTRE",
        "USER",
    ]
    """for which entites does a Set may be available for"""

    @classmethod
    def get_all(cls, *args, **kwargs):
        """get_all, customfieldsets, filtering allowed

        Args:
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
          kwargs (dict): extra parameters that a customfieldset may receive in
                         its get_all method. May include a user, pwd and url to
                         connect to Mambu.
        Returns:
          list of instances of a customfieldset with data from Mambu
        """
        if "filters" in kwargs:
            raise MambuPyError("filters is not allowed on MambuCustomFieldSet")
        if "sortBy" in kwargs:
            raise MambuPyError("sortBy is not allowed on MambuCustomFieldSet")
        if (
            "availableFor" in kwargs
            and kwargs["availableFor"]
            and kwargs["availableFor"] not in cls._availableFor
        ):
            raise MambuPyError(
                "key {} not in allowed _availableFor: {}".format(
                    kwargs["availableFor"], cls._availableFor
                )
            )

        return super().get_all(*args, **kwargs)
