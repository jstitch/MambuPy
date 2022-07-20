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
                       MambuEntityCommentable,
                       MambuInstallment)
from MambuPy.mambuutil import MambuPyError


class MambuLoan(
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntityCommentable,
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

    def _assignEntObjs(
        self,
        entities=None,
        detailsLevel="BASIC",
        get_entities=False,
        debug=False
    ):
        """Overwrites `MambuPy.api.mambustruct._assignEntObjs` for MambuLoan

           Determines the type of account holder and instantiates accordingly
        """
        if entities is None:
            entities = self._entities

        try:
            accountholder_index = entities.index(("accountHolderKey", "", "accountHolder"))
        except ValueError:
            accountholder_index = None

        if accountholder_index is not None and self.has_key("accountHolderKey"):
            if self.accountHolderType == "CLIENT":
                entities[accountholder_index] = (
                    "accountHolderKey", "mambuclient.MambuClient", "accountHolder")
            elif self.accountHolderType == "GROUP":
                entities[accountholder_index] = (
                    "accountHolderKey", "mambugroup.MambuGroup", "accountHolder")

        super()._assignEntObjs(
            entities,
            detailsLevel=detailsLevel,
            get_entities=get_entities,
            debug=debug)

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
        """Change status of mambu loan

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
