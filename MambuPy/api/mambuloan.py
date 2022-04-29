"""MambuLoan entity: a MambuEntity struct for credit Loans.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy
import json

from .entities import (MambuEntity, MambuEntityWritable,
                       MambuEntityAttachable,
                       MambuEntitySearchable,
                       MambuInstallment)


class MambuLoan(
    MambuEntity,
    MambuEntityWritable,
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
        "accountHolderId",
    ]
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

    _vos = [("disbursementDetails", "MambuDisbursementDetails")]
    """2-tuples of elements and Value Objects"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}

    def get_schedule(self):
        """Retrieves the installments schedule."""
        resp = self._connector.mambu_loanaccount_getSchedule(self.id)

        installments = json.loads(resp.decode())["installments"]

        self.schedule = []
        for installment in installments:
            installment_entity = MambuInstallment(**installment)
            installment_entity._tzattrs = copy.deepcopy(installment)
            installment_entity._convertDict2Attrs()
            self.schedule.append(installment_entity)
