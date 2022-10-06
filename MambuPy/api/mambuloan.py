"""MambuLoan entity: a MambuEntity struct for credit Loans.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import copy
import datetime
import json

from .entities import (MambuEntity, MambuEntityWritable,
                       MambuEntityAttachable,
                       MambuEntitySearchable,
                       MambuEntityCommentable,
                       MambuEntityOwnable,
                       MambuInstallment)
from MambuPy.api.vos import MambuDisbursementLoanTransactionInput
from MambuPy.mambuutil import MambuPyError


class MambuLoan(
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntityCommentable,
    MambuEntityOwnable,
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
        "creditOfficerUsername",
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
    """owner type of this entity"""

    _vos = [("disbursementDetails", "MambuDisbursementDetails")]
    """2-tuples of elements and Value Objects"""

    _entities = [
        ("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
        ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
        ("assignedCentreKey", "mambucentre.MambuCentre", "assignedCentre"),
        ("productTypeKey", "mambuproduct.MambuProduct", "productType"),
        ("originalAccountKey", "mambuloan.MambuLoan", "originalAccount"),
        ("accountHolderKey", "", "accountHolder")]
    """3-tuples of elements and Mambu Entities"""

    _accepted_actions = [
        "REQUEST_APPROVAL",
        "SET_INCOMPLETE",
        "APPROVE",
        "UNDO_APPROVE",
        "REJECT",
        "WITHDRAW",
        "CLOSE",
        "UNDO_REJECT",
        "UNDO_WITHDRAW",
        "UNDO_CLOSE",
    ]
    """accepted actions to change"""

    def __init__(self, **kwargs):
        self._entities = copy.deepcopy(MambuLoan._entities)
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

    def set_state(self, action, notes):
        """Request to change status of a MambuLoan

        Args:
            action (str): specify the action state
            notes (str): notes to associate to the change of status

        Raises:
          `MambuPyError`: if action not in _accepted_actions
        """
        if action in self._accepted_actions:
            resp = self._connector.mambu_change_state(
                entid=self.id, prefix=self._prefix, action=action, notes=notes
            )
            resp = json.loads(resp)
            self.accountState = resp["accountState"]
        else:
            raise MambuPyError(
                "field {} not in allowed _accepted_actions: {}".format(
                    action, self._accepted_actions
                )
            )

    def approve(self, notes):
        """Request to approve a loan account.

        Args:
          notes (str): notes to attach to the approval operation.
        """
        self.set_state("APPROVE", notes)

    def disburse(
            self,
            notes,
            firstRepaymentDate=None, disbursementDate=None,
            **kwargs
    ):
        """Request to disburse a loan account.

        Args:
          notes (str): notes to attach to the disbursement transaction.
          firstRepaymentDate (:py:obj:`datetime`): first repayment date for the
                             loan account. If None, value is fetched from
                             disbursement details. If naive datetime, use TZ
                             info from tzattrs
          disbursementDate (:py:obj:`datetime`): disbursement date for the loan
                           account. If None, value is fetched from disbursement
                           details, expected disbursement date. If naive
                           datetime, use TZ info from tzattrs
          kwargs (dict): allowed extra params for the disbursement transaction
                 request. :py:obj:`MambuPy.api.vos.MambuDisbursementLoanTransactionInput._schema_fields`
                 has the allowed fields permitted for this operation
        """
        self._serializeFields()

        if firstRepaymentDate:
            if not firstRepaymentDate.tzinfo:
                timezone_firstRepaymentDate = datetime.timezone(
                    datetime.timedelta(
                        hours=int(self.disbursementDetails._tzattrs[
                            "firstRepaymentDate"][-6:-3])))
                firstRepaymentDate = firstRepaymentDate.astimezone(
                    timezone_firstRepaymentDate)
            firstRepaymentDate = firstRepaymentDate.isoformat()
        else:
            firstRepaymentDate = self.disbursementDetails.firstRepaymentDate

        if disbursementDate:
            if not disbursementDate.tzinfo:
                timezone_disbursementDate = datetime.timezone(
                    datetime.timedelta(
                        hours=int(self.disbursementDetails._tzattrs[
                            "expectedDisbursementDate"][-6:-3])))
                disbursementDate = disbursementDate.astimezone(
                    timezone_disbursementDate)
            disbursementDate = disbursementDate.isoformat()
        else:
            disbursementDate = self.disbursementDetails.expectedDisbursementDate

        self.disbursement_tr_resp = self._connector.mambu_make_disbursement(
            self.id, notes, firstRepaymentDate, disbursementDate,
            MambuDisbursementLoanTransactionInput._schema_fields, **kwargs)

        self.refresh()
