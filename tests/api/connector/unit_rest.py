import base64
import copy
import logging
import os
import sys
import unittest

import mock
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api.connector import rest
from MambuPy.mambuutil import (MambuCommError, MambuError,
                               MambuPyError, apiurl, activate_request_session_objects)


logging.disable(logging.CRITICAL)


def app_json_headers():
    headers = copy.copy(rest.MambuConnectorREST()._headers)
    headers["Content-Type"] = "application/json"
    return headers


def app_default_headers():
    headers = copy.copy(rest.MambuConnectorREST()._headers)
    return headers


class TestSessionSingleton(unittest.TestCase):
    """Test cases for SessionSingleton class."""

    def setUp(self):
        """Set up test cases."""
        # Reset the singleton instance before each test
        rest.SessionSingleton._SessionSingleton__instance = None
        rest.SessionSingleton._SessionSingleton__session = None

    def test_singleton_instance(self):
        """Test that SessionSingleton maintains a single instance."""
        session1 = rest.SessionSingleton()
        session2 = rest.SessionSingleton()
        self.assertIs(session1, session2)

    def test_get_session_creates_new_session(self):
        """Test that get_session creates a new session when none exists."""
        session = rest.SessionSingleton()
        http_session = session.get_session()
        self.assertIsInstance(http_session, requests.Session)
        self.assertIsNotNone(http_session)

    def test_get_session_returns_existing_session(self):
        """Test that get_session returns the same session instance."""
        session = rest.SessionSingleton()
        http_session1 = session.get_session()
        http_session2 = session.get_session()
        self.assertIs(http_session1, http_session2)

    def test_session_has_retry_strategy(self):
        """Test that the session has proper retry strategy configured."""
        session = rest.SessionSingleton()
        http_session = session.get_session()

        # Get the adapter for https
        adapter = http_session.get_adapter('https://')
        self.assertIsInstance(adapter, HTTPAdapter)

        # Check retry strategy
        retry = adapter.max_retries
        self.assertIsInstance(retry, Retry)
        self.assertEqual(retry.total, 5)
        self.assertEqual(retry.backoff_factor, 1)
        self.assertIn(429, retry.status_forcelist)
        self.assertIn(500, retry.status_forcelist)
        self.assertIn(502, retry.status_forcelist)
        self.assertIn(503, retry.status_forcelist)
        self.assertIn(504, retry.status_forcelist)


class MambuConnectorREST(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        # Reset the singleton instance before each test
        rest.SessionSingleton._SessionSingleton__instance = None
        rest.SessionSingleton._SessionSingleton__session = None

    def test_properties(self):
        mcrest = rest.MambuConnectorREST()

        self.assertEqual(mcrest._tenant, apiurl)
        self.assertEqual(mcrest._headers["Accept"], "application/vnd.mambu.v2+json")
        self.assertEqual(mcrest._headers["Authorization"][:6], "Basic ")

    @mock.patch("MambuPy.mambuutil")
    def test___init__(self, mock_mambuutil):
        basic_auth = base64.b64encode(
            bytes("{}:{}".format(rest.apiuser, rest.apipwd), "utf-8")).decode()
        mcrest = rest.MambuConnectorREST()
        self.assertEqual(
            mcrest._headers,
            {'Accept': 'application/vnd.mambu.v2+json',
             'Authorization': 'Basic {}'.format(basic_auth)})
        self.assertEqual(mcrest._tenant, rest.apiurl)

        basic_auth = base64.b64encode(
            bytes("{}:{}".format("my_user", "my_pwd"), "utf-8")).decode()
        mcrest = rest.MambuConnectorREST(
            user="my_user", pwd="my_pwd", url="my_url")
        self.assertEqual(
            mcrest._headers,
            {'Accept': 'application/vnd.mambu.v2+json',
             'Authorization': 'Basic {}'.format(basic_auth)})
        self.assertEqual(mcrest._tenant, "my_url")

    @mock.patch("MambuPy.api.connector.rest.activate_request_session_objects")
    def test_connector_uses_session_when_enabled(self, mock_activate):
        """Test that connector uses session when enabled."""
        mock_activate.lower.return_value = "true"
        with mock.patch.object(rest.SessionSingleton, 'get_session') as mock_get_session:
            mock_get_session.return_value = requests.Session()
            connector = rest.MambuConnectorREST()
            self.assertIsNotNone(connector._session)
            self.assertIsInstance(connector._session, requests.Session)

    @mock.patch("MambuPy.api.connector.rest.activate_request_session_objects")
    def test_connector_doesnt_use_session_when_disabled(self, mock_activate):
        """Test that connector doesn't use session when disabled."""
        mock_activate.lower.return_value = "false"
        connector = rest.MambuConnectorREST()
        self.assertIsNone(connector._session)

    @mock.patch("MambuPy.api.connector.rest.activate_request_session_objects")
    @mock.patch("requests.Session.request")
    def test_connector_uses_session_for_requests(self, mock_request, mock_activate):
        """Test that connector uses session for requests when enabled."""
        mock_activate.lower.return_value = "true"
        # Setup mock response
        mock_response = mock.MagicMock()
        mock_response.content = b'{"data": "test"}'
        mock_response.raise_for_status = mock.MagicMock()
        mock_request.return_value = mock_response

        with mock.patch.object(rest.SessionSingleton, 'get_session') as mock_get_session:
            mock_session = requests.Session()
            mock_get_session.return_value = mock_session
            connector = rest.MambuConnectorREST()
            connector.mambu_get('test_id', 'test_prefix')

            # Verify session was used
            mock_request.assert_called_once()
            self.assertIsNotNone(connector._session)

    @mock.patch("MambuPy.api.connector.rest.activate_request_session_objects")
    @mock.patch("requests.Session.request")
    def test_connector_creates_new_session_for_each_request_when_disabled(self, mock_request, mock_activate):
        """Test that connector creates new session for each request when disabled."""
        mock_activate.lower.return_value = "false"
        # Setup mock response
        mock_response = mock.MagicMock()
        mock_response.content = b'{"data": "test"}'
        mock_response.raise_for_status = mock.MagicMock()
        mock_request.return_value = mock_response

        connector = rest.MambuConnectorREST()
        connector.mambu_get('test_id', 'test_prefix')

        # Verify new session was created
        mock_request.assert_called_once()
        self.assertIsNone(connector._session)

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

    @mock.patch("MambuPy.api.connector.rest.requests.Session")
    def test_mambu___request_404(self, mock_request_session):
        mock_request_session().request().status_code = 404
        mock_request_session().request().content = b"""
{"returnCode": "66",
 "returnStatus": "Kill the Jedi"}
"""
        mock_request_session().request().raise_for_status.side_effect = \
            requests.exceptions.HTTPError("404 not found")

        mcrest = rest.MambuConnectorREST()
        with self.assertRaisesRegex(MambuError, r"66 \(404\) - Kill the Jedi"):
            mcrest.__request("GET", "someURL")

        mock_request_session().request().content = b"""
{"returnCode": "66",
 "returnStatus": "Kill the Jedi",
 "errorSource": "Palpatine"}
"""
        mcrest = rest.MambuConnectorREST()
        with self.assertRaisesRegex(
            MambuError, r"^66 \(404\) - Kill the Jedi \(Palpatine\)$"
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
            params={"limit": 50, "offset": 0},
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
            params={"limit": 50, "offset": 0},
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

        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 50

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

        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 50

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

        rest.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 50

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
