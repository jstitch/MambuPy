"""Mambu Value Objects

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .mambustruct import MambuStruct


class MambuValueObject(MambuStruct):
    """A Mambu object with some schema but that you won't interact directly
    with in Mambu web, but through some entity."""


class MambuDocument(MambuValueObject):
    """Attached document"""


class MambuAddress(MambuValueObject):
    """Address"""


class MambuIDDocument(MambuValueObject):
    """ID Document"""
    _ownerType = "ID_DOCUMENT"
    """owner type of this entity"""


class MambuComment(MambuValueObject):
    """Comment"""


class MambuDisbursementDetails(MambuValueObject):
    """Disbursement Details"""


class MambuUserRole(MambuValueObject):
    """User Role"""


class MambuGroupMember(MambuValueObject):
    """Group member"""
    _vos = [("roles", "MambuGroupRole")]
    """2-tuples of elements and Value Objects"""

    _entities = [("clientKey", "mambuclient.MambuClient", "client")]
    """3-tuples of elements and Mambu Entities"""


class MambuGroupRole(MambuValueObject):
    """Group member role"""
