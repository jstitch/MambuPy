import unittest
import mock
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import (
    apiurl,
    MambuPyError, MambuError,
    PAGINATIONDETAILS,
    DETAILSLEVEL,
    )

from MambuPy.api import mambuconnector


class MambuConnectorReader(unittest.TestCase):
    def test_mambu_get(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader, "mambu_get"),
            True)
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get(None, "12345", "")

    def test_mambu_get_all(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader, "mambu_get_all"),
            True)
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_get_all(
                None, "", {}, 0, 0, "OFF", "BASIC", "")


class MambuConnectorREST(unittest.TestCase):
    def test_properties(self):
        mcrest = mambuconnector.MambuConnectorREST()

        self.assertEqual(mcrest._tenant, apiurl)
        self.assertEqual(mcrest._headers["Accept"], "application/vnd.mambu.v2+json")
        self.assertEqual(mcrest._headers["Authorization"][:6], "Basic ")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request(self, mock_requests):
        mock_requests.request().status_code = 400

        mock_requests.request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi"}]}
"""
        mcrest = mambuconnector.MambuConnectorREST()
        with self.assertRaisesRegex(MambuError, r"66 - Kill the Jedi"):
            mcrest.__request("GET", "someURL")

        mock_requests.request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi",
      "errorSource": "Palpatine"}]}
"""
        mcrest = mambuconnector.MambuConnectorREST()
        with self.assertRaisesRegex(MambuError, r"^66 - Kill the Jedi \(Palpatine\)$"):
            mcrest.__request("GET", "someURL")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu_get(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = mambuconnector.MambuConnectorREST()

        mcrest.mambu_get("12345", "someURL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL/12345".format(apiurl),
            params={},
            headers=mcrest._headers)

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu_get_all(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = mambuconnector.MambuConnectorREST()

        mcrest.mambu_get_all("someURL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL".format(apiurl),
            params={"paginationDetails": "OFF",
                    "detailsLevel": "BASIC"},
            headers=mcrest._headers)

        mcrest.mambu_get_all(
            "someURL",
            filters={"one": "two"},
            offset=10, limit=100, sortBy="id:ASC")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL".format(apiurl),
            params={"paginationDetails": "OFF",
                    "detailsLevel": "BASIC",
                    "offset": 10,
                    "limit": 100,
                    "sortBy": "id:ASC",
                    "one": "two"},
            headers=mcrest._headers)

    def test_mambu_get_all_validations(self):
        mcrest = mambuconnector.MambuConnectorREST()

        with self.assertRaisesRegex(MambuPyError, r"^offset must be integer"):
            mcrest.mambu_get_all(
                "someURL",
                offset="10")

        with self.assertRaisesRegex(MambuPyError, r"^limit must be integer"):
            mcrest.mambu_get_all(
                "someURL",
                limit="100")

        with self.assertRaisesRegex(
            MambuPyError,
            "paginationDetails must be in \['ON', 'OFF'\]"
        ):
            mcrest.mambu_get_all(
                "someURL",
                paginationDetails="NO")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^detailsLevel must be in \['BASIC', 'FULL'\]"):
            mcrest.mambu_get_all(
                "someURL",
                detailsLevel="fullDetails")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^sortBy must be a string with format 'field1:ASC,field2:DESC'"
        ):
            mcrest.mambu_get_all(
                "someURL",
                sortBy=12345)

        with self.assertRaisesRegex(
            MambuPyError,
            r"^sortBy must be a string with format 'field1:ASC,field2:DESC'"
        ):
            mcrest.mambu_get_all(
                "someURL",
                sortBy="invalidString")

        with self.assertRaisesRegex(
            MambuPyError, r"^filters must be a dictionary"
        ):
            mcrest.mambu_get_all(
                "someURL",
                filters=["12345", "ek12345"])


if __name__ == "__main__":
    unittest.main()
