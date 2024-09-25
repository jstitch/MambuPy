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


class MambuDisbursementLoanTransactionInput(MambuValueObject):
    """Disbursment Loan Transaction body"""

    _schema_fields = [
        "amount",
        "bookingDate",
        "externalId",
        "firstRepaymentDate",
        "notes",
        "originalCurrencyCode",
        "shiftAdjustableInterestPeriods",
        "valueDate",
    ]
    """List of schema fields for a loan disbursement transaction."""


class MambuRepaymentLoanTransactionInput(MambuValueObject):
    """Repayment Loan Transaction body"""

    _schema_fields = [
        "amount",
        "bookingDate",
        "externalId",
        "installmentEncodedKey",
        "notes",
        "originalCurrencyCode",
        "prepaymentRecalculationMethod",
        "valueDate",
        "transactionDetails",
    ]
    """List of schema fields for a loan repayment transaction."""


class MambuLoanTransactionDetailsInput(MambuValueObject):
    """Loan Transaction Details body"""

    _schema_fields = [
        "transactionChannelId",
        "transactionChannelKey",
    ]
    """List of schema fields for a loan repayment transaction."""


class MambuFeeLoanTransactionInput(MambuValueObject):
    """Repayment Loan Transaction body"""

    _schema_fields = [
        "amount",
        "bookingDate",
        "externalId",
        "fisrtRepaymentDate",
        "installmentNumber",
        "notes",
        "predefinedFeeKey",
        "valueDate",
    ]
    """List of schema fields for a loan fee transaction."""
