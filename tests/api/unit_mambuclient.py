import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambuclient
from MambuPy.mambuutil import MambuPyError


class MambuClient(unittest.TestCase):
    def test_has_properties(self):
        mc = mambuclient.MambuClient()
        self.assertEqual(mc._prefix, "clients")
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

    @mock.patch("MambuPy.api.mambustruct.MambuEntity._get_several")
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
