import copy
import json
import mock
import os
import sys
import unittest

import requests

sys.path.insert(0, os.path.abspath("."))

from MambuPy.mambuutil import (
    apiurl,
    MambuPyError, MambuError, MambuCommError,
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



class MambuConnectorWriter(unittest.TestCase):
    def test_mambu_upload_document(self):
        self.assertEqual(
            hasattr(mambuconnector.MambuConnectorWriter, "mambu_upload_document"),
            True)
        with self.assertRaises(NotImplementedError):
            mambuconnector.MambuConnectorWriter.mambu_upload_document(
                None, "OWNER", "id", "path/filename", "title", "notes")



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

    @mock.patch("MambuPy.api.mambuconnector.uuid")
    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_POST_nojsondump(self, mock_requests, mock_uuid):
        mock_requests.request().status_code = 200
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO"

        mock_requests.request().content = b"""Execute order 66"""
        headers = app_json_headers()
        headers["Idempotency-Key"] = "r2d2-n-c3pO"
        data = mock.Mock("non-jsonable")

        mcrest = mambuconnector.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data=data)

        mock_requests.request.assert_called_with(
            "POST",
            "someURL",
            params={},
            data=data,
            headers=headers)
        self.assertEqual(resp, b"Execute order 66")


    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_content_type(self, mock_requests):
        mock_requests.request().status_code = 200

        headers = copy.deepcopy(mambuconnector.MambuConnectorREST._headers)
        headers["Content-Type"] = "application/light-saber"
        mock_requests.request().content = b"""Execute order 66"""

        mcrest = mambuconnector.MambuConnectorREST()
        resp = mcrest.__request("GET", "someURL", content_type="application/light-saber")

        mock_requests.request.assert_called_with(
            "GET",
            "someURL",
            params={},
            data=None,
            headers=headers)
        self.assertEqual(resp, b"Execute order 66")

    @mock.patch("MambuPy.api.mambuconnector.uuid")
    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_w_body(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.request().status_code = 200

        mock_requests.request().content = b"""Execute order 66"""
        mcrest = mambuconnector.MambuConnectorREST()
        resp = mcrest.__request("POST", "someURL", data={"Commander": "Cody"})
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"
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
        with self.assertRaisesRegex(MambuError, r"66 \(400\) - Kill the Jedi"):
            mcrest.__request("GET", "someURL")

        mock_requests.request().content = b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi",
      "errorSource": "Palpatine"}]}
"""
        mcrest = mambuconnector.MambuConnectorREST()
        with self.assertRaisesRegex(
            MambuError, r"^66 \(400\) - Kill the Jedi \(Palpatine\)$"
        ):
            mcrest.__request("GET", "someURL")

    @mock.patch("MambuPy.api.mambuconnector.time")
    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu___request_retries(self, mock_requests, mock_time):
        # everything OK! no retries done
        mcrest = mambuconnector.MambuConnectorREST()
        mock_requests.request().status_code = 200
        mock_requests.request().content= b"""200!"""
        mock_requests.request.reset_mock()
        mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, 1)
        self.assertEqual(mcrest.retries, 0)
        mock_time.sleep.assert_called_once_with(0)

        # request throws RequestException (any exception from requests module
        # inherits from this one)
        mcrest = mambuconnector.MambuConnectorREST()
        mock_requests.exceptions.RequestException = requests.exceptions.RequestException
        mock_requests.request.side_effect = requests.exceptions.RequestException(
            "req exc")
        mock_time.sleep.reset_mock()
        mock_requests.request.reset_mock()
        with self.assertRaisesRegex(
            MambuCommError,
            r"^Comm error with Mambu: req exc$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)
        self.assertEqual(mock_time.sleep.call_count, mcrest._RETRIES + 1)
        for x in range(mcrest._RETRIES + 1):
            mock_time.sleep.assert_any_call(x)

        # request throws unknown Exception
        mcrest = mambuconnector.MambuConnectorREST()
        mock_requests.request.side_effect = Exception("unknown exc")
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuCommError,
            r"^Unknown error with Mambu: unknown exc$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)

        # error 400
        mcrest = mambuconnector.MambuConnectorREST()
        mock_requests.request.side_effect = None
        mock_requests.request().status_code = 400
        mock_requests.request().content= b"""
{"errors":
    [{"errorCode": "66",
      "errorReason": "Kill the Jedi"}]}
"""
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuError, r"^66 \(400\) - Kill the Jedi$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, 1)
        self.assertEqual(mcrest.retries, 0)

        # error 500
        mock_requests.request().status_code = 500
        mcrest = mambuconnector.MambuConnectorREST()
        mock_requests.reset_mock()
        with self.assertRaisesRegex(MambuError, r"^66 \(500\) - Kill the Jedi$"):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)

        # error 500, jsondecodeerror
        mock_requests.request().content= b"""Some really unknown error"""
        mock_requests.reset_mock()
        with self.assertRaisesRegex(
            MambuError, r"^UNKNOWN \(500\) - Some really unknown error$"
        ):
            mcrest.__request("GET", "someURL")
        self.assertEqual(mock_requests.request.call_count, mcrest._RETRIES + 1)
        self.assertEqual(mcrest.retries, mcrest._RETRIES)

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
            r"^detailsLevel must be in \['BASIC', 'FULL'\]"
        ):
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
            params={"detailsLevel": "BASIC"},
            data=None,
            headers=mcrest._headers)

        mcrest.mambu_get("12345", "someURL", "FULL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL/12345".format(apiurl),
            params={"detailsLevel": "FULL"},
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

    @mock.patch("MambuPy.api.mambuconnector.uuid")
    @mock.patch("MambuPy.api.mambuconnector.requests")
    def test_mambu_search(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"
        mock_requests.request().status_code = 200
        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"

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

    @mock.patch("MambuPy.api.mambuconnector.open")
    @mock.patch("MambuPy.api.mambuconnector.uuid")
    @mock.patch("MambuPy.api.mambuconnector.requests")
    @mock.patch("MambuPy.api.mambuconnector.MultipartEncoder")
    def test_mambu_upload_document(
        self, mock_multipartencoder, mock_requests, mock_uuid, mock_open
    ):
        with open("/tmp/selfie.png", "w") as f:
            f.write("yoda yo yo")
        mock_uuid.uuid4.return_value = "r2d2-n-c3pO"
        mock_requests.request().status_code = 200
        encoder = lambda: None; encoder.content_type = 'multipart/form-data; boundary=outer_rim'
        mock_multipartencoder.return_value = encoder

        mcrest = mambuconnector.MambuConnectorREST()

        mcrest.mambu_upload_document(
            "JEDI_ORDER",
            "Yoda",
            "/tmp/selfie.png",
            "my_selfie.png",
            "Some selfie")

        headers = app_json_headers()
        headers["Idempotency-Key"] = "r2d2-n-c3pO"
        headers["Content-Type"] = "multipart/form-data; boundary=outer_rim"
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/documents".format(apiurl),
            params={},
            data=encoder,
            headers=headers)
        mock_multipartencoder.assert_called_with(
            fields={
                'ownerType': "JEDI_ORDER",
                'id': "Yoda",
                'name': "my_selfie.png",
                'notes': "Some selfie",
                'file': ("selfie.png",
                         mock_open("/tmp/selfie.png", "rb"),
                         "image/png")})

        os.remove("/tmp/selfie.png")


if __name__ == "__main__":
    unittest.main()
