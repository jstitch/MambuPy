import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import MambuPyError
from MambuPy.api import mambuclient


class MambuClient(unittest.TestCase):
    def test_has_properties(self):
        mc = mambuclient.MambuClient()
        self.assertEqual(mc._prefix, "clients")
        self.assertEqual(
            mc._filter_keys, [
                "branchId",
                "centreId",
                "creditOfficerUsername",
                "firstName",
                "lastName",
                "idNumber",
                "state",
                "birthDate"])
        self.assertEqual(
            mc._sortBy_fields, [
                "creationDate",
                "lastModifiedDate",
                "firstName",
                "lastName"])
        self.assertEqual(
            mc._ownerType, "CLIENT")

    @mock.patch("MambuPy.api.mambuclient.MambuEntity.get_all")
    def test_get_all(self, sup_get_all_mock):
        sup_get_all_mock.return_value = "SupGetAllMock"

        mc = mambuclient.MambuClient.get_all()
        self.assertEqual(mc, "SupGetAllMock")

        mc = mambuclient.MambuClient.get_all(filters={})
        self.assertEqual(mc, "SupGetAllMock")

        mc = mambuclient.MambuClient.get_all(filters={"branchId": "MyBranch"})
        self.assertEqual(mc, "SupGetAllMock")

        mc = mambuclient.MambuClient.get_all(sortBy="firstName:ASC")
        self.assertEqual(mc, "SupGetAllMock")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^key \w+ not in allowed "
        ):
            mambuclient.MambuClient.get_all(
                filters={
                    "branchId": "MyBranch",
                    "Squad": "Red"})

        with self.assertRaisesRegex(
            MambuPyError,
            r"^field \w+ not in allowed "
        ):
            mambuclient.MambuClient.get_all(
                sortBy="field:ASC")


if __name__ == "__main__":
    unittest.main()
