import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api import mambutransaction
from MambuPy.mambuutil import MambuPyError


class MambuTransaction(unittest.TestCase):
    def test_implements_interfaces(self):
        ml = mambutransaction.MambuTransaction()
        self.assertTrue(isinstance(ml, mambutransaction.MambuEntity))
        self.assertTrue(isinstance(ml, mambutransaction.MambuEntitySearchable))

    def test_has_properties(self):
        ml = mambutransaction.MambuTransaction()
        self.assertEqual(ml._prefix, "loans/transactions")
        self.assertEqual(
            ml._filter_keys,
            [
            ],
        )
        self.assertEqual(
            ml._sortBy_fields, []
        )

    @mock.patch("MambuPy.api.entities.MambuConnectorREST")
    @mock.patch("MambuPy.api.entities.MambuEntity._get_several")
    def test_get_all(self, mock_get_several, mock_connector_rest):
        mock_get_several.return_value = "SupGetSeveral"

        mt = mambutransaction.MambuTransaction.get_all(loanAccountId="12345")
        self.assertEqual(mt, "SupGetSeveral")
        mock_get_several.assert_called_with(
            mock_connector_rest.return_value.mambu_get_all,
            mock_connector_rest.return_value,
            filters=None,
            offset=None, limit=None,
            paginationDetails="OFF", detailsLevel="BASIC",
            sortBy=None,
            prefix="loans/12345/transactions")


if __name__ == "__main__":
    unittest.main()
