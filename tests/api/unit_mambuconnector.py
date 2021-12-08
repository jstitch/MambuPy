import copy
import json
import mock
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import (
    apiurl,
    MambuPyError, MambuError,
    PAGINATIONDETAILS,
    DETAILSLEVEL,
    )

from MambuPy.api import mambuconnector


def app_json_headers():
    headers = copy.copy(mambuconnector.MambuConnectorREST._headers)
    headers["Content-Type"] = "application/json"
    return headers


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

    def test_mambu_search(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorReader, "mambu_search"),
            True)
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorReader.mambu_search(
                [{}], {}, 0, 0, "OFF", "BASIC", "")


class MambuConnectorREST(unittest.TestCase):
    def test_properties(self):
        mcrest = mambuconnector.MambuConnectorREST()

        self.assertEqual(mcrest._tenant, apiurl)
        self.assertEqual(mcrest._headers["Accept"], "application/vnd.mambu.v2+json")
        self.assertEqual(mcrest._headers["Authorization"][:6], "Basic ")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_GET(self, mock_requests):
        mock_requests.request().status_code = 200

        mock_requests.request().content = b"""Execute order 66"""
        mcrest = mambuconnector.MambuConnectorREST()
        resp = mcrest.__request("GET", "someURL", params={"limit": 0})
        mock_requests.request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 0},
            data=None,
            headers=mambuconnector.MambuConnectorREST._headers)
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_w_body(self, mock_requests):
        mock_requests.request().status_code = 200

        mock_requests.request().content = b"""Execute order 66"""
        mcrest = mambuconnector.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data={"Commander": "Cody"})
        headers = app_json_headers()
        mock_requests.request.assert_called_with(
            "POST",
            "someURL",
            params={},
            data='{"Commander": "Cody"}',
            headers=headers)
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_400(self, mock_requests):
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

    def test___validate_query_params(self):
        mcrest = mambuconnector.MambuConnectorREST()

        params = mcrest.__validate_query_params()
        self.assertEqual(params, {})

        params = mcrest.__validate_query_params(
            offset=0, limit=100,
            paginationDetails="ON", detailsLevel="BASIC")
        self.assertEqual(
            params,
            {"offset": 0, "limit": 100,
             "paginationDetails": "ON", "detailsLevel": "BASIC"})

        with self.assertRaisesRegex(MambuPyError, r"^offset must be integer"):
            mcrest.__validate_query_params(
                offset="10")

        with self.assertRaisesRegex(MambuPyError, r"^limit must be integer"):
            mcrest.__validate_query_params(
                limit="100")

        with self.assertRaisesRegex(
            MambuPyError,
            "paginationDetails must be in \['ON', 'OFF'\]"
        ):
            mcrest.__validate_query_params(
                paginationDetails="NO")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^detailsLevel must be in \['BASIC', 'FULL'\]"):
            mcrest.__validate_query_params(
                detailsLevel="fullDetails")

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu_get(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = mambuconnector.MambuConnectorREST()

        mcrest.mambu_get("12345", "someURL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL/12345".format(apiurl),
            params={},
            data=None,
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
            data=None,
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
            data=None,
            headers=mcrest._headers)

    def test_mambu_get_all_validations(self):
        mcrest = mambuconnector.MambuConnectorREST()

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

    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu_search(self, mock_requests):
        mock_requests.request().status_code = 200
        headers = app_json_headers()

        mcrest = mambuconnector.MambuConnectorREST()

        mcrest.mambu_search("someURL")
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF",
                    "detailsLevel": "BASIC"},
            data='{}',
            headers=headers)

        mcrest.mambu_search(
            "someURL",
            offset=10, limit=100)
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF",
                    "detailsLevel": "BASIC",
                    "offset": 10,
                    "limit": 100},
            data='{}',
            headers=headers)

        filterCriteria = [
            {"field": "someField",
             "operator": "EQUALS",
             "value": "someValue"}]
        mcrest.mambu_search(
            "someURL",
            filterCriteria=filterCriteria)
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF",
                    "detailsLevel": "BASIC"},
            data=json.dumps({"filterCriteria": filterCriteria}),
            headers=headers)

        sortingCriteria = {"field": "someField",
                           "order": "ASC"}
        mcrest.mambu_search(
            "someURL",
            filterCriteria=filterCriteria,
            sortingCriteria=sortingCriteria)
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF",
                    "detailsLevel": "BASIC"},
            data=json.dumps(
                {"filterCriteria": filterCriteria,
                 "sortingCriteria": sortingCriteria}),
            headers=headers)

    def test_mambu_search_validations(self):
        mcrest = mambuconnector.MambuConnectorREST()

        # filterCriteria
        with self.assertRaisesRegex(
            MambuPyError,
            r"^filterCriteria must be a list of dictionaries"
        ):
            mcrest.mambu_search(
                "someURL",
            filterCriteria="filterCriteria")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^each filterCriteria must be a dictionary"
        ):
            mcrest.mambu_search(
                "someURL",
            filterCriteria=["filterCriteria"])

        with self.assertRaisesRegex(
            MambuPyError,
            r"^a filterCriteria must have a field and an operator, member of \["
        ):
            mcrest.mambu_search(
                "someURL",
            filterCriteria=[{}])

        # sortingCriteria
        with self.assertRaisesRegex(
            MambuPyError,
            r"^sortingCriteria must be a dictionary"
        ):
            mcrest.mambu_search(
                "someURL",
            sortingCriteria="sortingCriteria")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^sortingCriteria must have a field and an order, member of \['ASC', 'DESC'\]"
        ):
            mcrest.mambu_search(
                "someURL",
            sortingCriteria={})


if __name__ == "__main__":
    unittest.main()
