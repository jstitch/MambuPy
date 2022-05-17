import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambubranch
from MambuPy.mambuutil import MambuPyError


class MambuBranch(unittest.TestCase):
    def test_implements_interfaces(self):
        mb = mambubranch.MambuBranch()
        self.assertTrue(isinstance(mb, mambubranch.MambuEntity))
        self.assertTrue(isinstance(mb, interfaces.MambuOwner))

    def test_has_properties(self):
        mb = mambubranch.MambuBranch()
        self.assertEqual(mb._prefix, "branches")
        self.assertEqual(
            mb._filter_keys,
            [
            ],
        )
        self.assertEqual(
            mb._sortBy_fields, ["creationDate", "lastModifiedDate", "id", "name"]
        )
        self.assertEqual(mb._vos, [("addresses", "MambuAddress")])

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mb = mambubranch.MambuBranch.get_all()
        self.assertEqual(mb, "SupGetSeveral")

        mb = mambubranch.MambuBranch.get_all(filters={})
        self.assertEqual(mb, "SupGetSeveral")

        mb = mambubranch.MambuBranch.get_all(sortBy="id:ASC")
        self.assertEqual(mb, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambubranch.MambuBranch.get_all(filters={"branchId": "MyBranch", "Squad": "Red"})

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambubranch.MambuBranch.get_all(sortBy="field:ASC")

        mambubranch.MambuBranch._filter_keys = ["id"]
        mb = mambubranch.MambuBranch.get_all(filters={"id": "ASC"})
        self.assertEqual(mb, "SupGetSeveral")
        mambubranch.MambuBranch._filter_keys = []


if __name__ == "__main__":
    unittest.main()
