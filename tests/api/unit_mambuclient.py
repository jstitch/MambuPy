import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import interfaces
from MambuPy.api import mambuclient
from MambuPy.mambuutil import MambuPyError


class MambuClient(unittest.TestCase):
    def test_implements_interfaces(self):
        mc = mambuclient.MambuClient()
        self.assertTrue(isinstance(mc, mambuclient.MambuEntity))
        self.assertTrue(isinstance(mc, mambuclient.MambuEntityWritable))
        self.assertTrue(isinstance(mc, mambuclient.MambuEntityAttachable))
        self.assertTrue(isinstance(mc, mambuclient.MambuEntitySearchable))
        self.assertTrue(isinstance(mc, mambuclient.MambuEntityCommentable))
        self.assertTrue(isinstance(mc, interfaces.MambuHolder))

    def test_has_properties(self):
        mc = mambuclient.MambuClient()
        self.assertEqual(mc._prefix, "clients")
        self.assertEqual(
            mc._default_tzattrs,
            {
                "birthDate": None,
                "groupKeys": [None],
                "addresses": [{}],
                "idDocuments": [{}],
            })
        self.assertEqual(
            mc._filter_keys,
            [
                "branchId",
                "centreId",
                "creditOfficerUsername",
                "firstName",
                "lastName",
                "idNumber",
                "state",
                "birthDate",
            ],
        )
        self.assertEqual(
            mc._sortBy_fields,
            ["creationDate", "lastModifiedDate", "firstName", "lastName"],
        )
        self.assertEqual(mc._ownerType, "CLIENT")
        self.assertEqual(mc._vos, [("addresses", "MambuAddress"),
                                   ("idDocuments", "MambuIDDocument")])
        self.assertEqual(
            mc._entities,
            [("groupKeys", "mambugroup.MambuGroup", "groups"),
             ("assignedUserKey", "mambuuser.MambuUser", "assignedUser"),
             ("assignedBranchKey", "mambubranch.MambuBranch", "assignedBranch"),
             ("assignedCentreKey", "mambucentre.MambuCentre", "assignedCentre")])

    def test__delete_for_creation(self):
        mc = mambuclient.MambuClient()
        mc._attrs = {"id": "12345"}
        mc._delete_for_creation()
        self.assertEqual(mc._attrs, {"id": "12345"})

        mc._attrs["approvedDate"] = None
        mc._delete_for_creation()
        self.assertEqual(mc._attrs, {"id": "12345"})

    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several):
        mock_get_several.return_value = "SupGetSeveral"

        mc = mambuclient.MambuClient.get_all()
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuclient.MambuClient.get_all(filters={})
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuclient.MambuClient.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mc, "SupGetSeveral")

        mc = mambuclient.MambuClient.get_all(sortBy="firstName:ASC")
        self.assertEqual(mc, "SupGetSeveral")

        with self.assertRaisesRegex(MambuPyError, r"^key \w+ not in allowed "):
            mambuclient.MambuClient.get_all(
                filters={"branchId": "MyBranch", "Squad": "Red"}
            )

        with self.assertRaisesRegex(MambuPyError, r"^field \w+ not in allowed "):
            mambuclient.MambuClient.get_all(sortBy="field:ASC")


if __name__ == "__main__":
    unittest.main()
