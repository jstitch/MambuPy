import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import MambuPyError
from MambuPy.api import mambugroup


class MambuGroup(unittest.TestCase):
    def test_has_properties(self):
        mg = mambugroup.MambuGroup()
        self.assertEqual(mg._prefix, "groups")
        self.assertEqual(
            mg._filter_keys, [
                "branchId",
                "centreId",
                "creditOfficerUsername"])
        self.assertEqual(
            mg._sortBy_fields, [
                "creationDate",
                "lastModifiedDate",
                "groupName"])
        self.assertEqual(
            mg._ownerType, "GROUP")

    @mock.patch("MambuPy.api.mambugroup.MambuEntity.get_all")
    def test_get_all(self, sup_get_all_mock):
        sup_get_all_mock.return_value = "SupGetAllMock"

        mg = mambugroup.MambuGroup.get_all()
        self.assertEqual(mg, "SupGetAllMock")

        mg = mambugroup.MambuGroup.get_all(filters={})
        self.assertEqual(mg, "SupGetAllMock")

        mg = mambugroup.MambuGroup.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mg, "SupGetAllMock")

        mg = mambugroup.MambuGroup.get_all(sortBy="groupName:ASC")
        self.assertEqual(mg, "SupGetAllMock")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^key \w+ not in allowed "
        ):
            mambugroup.MambuGroup.get_all(
                filters={
                    "branchId": "MyBranch",
                    "Squad": "Red"})

        with self.assertRaisesRegex(
            MambuPyError,
            r"^field \w+ not in allowed "
        ):
            mambugroup.MambuGroup.get_all(
                sortBy="field:ASC")


if __name__ == "__main__":
    unittest.main()
