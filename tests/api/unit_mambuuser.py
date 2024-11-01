import inspect
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
        self.assertTrue(isinstance(mu, mambuuser.MambuEntityWritable))
        self.assertTrue(isinstance(mu, mambuuser.MambuEntityAttachable))
        self.assertTrue(isinstance(mu, mambuuser.MambuEntityCommentable))
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
        self.assertEqual(
            mu._entities,
            [("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
             ("role", "mamburole.MambuRole", "role")])

    def test___repr__(self):
        mu = mambuuser.MambuUser(**{"username": "charlie.brown"})
        self.assertEqual(repr(mu), "MambuUser - username: charlie.brown")

        mu = mambuuser.MambuUser(**{"id": "123456789"})
        self.assertEqual(repr(mu), "MambuUser - id: 123456789")

    @mock.patch("MambuPy.api.mambuuser.MambuUser.getEntities")
    def test___getattribute__(self, mock_getEntities):
        mu = mambuuser.MambuUser(
            **{"role": {"encodedKey": "0123456789abcdef"}})

        self.assertEqual(inspect.isfunction(mu.get_role), True)
        self.assertEqual(
            inspect.getsource(mu.get_role).strip(),
            """return lambda **kwargs: self.getEntities(entities=["role"], **kwargs)[0]""")
        mu.get_role()
        mock_getEntities.assert_called_with(entities=["role"])

    def test__updateVOs(self):
        mu = mambuuser.MambuUser(
            **{"role": {
                "encodedKey": "0123456789abcdef",
                "id": "123456",
                "name": "MY ROLE"}})

        mu._updateVOs()
        self.assertEqual(
            mu.role,
            {"encodedKey": "0123456789abcdef", "id": "123456"})

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mc = mambuuser.MambuUser.get_all()
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(something="else")
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(filters={})
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuuser.MambuUser.get_all(filters={"branchId": "MyBranch"}, branchIdType="ASSIGNED")
        self.assertEqual(mc, "SupGetSeveral")
        mc = mambuuser.MambuUser.get_all(filters={"branchId": "MyBranch"}, branchIdType="MANAGE")
        self.assertEqual(mc, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^branchIdType not allowed if branchId not provided$"):
            mambuuser.MambuUser.get_all(branchIdType="ASSIGNED")

        with self.assertRaisesRegex(MambuPyError, r"^branchIdType not allowed if branchId not provided$"):
            mambuuser.MambuUser.get_all(branchIdType="MANAGE")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambuuser.MambuUser.get_all(
                filters={"branchId": "MyBranch", "Squad": "Red"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambuuser.MambuUser.get_all(sortBy="field:ASC")

        with self.assertRaisesRegex(MambuPyError, r"^Invalid branchIdType: someRandomValue"):
            mambuuser.MambuUser.get_all(filters={"branchId": "BRANCHID"}, branchIdType="someRandomValue")


if __name__ == "__main__":
    unittest.main()
