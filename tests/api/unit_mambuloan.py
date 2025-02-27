import datetime
import os
import sys
import unittest

from dateutil.tz import tzlocal
from freezegun import freeze_time
import mock


sys.path.insert(0, os.path.abspath("."))

from MambuPy.api.mambutransaction import MambuTransaction
from MambuPy.api import entities
from MambuPy.api import mambuloan
from MambuPy.api.vos import (
    MambuDisbursementDetails,
    MambuDisbursementLoanTransactionInput,
    MambuFeeLoanTransactionInput,
    MambuRepaymentLoanTransactionInput,
    MambuLoanTransactionDetailsInput,
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

    def test__delete_for_creation(self):
        ml = mambuloan.MambuLoan()
        ml._attrs = {"id": "12345"}
        ml._delete_for_creation()
        self.assertEqual(ml._attrs, {"id": "12345"})

        ml._attrs["currency"] = None
        ml._attrs["accountState"] = None
        ml._attrs["scheduleSettings"] = {"hasCustomSchedule": None}
        ml._attrs["interestSettings"] = {"accrueLateInterest": None}
        ml._delete_for_creation()
        self.assertEqual(ml._attrs, {"id": "12345", "scheduleSettings": {}, "interestSettings": {}})

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

    @freeze_time("2022-07-30T18:00:00-06:00", tz_offset=-6)
    def test_get_schedule(self):
        ml = mambuloan.MambuLoan(**{"id": "12345", "connector": mock.Mock()})
        mock_connector = ml._connector

        mock_connector.mambu_loanaccount_getSchedule.return_value = b"""{"installments": [
        {"encodedKey":"54321dcba",
         "parentAccountKey":"abcd12345",
         "number":"1",
         "dueDate":"2022-07-14T19:00:00-06:00",
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
         "dueDate":"2022-07-21T19:00:00-06:00",
         "state":"PENDING",
         "isPaymentHoliday":false,
         "principal":{"amount":{"expected":20105.8300000000,"paid":0,"due":20105.8300000000}},
         "interest":{"amount":{"expected":408.1400000000,"paid":0,"due":408.1400000000},
                     "tax":{"expected":0,"paid":0,"due":0}},
         "fee":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}},
         "penalty":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}}}],
        "currency": {"code": "MXN"}}
        """

        ml.get_schedule()

        mock_connector.mambu_loanaccount_getSchedule.assert_called_with("12345")
        self.assertEqual(len(ml.schedule), 2)

        self.assertTrue(isinstance(ml.schedule[0], entities.MambuInstallment))
        self.assertEqual(ml.schedule[0]["encodedKey"], "54321dcba")
        self.assertEqual(ml.schedule[0]["number"], 1)
        self.assertEqual(ml.schedule[0]["state"], "PAID")
        # self.assertEqual(ml.schedule[0]["dueDate"].strftime("%Y%m%d"), "20220715")
        # self.assertEqual(repr(ml.schedule[0]), "MambuInstallment - #1, PAID, 2022-07-15")

        self.assertTrue(isinstance(ml.schedule[1], entities.MambuInstallment))
        self.assertEqual(ml.schedule[1]["encodedKey"], "09876fedc")
        self.assertEqual(ml.schedule[1]["number"], 2)
        self.assertEqual(ml.schedule[1]["state"], "PENDING")
        # self.assertEqual(ml.schedule[1]["dueDate"].strftime("%Y%m%d"), "20220722")
        # self.assertEqual(repr(ml.schedule[1]), "MambuInstallment - #2, PENDING, 2022-07-22")

    @mock.patch("MambuPy.api.mambutransaction.MambuTransaction.get_all")
    def test_get_transactions(self,mock_get_all):
        mock_get_all.return_value =  [
            MambuTransaction(id='2897470', amount=6708.0,type ='REPAYMENT'),
            MambuTransaction(id='2897455', amount=-6708.0, type= 'REPAYMENT_ADJUSTMENT')
        ]
        ml= mambuloan.MambuLoan(id="12345")
        ml.get_transactions()
        mock_get_all.assert_called_once_with("12345")
        self.assertEqual(len(ml.transactions), 2)
        self.assertEqual(ml.transactions[0]["type"],"REPAYMENT")

        self.assertTrue(isinstance(ml.transactions[0], MambuTransaction))

    def test_set_state(self):
        ml = mambuloan.MambuLoan(id=1, connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_change_state.return_value = '{"accountState": "APPROVED"}'

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

    def test_approve(self):
        ml = mambuloan.MambuLoan(id=1, connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_change_state.return_value = '{"accountState": "APPROVED"}'

        ml.approve(notes="Smells like teen spirit")

        mock_connector.mambu_change_state.assert_called_with(
            action="APPROVE",
            entid=1,
            notes="Smells like teen spirit",
            prefix="loans"
        )
        self.assertEqual(ml.accountState, "APPROVED")

    def test_disburse_implicit_dates(self):
        ml = mambuloan.MambuLoan(
            id='12345', accountState="APPROVED", connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_make_disbursement.return_value = '{"encodedKey": "abc123"}'
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

    def test_disburse_explicit_dates(self):
        ml = mambuloan.MambuLoan(
            id='12345', accountState="APPROVED", connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_make_disbursement.return_value = '{"encodedKey": "abc123"}'
        ml.refresh = mock.Mock()

        # explicit firstrepaymentdate and valuedate
        firstRepaymentDate = datetime.datetime.now(
            tz=datetime.timezone(datetime.timedelta(0)))
        valueDate = datetime.datetime.now(
            tz=datetime.timezone(datetime.timedelta(0)))
        ml.disbursementDetails = MambuDisbursementDetails(**{
            "firstRepaymentDate": firstRepaymentDate,
            "expectedDisbursementDate": valueDate})
        ml.disbursementDetails._tzattrs = {
            "firstRepaymentDate": "UTC+00:00",
            "expectedDisbursementDate": "UTC+00:00"}
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

        mock_connector.reset_mock()
        ml.refresh.reset_mock()
        firstRepaymentDate = datetime.datetime.now()
        valueDate = datetime.datetime.now()
        ml.disbursementDetails = MambuDisbursementDetails(**{
            "firstRepaymentDate": firstRepaymentDate,
            "expectedDisbursementDate": valueDate})
        ml.disbursementDetails._tzattrs = {
            "firstRepaymentDate": "UTC+00:00",
            "expectedDisbursementDate": "UTC+00:00"}
        ml.disburse(
            notes="A denial",
            firstRepaymentDate=firstRepaymentDate,
            disbursementDate=valueDate,
            **{"something": "else"})
        mock_connector.mambu_make_disbursement.assert_called_with(
            '12345',
            "A denial",
            firstRepaymentDate.astimezone(
                datetime.timezone(datetime.timedelta(0))).isoformat(),
            valueDate.astimezone(
                datetime.timezone(datetime.timedelta(0))).isoformat(),
            MambuDisbursementLoanTransactionInput._schema_fields,
            **{"something": "else"}
        )
        ml.refresh.assert_called_once()

    def test_reject(self):
        ml = mambuloan.MambuLoan(id=1, connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_change_state.return_value = '{"accountState": "REJECTED"}'

        ml.reject(notes="Black hole sun")

        mock_connector.mambu_change_state.assert_called_with(
            action="REJECT",
            entid=1,
            notes="Black hole sun",
            prefix="loans"
        )
        self.assertEqual(ml.accountState, "REJECTED")

    def test_close(self):
        ml = mambuloan.MambuLoan(id=1, connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_change_state.return_value = '{"accountState": "CLOSED"}'

        ml.close(notes="Jeremy spoke in class again")

        mock_connector.mambu_change_state.assert_called_with(
            action="CLOSE",
            entid=1,
            notes="Jeremy spoke in class again",
            prefix="loans"
        )
        self.assertEqual(ml.accountState, "CLOSED")

    def test_writeoff(self):
        def write_off(loan):
            loan.accountState = 'CLOSED'
            loan.accountSubState = 'WRITTEN_OFF'
        ml = mambuloan.MambuLoan(id=1, connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_loanaccount_writeoff.return_value = ''

        ml.refresh = mock.Mock()
        ml.refresh.side_effect = write_off(ml)

        ml.writeoff(notes="Smells like teen spirit")

        mock_connector.mambu_loanaccount_writeoff.assert_called_with(
            1,
            "Smells like teen spirit",
        )
        self.assertEqual(ml.accountState, "CLOSED")
        self.assertEqual(ml.accountSubState, "WRITTEN_OFF")

    def test_repay(self):
        ml = mambuloan.MambuLoan(id='12345', accountState="ACTIVE", connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_make_repayment.return_value = '{"encodedKey": "abc123"}'
        ml.refresh = mock.Mock()

        valueDate = datetime.datetime.now()
        valueDateAssert = datetime.datetime.strptime(
            valueDate.strftime("%Y-%m-%d %H%M%S"), "%Y-%m-%d %H%M%S")
        timezone = datetime.datetime.now().astimezone(tzlocal()).isoformat()[-6:]
        valueDateAssert = valueDateAssert.isoformat() + timezone

        ml.repay(
            amount=100.0,
            notes="STP",
            valueDate=valueDate,
            **{"_something": {"else": "cf_val"}})

        mock_connector.mambu_make_repayment.assert_called_with(
            '12345',
            100.0,
            "STP",
            valueDateAssert,
            MambuRepaymentLoanTransactionInput._schema_fields,
            MambuLoanTransactionDetailsInput._schema_fields,
            **{"_something": {"else": "cf_val"}}
        )
        ml.refresh.assert_called_once()

    def test_adjust(self):
        ml = mambuloan.MambuLoan(id='12345', accountState="ACTIVE", connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_loantransaction_adjust.return_value = '{"encodedKey": "abc123"}'
        ml.refresh = mock.Mock()

        ml.adjust_transaction(transactionId="Neil Young", notes="Crazy Horse")

        mock_connector.mambu_loantransaction_adjust.assert_called_with(
            'Neil Young',
            "Crazy Horse",
        )
        ml.refresh.assert_called_once()

    def test_adjust_validate_transactionId(self):
        ml = mambuloan.MambuLoan(id='12345', accountState="ACTIVE", connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_loantransaction_adjust.return_value = '{"encodedKey": "abc123"}'
        ml.refresh = mock.Mock()

        ml.transactions = [
            MambuTransaction(id='2897470', amount=6708.0,type ='REPAYMENT'),
        ]

        ml.adjust_transaction(transactionId="2897470", notes="hey hey my my")
        mock_connector.mambu_loantransaction_adjust.assert_called_with(
            '2897470',
            "hey hey my my",
        )
        with self.assertRaisesRegex(
            MambuPyError, r"^transactionId 'my my hey hey' not found in loan transactions"
        ):
            ml.adjust_transaction(transactionId="my my hey hey", notes="hey hey my my")

    def test_apply_fee(self):
        ml = mambuloan.MambuLoan(id='12345', accountState="ACTIVE", connector=mock.Mock())
        mock_connector = ml._connector
        mock_connector.mambu_make_fee.return_value = '{"encodedKey": "abc123"}'
        ml.refresh = mock.Mock()

        valueDate = datetime.datetime.now()
        valueDateAssert = datetime.datetime.strptime(
            valueDate.strftime("%Y-%m-%d %H%M%S"), "%Y-%m-%d %H%M%S")
        timezone = datetime.datetime.now().astimezone(tzlocal()).isoformat()[-6:]
        valueDateAssert = valueDateAssert.isoformat() + timezone

        ml.apply_fee(
            amount=100.0,
            installmentNumber=15,
            notes="STP",
            valueDate=valueDate,
            **{"something": "else"})

        mock_connector.mambu_make_fee.assert_called_with(
            '12345',
            100.0,
            15,
            "STP",
            valueDateAssert,
            MambuFeeLoanTransactionInput._schema_fields,
            **{"something": "else"}
        )
        ml.refresh.assert_called_once()


if __name__ == "__main__":
    unittest.main()
