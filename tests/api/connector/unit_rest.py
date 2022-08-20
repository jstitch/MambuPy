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
    headers = copy.copy(rest.MambuConnectorREST()._headers)
    headers["Content-Type"] = "application/json"
    return headers


def app_default_headers():
    headers = copy.copy(rest.MambuConnectorREST()._headers)
    return headers


class MambuConnectorREST(unittest.TestCase):
    def test_properties(self):
        mcrest = rest.MambuConnectorREST()

        self.assertEqual(mcrest._tenant, apiurl)
        self.assertEqual(mcrest._headers["Accept"], "application/vnd.mambu.v2+json")
        self.assertEqual(mcrest._headers["Authorization"][:6], "Basic ")

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_GET(self, mock_requests):
        mock_requests.Session().request().status_code = 200

        mock_requests.Session().request().content = b"""Execute order 66"""
        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("GET", "someURL", params={"limit": 0})
        mock_requests.Session().request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 0},
            data=None,
            headers=app_default_headers(),
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_POST_nojsondump(self, mock_requests, mock_uuid):
        mock_requests.Session().request().status_code = 200
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO"

        mock_requests.Session().request().content = b"""Execute order 66"""
        headers = app_json_headers()
        headers["Idempotency-Key"] = "r2d2-n-c3pO"
        data = mock.Mock("non-jsonable")

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data=data)

        mock_requests.Session().request.assert_called_with(
            "POST", "someURL", params={}, data=data, headers=headers
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_content_type(self, mock_requests):
        mock_requests.Session().request().status_code = 200

        headers = app_default_headers()
        headers["Content-Type"] = "application/light-saber"
        mock_requests.Session().request().content = b"""Execute order 66"""

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("GET", "someURL", content_type="application/light-saber")

        mock_requests.Session().request.assert_called_with(
            "GET", "someURL", params={}, data=None, headers=headers
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_w_body(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.Session().request().status_code = 200

        mock_requests.Session().request().content = b"""Execute order 66"""
        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data={"Commander": "Cody"})
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"
        mock_requests.Session().request.assert_called_with(
            "POST", "someURL", params={}, data='{"Commander": "Cody"}', headers=headers
        )
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.connector.rest.requests.Session")
    def test_mambu___request_400(self, mock_request_session):
        mock_request_session().request().status_code = 400
        mock_request_session().request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi"}]}
"""
        mock_request_session().request().raise_for_status.side_effect = \
            requests.exceptions.HTTPError("404 not found")

        mcrest = rest.MambuConnectorREST()
        with self.assertRaisesRegex(MambuError, r"66 \(400\) - Kill the Jedi"):
            mcrest.__request("GET", "someURL")

        mock_request_session().request().content = b"""
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

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___request_retries(self, mock_requests):
        # everything OK! no retries done
        mcrest = rest.MambuConnectorREST()
        mock_requests.Session().request().status_code = 200
        mock_requests.Session().request().content = b"""200!"""
        mock_requests.Session().request.reset_mock()
        mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.Session().request.call_count, 1)

        # request throws RequestException (any exception from requests module
        # inherits from this one)
        mcrest = rest.MambuConnectorREST()
        mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.exceptions.RetryError = requests.exceptions.RetryError
        mock_requests.Session().request.side_effect =\
            requests.exceptions.RequestException("req exc")
        mock_requests.Session().request.reset_mock()
        with self.assertRaisesRegex(
                MambuCommError, r"^Unknown comm error with Mambu: req exc$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.Session().request.call_count, 1)

        # request throws unknown Exception
        mcrest = rest.MambuConnectorREST()
        mock_requests.Session().request.side_effect = Exception("unknown exc")
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuCommError, r"^Unknown comm error with Mambu: unknown exc$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.Session().request.call_count, 1)

        # error 400
        mcrest = rest.MambuConnectorREST()
        mock_requests.Session().request.side_effect = None
        mock_requests.Session().request().status_code = 400
        mock_requests.Session().request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi"}]}
"""
        mock_requests.Session().request().raise_for_status.side_effect = \
            requests.exceptions.HTTPError("404 not found")
        mock_requests.Session().reset_mock()
        with self.assertRaisesRegex(
                MambuError, r"^66 \(400\) - Kill the Jedi$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.Session().request.call_count, 1)

        # error 500
        mock_requests.Session().request().status_code = 500
        mock_requests.Session().request().raise_for_status.side_effect = \
            requests.exceptions.HTTPError("502 server error")
        mcrest = rest.MambuConnectorREST()
        mock_requests.Session().reset_mock()
        with self.assertRaisesRegex(MambuError, r"^66 \(500\) - Kill the Jedi$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.Session().request.call_count, 1)

        # error 500, jsondecodeerror
        mock_requests.Session().request().content = b"""Some really unknown error"""
        mock_requests.Session().request().raise_for_status.side_effect = \
            requests.exceptions.HTTPError("500 unkown error")
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuError, r"^UNKNOWN \(500\) - Some really unknown error$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.Session().request.call_count, 1)

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___list_request(self, mock_requests):
        mock_requests.Session().request().status_code = 200
        mock_requests.Session().request().content = b"""\
[{"hello":"world"},\
{"goodbye":"world"}]"""
        mock_requests.reset_mock()

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__list_request("GET", "someURL")
        mock_requests.Session().request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 1000, "offset": 0},
            data=None,
            headers=app_default_headers(),
        )
        self.assertEqual(mock_requests.Session().request.call_count, 1)
        self.assertEqual(resp, b'[{"hello":"world"},{"goodbye":"world"}]')

        mcrest.__list_request(
            "GET", "someURL", params={"limit": 1, "offset": 0})
        mock_requests.Session().request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 1, "offset": 0},
            data=None,
            headers=app_default_headers(),
        )

        mcrest.__list_request(
            "GET", "someURL", params={"limit": 1, "offset": 1})
        mock_requests.Session().request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 1, "offset": 1},
            data=None,
            headers=app_default_headers(),
        )

        mcrest.__list_request("GET", "someURL", data={"some": "data"})
        mock_requests.Session().request.assert_called_with(
            "GET",
            "someURL",
            params={"limit": 1000, "offset": 0},
            data='{"some": "data"}',
            headers=app_default_headers(),
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___list_request_w_limit_even(self, mock_requests):
        response_content = b"""\
[{"my my":"hey hey"},\
{"rock n' roll":"is here to stay"},\
{"it's better to burnout":"than to fade away"},\
{"my my":"hey hey"},\
{"hey hey":"my my"},\
{"rock n' roll":"will never die"},\
{"there's more to the picture":"than meets the eye"},\
{"hey hey":"my my"}]"""
        resp1 = requests.models.Response()
        resp1.status_code = 200
        resp1._content = b"""\
[{"my my":"hey hey"},\
{"rock n' roll":"is here to stay"},\
{"it's better to burnout":"than to fade away"},\
{"my my":"hey hey"}]"""
        resp2 = requests.models.Response()
        resp2.status_code = 200
        resp2._content = b"""\
[{"hey hey":"my my"},\
{"rock n' roll":"will never die"},\
{"there's more to the picture":"than meets the eye"},\
{"hey hey":"my my"}]"""
        resp3 = requests.models.Response()
        resp3.status_code = 200
        resp3._content = b"[]"

        mock_requests.Session().request.side_effect = [resp1, resp2, resp3]
        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 4

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__list_request("GET", "someURL")
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 4, "offset": 0},
            data=None,
            headers=app_default_headers(),
        )
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 4, "offset": 4},
            data=None,
            headers=app_default_headers(),
        )
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 4, "offset": 8},
            data=None,
            headers=app_default_headers(),
        )
        self.assertEqual(mock_requests.Session().request.call_count, 3)
        self.assertEqual(resp, response_content)

        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___list_request_w_limit_odd(self, mock_requests):
        response_content = b"""\
[{"my my":"hey hey"},\
{"rock n' roll":"is here to stay"},\
{"it's better to burnout":"than to fade away"},\
{"my my":"hey hey"},\
{"hey hey":"my my"},\
{"rock n' roll":"will never die"},\
{"there's more to the picture":"than meets the eye"},\
{"hey hey":"my my"}]"""
        resp1 = requests.models.Response()
        resp1.status_code = 200
        resp1._content = b"""\
[{"my my":"hey hey"},\
{"rock n' roll":"is here to stay"},\
{"it's better to burnout":"than to fade away"}]"""
        resp2 = requests.models.Response()
        resp2.status_code = 200
        resp2._content = b"""\
[{"my my":"hey hey"},\
{"hey hey":"my my"},\
{"rock n' roll":"will never die"}]"""
        resp3 = requests.models.Response()
        resp3.status_code = 200
        resp3._content = b"""\
[{"there's more to the picture":"than meets the eye"},\
{"hey hey":"my my"}]"""

        mock_requests.Session().request.side_effect = [resp1, resp2, resp3]
        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 3

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__list_request("GET", "someURL")
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 3, "offset": 0},
            data=None,
            headers=app_default_headers(),
        )
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 3, "offset": 3},
            data=None,
            headers=app_default_headers(),
        )
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 3, "offset": 6},
            data=None,
            headers=app_default_headers(),
        )
        self.assertEqual(mock_requests.Session().request.call_count, 3)
        self.assertEqual(resp, response_content)

        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu___list_request_w_limit_minor(self, mock_requests):
        response_content = b"""\
[{"my my":"hey hey"},\
{"rock n' roll":"is here to stay"},\
{"it's better to burnout":"than to fade away"},\
{"my my":"hey hey"},\
{"hey hey":"my my"}]"""
        resp1 = requests.models.Response()
        resp1.status_code = 200
        resp1._content = b"""\
[{"my my":"hey hey"},\
{"rock n' roll":"is here to stay"},\
{"it's better to burnout":"than to fade away"}]"""
        resp2 = requests.models.Response()
        resp2.status_code = 200
        resp2._content = b"""\
[{"my my":"hey hey"},\
{"hey hey":"my my"}]"""

        mock_requests.Session().request.side_effect = [resp1, resp2]
        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 3

        mcrest = rest.MambuConnectorREST()
        resp = mcrest.__list_request("GET", "someURL", params={"limit": 5})
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 3, "offset": 0},
            data=None,
            headers=app_default_headers(),
        )
        mock_requests.Session().request.assert_any_call(
            "GET",
            "someURL",
            params={"limit": 2, "offset": 3},
            data=None,
            headers=app_default_headers(),
        )
        self.assertEqual(mock_requests.Session().request.call_count, 2)
        self.assertEqual(resp, response_content)

        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000

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
