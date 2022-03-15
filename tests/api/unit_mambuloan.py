import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambuloan
from MambuPy.mambuutil import MambuPyError


class MambuLoan(unittest.TestCase):
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

    @mock.patch("MambuPy.api.mambustruct.MambuEntity._get_several")
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


if __name__ == "__main__":
    unittest.main()
