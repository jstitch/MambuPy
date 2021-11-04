import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import apiurl

from MambuPy.api import mambuconnector


class MambuConnectorReader(unittest.TestCase):
    def test_mambu_get(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader, "mambu_get"),
            True)
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get(None, "12345", "")


class MambuConnectorREST(unittest.TestCase):
    def test_properties(self):
        mcrest = mambuconnector.MambuConnectorREST()

        self.assertEqual(mcrest._tenant, apiurl)
        self.assertEqual(mcrest._headers["Accept"], "application/vnd.mambu.v2+json")
        self.assertEqual(mcrest._headers["Authorization"][:6], "Basic ")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu_get(self, mock_requests):
        mcrest = mambuconnector.MambuConnectorREST()

        mcrest.mambu_get("12345", "someURL")

        mock_requests.request.assert_called_with(
            "GET", "https://{}/api/someURL/12345".format(apiurl), headers=mcrest._headers)


if __name__ == "__main__":
    unittest.main()
