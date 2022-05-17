import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambuuser
from MambuPy.mambuutil import MambuPyError


class MambuUser(unittest.TestCase):
    def test_implements_interfaces(self):
        mu = mambuuser.MambuUser()
        self.assertTrue(isinstance(mu, mambuuser.MambuEntity))
        self.assertTrue(isinstance(mu, interfaces.MambuWritable))
        self.assertTrue(isinstance(mu, interfaces.MambuAttachable))
        self.assertTrue(isinstance(mu, interfaces.MambuOwner))

    def test_has_properties(self):
        mu = mambuuser.MambuUser()
        self.assertEqual(mu._prefix, "users")
        self.assertEqual(
            mu._filter_keys,
            [
                "branchId",
            ],
        )
        self.assertEqual(
            mu._sortBy_fields,
            [],
        )
        self.assertEqual(mu._ownerType, "USER")
        self.assertEqual(mu._vos, [("role", "MambuUserRole")])
        self.assertEqual(
            mu._entities,
            [("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch")])

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mc = mambuuser.MambuUser.get_all()
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(filters={})
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(branchIdType="ASSIGNED")
        self.assertEqual(mc, "SupGetSeveral")
        mc = mambuuser.MambuUser.get_all(branchIdType="MANAGE")
        self.assertEqual(mc, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambuuser.MambuUser.get_all(
                filters={"branchId": "MyBranch", "Squad": "Red"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambuuser.MambuUser.get_all(sortBy="field:ASC")

        with self.assertRaisesRegex(MambuPyError, r"^Invalid branchIdType: someRandomValue"):
            mambuuser.MambuUser.get_all(branchIdType="someRandomValue")


if __name__ == "__main__":
    unittest.main()
