import json
import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy.api.connector import rest
from MambuPy.mambuutil import (MambuError,
                               MambuPyError, apiurl)

from unit_rest import app_json_headers


class MambuConnectorReaderREST(unittest.TestCase):
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_get(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_get("12345", "someURL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL/12345".format(apiurl),
            params={"detailsLevel": "BASIC"},
            data=None,
            headers=mcrest._headers,
        )

        mcrest.mambu_get("12345", "someURL", "FULL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL/12345".format(apiurl),
            params={"detailsLevel": "FULL"},
            data=None,
            headers=mcrest._headers,
        )

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_get_all(self, mock_requests):
        mock_requests.request().status_code = 200
        mock_requests.request().content = b"[]"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_get_all("someURL")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL".format(apiurl),
            params={"paginationDetails": "OFF", "detailsLevel": "BASIC",
                    "limit": 1000, "offset": 0},
            data=None,
            headers=mcrest._headers,
        )

        mcrest.mambu_get_all(
            "someURL", filters={"one": "two"}, offset=10, limit=100, sortBy="id:ASC"
        )

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL".format(apiurl),
            params={
                "paginationDetails": "OFF",
                "detailsLevel": "BASIC",
                "offset": 10,
                "limit": 100,
                "sortBy": "id:ASC",
                "one": "two",
            },
            data=None,
            headers=mcrest._headers,
        )

        mcrest.mambu_get_all("someURL", **{"someParam": "someValue"})
        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/someURL".format(apiurl),
            params={"paginationDetails": "OFF", "detailsLevel": "BASIC", "someParam": "someValue",
                    "limit": 1000, "offset": 0},
            data=None,
            headers=mcrest._headers,
        )

    def test_mambu_get_all_validations(self):
        mcrest = rest.MambuConnectorREST()

        with self.assertRaisesRegex(
            MambuPyError, r"^sortBy must be a string with format 'field1:ASC,field2:DESC'"
        ):
            mcrest.mambu_get_all("someURL", sortBy=12345)

        with self.assertRaisesRegex(
            MambuPyError, r"^sortBy must be a string with format 'field1:ASC,field2:DESC'"
        ):
            mcrest.mambu_get_all("someURL", sortBy="invalidString")

        with self.assertRaisesRegex(MambuPyError, r"^filters must be a dictionary"):
            mcrest.mambu_get_all("someURL", filters=["12345", "ek12345"])

    @mock.patch("MambuPy.api.connector.rest.uuid")
    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_search(self, mock_requests, mock_uuid):
        mock_uuid.uuid4.return_value = "An UUID"

        mock_requests.request().status_code = 200
        mock_requests.request().content = b"[]"

        headers = app_json_headers()
        headers["Idempotency-Key"] = "An UUID"

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_search("someURL")
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF", "detailsLevel": "BASIC",
                    "limit": 1000, "offset": 0},
            data="{}",
            headers=headers,
        )

        mcrest.mambu_search("someURL", offset=10, limit=100)
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={
                "paginationDetails": "OFF",
                "detailsLevel": "BASIC",
                "offset": 10,
                "limit": 100,
            },
            data="{}",
            headers=headers,
        )

        filterCriteria = [
            {"field": "someField", "operator": "EQUALS", "value": "someValue"}
        ]
        mcrest.mambu_search("someURL", filterCriteria=filterCriteria)
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF", "detailsLevel": "BASIC",
                    "limit": 1000, "offset": 0},
            data=json.dumps({"filterCriteria": filterCriteria}),
            headers=headers,
        )

        sortingCriteria = {"field": "someField", "order": "ASC"}
        mcrest.mambu_search(
            "someURL", filterCriteria=filterCriteria, sortingCriteria=sortingCriteria
        )
        mock_requests.request.assert_called_with(
            "POST",
            "https://{}/api/someURL:search".format(apiurl),
            params={"paginationDetails": "OFF", "detailsLevel": "BASIC",
                    "limit": 1000, "offset": 0},
            data=json.dumps(
                {"filterCriteria": filterCriteria, "sortingCriteria": sortingCriteria}
            ),
            headers=headers,
        )

    def test_mambu_search_validations(self):
        mcrest = rest.MambuConnectorREST()

        # filterCriteria
        with self.assertRaisesRegex(
            MambuPyError, r"^filterCriteria must be a list of dictionaries"
        ):
            mcrest.mambu_search("someURL", filterCriteria="filterCriteria")

        with self.assertRaisesRegex(
            MambuPyError, r"^filterCriteria must be a list of dictionaries"
        ):
            mcrest.mambu_search("someURL", filterCriteria=["filterCriteria"])

        with self.assertRaisesRegex(
            MambuPyError,
            r"^a filterCriteria must have a field and an operator, member of \[",
        ):
            mcrest.mambu_search("someURL", filterCriteria=[{}])

        # sortingCriteria
        with self.assertRaisesRegex(
            MambuPyError, r"^sortingCriteria must be a dictionary"
        ):
            mcrest.mambu_search("someURL", sortingCriteria="sortingCriteria")

        with self.assertRaisesRegex(
            MambuPyError,
            r"^sortingCriteria must have a field and an order, member of \['ASC', 'DESC'\]",
        ):
            mcrest.mambu_search("someURL", sortingCriteria={})

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_get_documents_metadata(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_get_documents_metadata(
            "entID", "MY_OWNER_TYPE",
            offset=1, limit=2, paginationDetails="ON")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/documents/documentsMetadata".format(apiurl),
            params={
                "entity": "MY_OWNER_TYPE", "ownerKey": "entID",
                "offset": 1, "limit": 2, "paginationDetails": "ON"},
            data=None,
            headers=mcrest._headers)

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_loanaccount_getSchedule(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_loanaccount_getSchedule("loanid")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/loans/loanid/schedule".format(apiurl),
            params={},
            data=None,
            headers=mcrest._headers)

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_get_customfield(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = rest.MambuConnectorREST()

        mcrest.mambu_get_customfield("cfid")

        mock_requests.request.assert_called_with(
            "GET",
            "https://{}/api/customfields/{}".format(apiurl, "cfid"),
            params={},
            data=None,
            headers=mcrest._headers)

    @mock.patch("MambuPy.api.connector.rest.requests")
    def test_mambu_get_comments(self, mock_requests):
        mock_requests.request().status_code = 200

        mcrest = rest.MambuConnectorREST()

        for owner_type in [
                "CLIENT",
                "GROUP",
                "LOAN_PRODUCT",
                "SAVINGS_PRODUCT",
                "CENTRE",
                "BRANCH",
                "USER",
                "LOAN_ACCOUNT",
                "DEPOSIT_ACCOUNT",
                "ID_DOCUMENT",
                "LINE_OF_CREDIT",
                "GL_JOURNAL_ENTRY"
        ]:
            mock_requests.reset_mock()
            mcrest.mambu_get_comments(
                "OWNER_ID", owner_type,
                offset=1, limit=2, paginationDetails="ON")
            mock_requests.request.assert_called_with(
                "GET",
                "https://{}/api/comments".format(apiurl),
                params={
                    "ownerType": owner_type, "ownerKey": "OWNER_ID",
                    "offset": 1, "limit": 2, "paginationDetails": "ON"},
                data=None,
                headers=mcrest._headers)

        with self.assertRaisesRegex(
                MambuError, r"Owner MY_OWNER_TYPE not allowed"):
            mcrest.mambu_get_comments("OWNER_ID", "MY_OWNER_TYPE")


if __name__ == "__main__":
    unittest.main()
