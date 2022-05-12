import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import entities
from MambuPy.api import interfaces
from MambuPy.api import mambuloan
from MambuPy.mambuutil import MambuPyError


class MambuLoan(unittest.TestCase):
    def test_implements_interfaces(self):
        ml = mambuloan.MambuLoan()
        self.assertTrue(isinstance(ml, mambuloan.MambuEntity))
        self.assertTrue(isinstance(ml, interfaces.MambuWritable))
        self.assertTrue(isinstance(ml, interfaces.MambuAttachable))
        self.assertTrue(isinstance(ml, interfaces.MambuSearchable))

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
             ("originalAccountKey", "mambuloan.MambuLoan", "originalAccount")])

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
         "interest":{"amount":{"expected":408.1400000000,"paid":0,"due":408.1400000000},"tax":{"expected":0,"paid":0,"due":0}},
         "fee":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}},
         "penalty":{"amount":{"expected":0,"paid":0,"due":0},"tax":{"expected":0,"paid":0,"due":0}}},
        {"encodedKey":"09876fedc",
         "parentAccountKey":"abcd12345",
         "number":"2",
         "dueDate":"2022-07-21T19:00:00-05:00",
         "state":"PENDING",
         "isPaymentHoliday":false,
         "principal":{"amount":{"expected":20105.8300000000,"paid":0,"due":20105.8300000000}},
         "interest":{"amount":{"expected":408.1400000000,"paid":0,"due":408.1400000000},"tax":{"expected":0,"paid":0,"due":0}},
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


if __name__ == "__main__":
    unittest.main()
