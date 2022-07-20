import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambugroup
from MambuPy.mambuutil import MambuPyError


class MambuGroup(unittest.TestCase):
    def test_implements_interfaces(self):
        mg = mambugroup.MambuGroup()
        self.assertTrue(isinstance(mg, mambugroup.MambuEntity))
        self.assertTrue(isinstance(mg, interfaces.MambuWritable))
        self.assertTrue(isinstance(mg, interfaces.MambuAttachable))
        self.assertTrue(isinstance(mg, interfaces.MambuSearchable))
        self.assertTrue(isinstance(mg, interfaces.MambuCommentable))
        self.assertTrue(isinstance(mg, interfaces.MambuHolder))

    def test_has_properties(self):
        mg = mambugroup.MambuGroup()
        self.assertEqual(mg._prefix, "groups")
        self.assertEqual(
            mg._filter_keys, ["branchId", "centreId", "creditOfficerUsername"]
        )
        self.assertEqual(
            mg._sortBy_fields, ["creationDate", "lastModifiedDate", "groupName"]
        )
        self.assertEqual(mg._ownerType, "GROUP")
        self.assertEqual(mg._vos, [("addresses", "MambuAddress"),
                                   ("groupMembers", "MambuGroupMember")])
        self.assertEqual(
            mg._entities,
            [("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
             ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
             ("assignedCentreKey", "mambucentre.MambuCentre", "assignedCentre")])

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mg = mambugroup.MambuGroup.get_all()
        self.assertEqual(mg, "SupGetSeveral")

        mg = mambugroup.MambuGroup.get_all(filters={})
        self.assertEqual(mg, "SupGetSeveral")

        mg = mambugroup.MambuGroup.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mg, "SupGetSeveral")

        mg = mambugroup.MambuGroup.get_all(sortBy="groupName:ASC")
        self.assertEqual(mg, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambugroup.MambuGroup.get_all(
                filters={"branchId": "MyBranch", "Squad": "Red"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambugroup.MambuGroup.get_all(sortBy="field:ASC")


class MambuGroupMember(unittest.TestCase):
    def test__extractVOs(self):
        mg = mambugroup.MambuGroup()
        mg._attrs = {
            "groupMembers": [
                {"clientKey": "abc123", "roles": []},
                {"clientKey": "def456", "roles": [
                    {"encodedKey": "ghi789",
                     "roleName": "MyRole",
                     "roleNameId": "789"}]}
                ]
        }
        mg._extractVOs()

        self.assertEqual(len(mg.groupMembers), 2)
        for member in mg.groupMembers:
            self.assertEqual(
                member.__class__.__name__,
                "MambuGroupMember")
        self.assertEqual(len(mg.groupMembers[0]["roles"]), 0)
        self.assertEqual(len(mg.groupMembers[1]["roles"]), 1)
        self.assertEqual(
            mg.groupMembers[1]["roles"][0].__class__.__name__,
            "MambuGroupRole")

    def test__updateVOs(self):
        from mambupy.api.vos import MambuGroupMember, MambuGroupRole

        mg = mambugroup.MambuGroup()
        mg._attrs = {
            "groupMembers": [
                MambuGroupMember(**{"clientKey": "abc123", "roles": []}),
                MambuGroupMember(**{"clientKey": "def456", "roles": [
                    MambuGroupRole(**{"encodedKey": "ghi789",
                                      "roleName": "MyRole",
                                      "roleNameId": "789"})]})
                ]
        }
        mg._updateVOs()

        self.assertEqual(len(mg.groupMembers), 2)
        self.assertEqual(mg.groupMembers[0], {"clientKey": "abc123", "roles": []})
        self.assertEqual(mg.groupMembers[1],
                         {"clientKey": "def456",
                          "roles": [
                              {"encodedKey": "ghi789",
                               "roleName": "MyRole",
                               "roleNameId": "789"}
                              ]})


if __name__ == "__main__":
    unittest.main()
