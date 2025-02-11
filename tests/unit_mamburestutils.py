# coding: utf-8
import logging
import mock
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))
logging.disable(logging.CRITICAL)

from MambuPy.rest import mambustruct, mamburestutils


class RequestsCounterTests(unittest.TestCase):
    """Requests Counter singleton tests"""

    def setUp(self):
        self.rc = mamburestutils.RequestsCounter()
        self.rc.cnt = 0

    def test_rc(self):
        """Test counter of singleton"""
        rc = mamburestutils.RequestsCounter()
        rc.reset()

        self.assertEqual(rc.cnt, 0)
        rc.add("hola")
        self.assertEqual(rc.cnt, 1)
        self.assertEqual(rc.requests, ["hola"])

        rc.reset()
        self.assertEqual(rc.cnt, 0)
        self.assertEqual(rc.requests, [])


class MambureStructIteratorTests(unittest.TestCase):
    def setUp(self):
        class test_class:
            def __init__(self, wrap):
                self.iterator = mamburestutils.MambuStructIterator(wrap)

            def __iter__(self):
                return self.iterator

        self.test_class = test_class

    def test_iterator(self):
        it = self.test_class(range(7))
        self.assertEqual(it.iterator.wrapped, range(7))
        self.assertEqual(it.iterator.offset, 0)

        for i, j in zip(it, range(7)):
            self.assertEqual(i, j)

        with self.assertRaises(StopIteration):
            it.iterator.next()


class MambuFunctionTests(unittest.TestCase):
    """mamburestutils module Functions Tests"""

    def setUp(self):
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_set_custom_field(self, requests, json, iri_to_uri):
        """Test set_custom_field"""
        with mock.patch("MambuPy.rest.mambuuser.MambuUser") as mock_mambuuser, mock.patch(
            "MambuPy.rest.mambuclient.MambuClient"
        ) as mock_mambuclient:
            mock_mambuuser.return_value = {"id": "user123"}
            mock_mambuclient.return_value = {"id": "client123"}

            # default case: any datatype
            json.loads.return_value = {
                "customFields": [
                    {
                        "customField": {
                            "state": "",
                            "name": "field",
                            "id": "fieldid",
                            "dataType": "STRING",
                        },
                        "customFieldSetGroupIndex": -1,
                        "value": "val",
                    },
                ]
            }
            ms = mambustruct.MambuStruct(
                urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
                custom_field_name="customFields",
            )
            mamburestutils.set_custom_field(ms, customfield="field")
            self.assertEqual(ms.field, "val")
            mamburestutils.set_custom_field(ms, customfield="fieldid")
            self.assertEqual(ms.fieldid, "val")

            # user_link custom field
            json.loads.return_value = {
                "customFields": [
                    {
                        "customField": {
                            "state": "",
                            "name": "field",
                            "id": "fieldid",
                            "dataType": "USER_LINK",
                        },
                        "customFieldSetGroupIndex": -1,
                        "value": "user123",
                    },
                ]
            }
            ms = mambustruct.MambuStruct(
                urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
                custom_field_name="customFields",
            )
            mamburestutils.set_custom_field(ms, customfield="field")
            self.assertEqual(type(ms.field), dict)
            self.assertEqual(ms.field["id"], "user123")
            mamburestutils.set_custom_field(ms, customfield="fieldid")
            self.assertEqual(type(ms.fieldid), dict)
            self.assertEqual(ms.fieldid["id"], "user123")

            # client_link custom field
            json.loads.return_value = {
                "customFields": [
                    {
                        "customField": {
                            "state": "",
                            "name": "field",
                            "id": "fieldid",
                            "dataType": "CLIENT_LINK",
                        },
                        "customFieldSetGroupIndex": -1,
                        "value": "client123",
                    },
                ]
            }
            ms = mambustruct.MambuStruct(
                urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
                custom_field_name="customFields",
            )
            mamburestutils.set_custom_field(ms, customfield="field")
            self.assertEqual(type(ms.field), dict)
            self.assertEqual(ms.field["id"], "client123")
            mamburestutils.set_custom_field(ms, customfield="fieldid")
            self.assertEqual(type(ms.fieldid), dict)
            self.assertEqual(ms.fieldid["id"], "client123")

            # grouped custom field
            json.loads.return_value = {
                "customFields": [
                    {
                        "customField": {
                            "state": "",
                            "name": "field",
                            "id": "fieldid",
                            "dataType": "STRING",
                        },
                        "customFieldSetGroupIndex": 0,
                        "value": "val",
                    },
                ]
            }
            ms = mambustruct.MambuStruct(
                urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
                custom_field_name="customFields",
            )
            mamburestutils.set_custom_field(ms, customfield="field_0")
            self.assertEqual(ms.field_0, "val")
            mamburestutils.set_custom_field(ms, customfield="fieldid_0")
            self.assertEqual(ms.fieldid_0, "val")


if __name__ == "__main__":
    unittest.main()
