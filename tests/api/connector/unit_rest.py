import copy
import os
import sys
import unittest

import mock
import requests

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api.connector import rest
from MambuPy.mambuutil import (MambuCommError, MambuError,
                               MambuPyError, apiurl)


def app_json_headers():
    headers = copy.copy(rest.MambuConnectorREST._headers)
    headers["Content-Type"] = "application/json"
    return headers


class MambuConnectorREST(unittest.TestCase):
    def test_properties(self):
        mcrest = rest.MambuConnectorREST()

        self.assertEqual(mcrest._tenant, apiurl)
        self.assertEqual(mcrest._headers["Accept"], "application/vnd.mambu.v2+json")
        self.assertEqual(mcrest._headers["Authorization"][:6], "Basic ")

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_GET(self, mock_requests):
        mock_requests.request().status_code = 200

        mock_requests.request().content = b"""Execute order 66"""
        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("GET", "someURL", params={"limit": 0})
        mock_requests.request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 0},
            data=None,
            headers=rest.MambuConnectorREST._headers,
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_POST_nojsondump(self, mock_requests, mock_uuid):
        mock_requests.request().status_code = 200
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO"

        mock_requests.request().content = b"""Execute order 66"""
        headers = app_json_headers()
        headers["Idempotency-Key"] = "r2d2-n-c3pO"
        data = mock.Mock("non-jsonable")

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data=data)

        mock_requests.request.assert_called_with(
            "POST", "someURL", params={}, data=data, headers=headers
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_content_type(self, mock_requests):
        mock_requests.request().status_code = 200

        headers = copy.deepcopy(rest.MambuConnectorREST._headers)
        headers["Content-Type"] = "application/light-saber"
        mock_requests.request().content = b"""Execute order 66"""

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("GET", "someURL", content_type="application/light-saber")

        mock_requests.request.assert_called_with(
            "GET", "someURL", params={}, data=None, headers=headers
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_w_body(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.request().status_code = 200

        mock_requests.request().content = b"""Execute order 66"""
        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data={"Commander": "Cody"})
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"
        mock_requests.request.assert_called_with(
            "POST", "someURL", params={}, data='{"Commander": "Cody"}', headers=headers
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_400(self, mock_requests):
        mock_requests.request().status_code = 400

        mock_requests.request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi"}]}
"""
        mcrest = rest.MambuConnectorREST()
        with self.assertRaisesRegex(MambuError, r"66 \(400\) - Kill the Jedi"):
            mcrest.__request("GET", "someURL")

        mock_requests.request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi",
      "errorSource": "Palpatine"}]}
"""
        mcrest = rest.MambuConnectorREST()
        with self.assertRaisesRegex(
            MambuError, r"^66 \(400\) - Kill the Jedi \(Palpatine\)$"
        ):
            mcrest.__request("GET", "someURL")

    @mock.patch("MambuPy.api.connector.rest.time")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_retries(self, mock_requests, mock_time):
        # everything OK! no retries done
        mcrest = rest.MambuConnectorREST()
        mock_requests.request().status_code = 200
        mock_requests.request().content = b"""200!"""
        mock_requests.request.reset_mock()
        mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, 1)
        self.assertEqual(mcrest.retries, 0)
        mock_time.sleep.assert_called_once_with(0)

        # request throws RequestException (any exception from requests module
        # inherits from this one)
        mcrest = rest.MambuConnectorREST()
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.request.side_effect = requests.exceptions.RequestException(
            "req exc"
        )
        mock_time.sleep.reset_mock()
        mock_requests.request.reset_mock()
        with self.assertRaisesRegex(MambuCommError, r"^Comm error with Mambu: req exc$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)
        self.assertEqual(mock_time.sleep.call_count, mcrest._RETRIES + 1)
        for x in range(mcrest._RETRIES + 1):
            mock_time.sleep.assert_any_call(x)

        # request throws unknown Exception
        mcrest = rest.MambuConnectorREST()
        mock_requests.request.side_effect = Exception("unknown exc")
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuCommError, r"^Unknown error with Mambu: unknown exc$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)

        # error 400
        mcrest = rest.MambuConnectorREST()
        mock_requests.request.side_effect = None
        mock_requests.request().status_code = 400
        mock_requests.request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi"}]}
"""
        mock_requests.reset_mock()
        with self.assertRaisesRegex(MambuError, r"^66 \(400\) - Kill the Jedi$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, 1)
        self.assertEqual(mcrest.retries, 0)

        # error 500
        mock_requests.request().status_code = 500
        mcrest = rest.MambuConnectorREST()
        mock_requests.reset_mock()
        with self.assertRaisesRegex(MambuError, r"^66 \(500\) - Kill the Jedi$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)

        # error 500, jsondecodeerror
        mock_requests.request().content = b"""Some really unknown error"""
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuError, r"^UNKNOWN \(500\) - Some really unknown error$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)

    def test___validate_query_params(self):
        mcrest = rest.MambuConnectorREST()

        params = mcrest.__validate_query_params()
        self.assertEqual(params, {})

        params = mcrest.__validate_query_params(
            offset=0, limit=100, paginationDetails="ON", detailsLevel="BASIC"
        )
        self.assertEqual(
            params,
            {
                "offset": 0,
                "limit": 100,
                "paginationDetails": "ON",
                "detailsLevel": "BASIC",
            },
        )

        with self.assertRaisesRegex(MambuPyError, r"^offset must be integer"):
            mcrest.__validate_query_params(offset="10")

        with self.assertRaisesRegex(MambuPyError, r"^limit must be integer"):
            mcrest.__validate_query_params(limit="100")

        with self.assertRaisesRegex(
            MambuPyError, "paginationDetails must be in \['ON', 'OFF'\]"
        ):
            mcrest.__validate_query_params(paginationDetails="NO")

        with self.assertRaisesRegex(
            MambuPyError, r"^detailsLevel must be in \['BASIC', 'FULL'\]"
        ):
            mcrest.__validate_query_params(detailsLevel="fullDetails")


if __name__ == "__main__":
    unittest.main()
