import datetime
import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities
from MambuPy.api import mambuloan
from MambuPy.api.vos import (
    MambuDisbursementDetails,
    MambuDisbursementLoanTransactionInput,
)
from MambuPy.mambuutil import MambuPyError


class MambuLoan(unittest.TestCase):
    def test_implements_interfaces(self):
        ml = mambuloan.MambuLoan()
        self.assertTrue(isinstance(ml, mambuloan.MambuEntity))
        self.assertTrue(isinstance(ml, mambuloan.MambuEntityWritable))
        self.assertTrue(isinstance(ml, mambuloan.MambuEntityAttachable))
        self.assertTrue(isinstance(ml, mambuloan.MambuEntityCommentable))
        self.assertTrue(isinstance(ml, mambuloan.MambuEntityOwnable))
        self.assertTrue(isinstance(ml, mambuloan.MambuEntitySearchable))

    def test_has_properties(self):
        ml = mambuloan.MambuLoan()
        self.assertEqual(ml._prefix, "loans")
        self.assertEqual(
            ml._filter_keys,
            [
                "branchId",
                "centreId",
                "accountState",
                "accountHolderType",
                "accountHolderId",
                "creditOfficerUsername",
            ],
        )
        self.assertEqual(
            ml._sortBy_fields, ["creationDate", "lastModifiedDate", "id", "loanName"]
        )
        self.assertEqual(ml._ownerType, "LOAN_ACCOUNT")
        self.assertEqual(ml._vos, [("disbursementDetails", "MambuDisbursementDetails")])
        self.assertEqual(
            ml._entities,
            [("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
             ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
             ("assignedCentreKey", "mambucentre.MambuCentre", "assignedCentre"),
             ("productTypeKey", "mambuproduct.MambuProduct", "productType"),
             ("originalAccountKey", "mambuloan.MambuLoan", "originalAccount"),
             ("accountHolderKey", "", "accountHolder")])

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        ml = mambuloan.MambuLoan.get_all()
        self.assertEqual(ml, "SupGetSeveral")

        ml = mambuloan.MambuLoan.get_all(filters={})
        self.assertEqual(ml, "SupGetSeveral")

        ml = mambuloan.MambuLoan.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(ml, "SupGetSeveral")

        ml = mambuloan.MambuLoan.get_all(sortBy="id:ASC")
        self.assertEqual(ml, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambuloan.MambuLoan.get_all(filters={"branchId": "MyBranch", "Squad": "Red"})

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambuloan.MambuLoan.get_all(sortBy="field:ASC")

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_get_schedule(self, mock_connector):
        mock_connector.mambu_loanaccount_getSchedule.return_value = b"""{"installments": [
        {"encodedKey":"54321dcba",
         "parentAccountKey":"abcd12345",
         "number":"1",
         "dueDate":"2022-07-14T19:00:00-05:00",
         "state":"PAID",
         "isPaymentHoliday":false,
         "principal":{"amount":{"expected":0,"paid":20105.8300000000,"due":20105.8300000000}},
         "interest":{"amount":{"expected":408.1400000000,"paid":0,"due":408.1400000000},
                     "tax":{"expected":0,"paid":0,"due":0}},
         "fee":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}},
         "penalty":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}}},
        {"encodedKey":"09876fedc",
         "parentAccountKey":"abcd12345",
         "number":"2",
         "dueDate":"2022-07-21T19:00:00-05:00",
         "state":"PENDING",
         "isPaymentHoliday":false,
         "principal":{"amount":{"expected":20105.8300000000,"paid":0,"due":20105.8300000000}},
         "interest":{"amount":{"expected":408.1400000000,"paid":0,"due":408.1400000000},
                     "tax":{"expected":0,"paid":0,"due":0}},
         "fee":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}},
         "penalty":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}}}],
        "currency": {"code": "MXN"}}
        """

        ml = mambuloan.MambuLoan(**{"id": "12345"})
        ml.get_schedule()

        mock_connector.mambu_loanaccount_getSchedule.assert_called_with("12345")
        self.assertEqual(len(ml.schedule), 2)

        self.assertTrue(isinstance(ml.schedule[0], entities.MambuInstallment))
        self.assertEqual(ml.schedule[0]["encodedKey"], "54321dcba")
        self.assertEqual(ml.schedule[0]["number"], 1)
        self.assertEqual(ml.schedule[0]["state"], "PAID")
        self.assertEqual(ml.schedule[0]["dueDate"].strftime("%Y%m%d"), "20220714")
        self.assertEqual(repr(ml.schedule[0]), "MambuInstallment - #1, PAID, 2022-07-14")

        self.assertTrue(isinstance(ml.schedule[1], entities.MambuInstallment))
        self.assertEqual(ml.schedule[1]["encodedKey"], "09876fedc")
        self.assertEqual(ml.schedule[1]["number"], 2)
        self.assertEqual(ml.schedule[1]["state"], "PENDING")
        self.assertEqual(ml.schedule[1]["dueDate"].strftime("%Y%m%d"), "20220721")
        self.assertEqual(repr(ml.schedule[1]), "MambuInstallment - #2, PENDING, 2022-07-21")

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_set_state(self, mock_connector):
        mock_connector.mambu_change_state.return_value = '{"accountState": "APPROVED"}'
        ml = mambuloan.MambuLoan(id=1)

        ml.set_state(
            action="APPROVE",
            notes="PRUEBA 66"
        )

        mock_connector.mambu_change_state.assert_called_with(
            action="APPROVE",
            entid=1,
            notes="PRUEBA 66",
            prefix="loans"
        )
        self.assertEqual(ml.accountState, "APPROVED")

        mock_connector.mambu_change_state.reset_mock()
        with self.assertRaisesRegex(
            MambuPyError, r"^field CANCELADO not in allowed _accepted_actions"
        ):
            ml.set_state(
                action="CANCELADO",
                notes="PRUEBA 66"
            )
            mock_connector.mambu_change_state.assert_not_called()

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_approve(self, mock_connector):
        mock_connector.mambu_change_state.return_value = '{"accountState": "APPROVED"}'
        ml = mambuloan.MambuLoan(id=1)

        ml.approve(notes="Smells like teen spirit")

        mock_connector.mambu_change_state.assert_called_with(
            action="APPROVE",
            entid=1,
            notes="Smells like teen spirit",
            prefix="loans"
        )
        self.assertEqual(ml.accountState, "APPROVED")

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_disburse_implicit_dates(self, mock_connector):
        mock_connector.mambu_make_disbursement.return_value = '{"encodedKey": "abc123"}'
        ml = mambuloan.MambuLoan(id='12345', accountState="APPROVED")
        ml.refresh = mock.Mock()

        # implicit firstrepaymentdate and valuedate
        firstRepaymentDate = datetime.datetime.now()
        valueDate = datetime.datetime.now()
        ml.disbursementDetails = MambuDisbursementDetails(**{
            "firstRepaymentDate": firstRepaymentDate,
            "expectedDisbursementDate": valueDate})
        ml.disbursementDetails._tzattrs = {
            "firstRepaymentDate": "UTC-05:00",
            "expectedDisbursementDate": "UTC-05:00"}
        ml.disburse(
            notes="A denial",
            **{"something": "else"})

        mock_connector.mambu_make_disbursement.assert_called_with(
            '12345',
            "A denial",
            firstRepaymentDate.isoformat() + "-05:00",
            valueDate.isoformat() + "-05:00",
            MambuDisbursementLoanTransactionInput._schema_fields,
            **{"something": "else"}
        )
        ml.refresh.assert_called_once()

    @mock.patch("MambuPy.api.entities.MambuEntity._connector")
    def test_disburse_explicit_dates(self, mock_connector):
        mock_connector.mambu_make_disbursement.return_value = '{"encodedKey": "abc123"}'
        ml = mambuloan.MambuLoan(id='12345', accountState="APPROVED")
        ml.refresh = mock.Mock()

        # explicit firstrepaymentdate and valuedate
        firstRepaymentDate = datetime.datetime.now()
        valueDate = datetime.datetime.now()
        ml.disburse(
            notes="A denial",
            firstRepaymentDate=firstRepaymentDate,
            disbursementDate=valueDate,
            **{"something": "else"})

        mock_connector.mambu_make_disbursement.assert_called_with(
            '12345',
            "A denial",
            firstRepaymentDate.isoformat(),
            valueDate.isoformat(),
            MambuDisbursementLoanTransactionInput._schema_fields,
            **{"something": "else"}
        )
        ml.refresh.assert_called_once()


if __name__ == "__main__":
    unittest.main()
