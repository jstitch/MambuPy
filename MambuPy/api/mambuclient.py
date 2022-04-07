"""MambuClient entity: a MambuEntity struct for Clients.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import (MambuEntity, MambuEntityWritable,
                       MambuEntityAttachable,
                       MambuEntitySearchable)


class MambuClient(
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntitySearchable
):
    """MambuClient entity"""

    _prefix = "clients"
    """prefix constant for connections to Mambu"""

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
    """attachments owner type of this entity"""

    _vos = [("addresses", "MambuAddress")]
    """2-tuples of elements and Value Objects"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}
