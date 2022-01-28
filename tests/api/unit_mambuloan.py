import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import MambuPyError
from MambuPy.api import mambuloan


class MambuLoan(unittest.TestCase):
    def test_has_properties(self):
        ml = mambuloan.MambuLoan()
        self.assertEqual(ml._prefix, "loans")
        self.assertEqual(
            ml._filter_keys, [
                "branchId",
                "centreId",
                "accountState",
                "accountHolderType",
                "accountHolderId"])
        self.assertEqual(
            ml._sortBy_fields, [
                "creationDate",
                "lastModifiedDate",
                "id",
                "loanName"])
        self.assertEqual(
            ml._ownerType, "LOAN_ACCOUNT")

    @mock.patch("MambuPy.api.mambuloan.MambuEntity.get_all")
    def test_get_all(self, sup_get_all_mock):
        sup_get_all_mock.return_value = "SupGetAllMock"

        ml = mambuloan.MambuLoan.get_all()
        self.assertEqual(ml, "SupGetAllMock")

        ml = mambuloan.MambuLoan.get_all(filters={})
        self.assertEqual(ml, "SupGetAllMock")

        ml = mambuloan.MambuLoan.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(ml, "SupGetAllMock")

        ml = mambuloan.MambuLoan.get_all(sortBy="id:ASC")
        self.assertEqual(ml, "SupGetAllMock")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^key \w+ not in allowed "
        ):
            mambuloan.MambuLoan.get_all(
                filters={
                    "branchId": "MyBranch",
                    "Squad": "Red"})

        with self.assertRaisesRegex(
            MambuPyError,
            r"^field \w+ not in allowed "
        ):
            mambuloan.MambuLoan.get_all(
                sortBy="field:ASC")


if __name__ == "__main__":
    unittest.main()
