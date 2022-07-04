# coding: utf-8

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambustruct

try:
    unittest.TestCase.assertRaisesRegexp = unittest.TestCase.assertRaisesRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRaisesRegex instead


class Response(object):
    def __init__(self, text):
        self.text = json.dumps(text)
        self.content = text


class MambuStructMethodsTests(unittest.TestCase):
    """MambuStruct Methods Tests"""

    def setUp(self):
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_init(self, requests, json, iri_to_uri):
        """Test init method, which is called by the connect method"""
        orig_preprocess = mambustruct.MambuStruct.preprocess
        orig_convertDict2Attrs = mambustruct.MambuStruct.convertDict2Attrs
        orig_postprocess = mambustruct.MambuStruct.postprocess
        orig_util_date_format = mambustruct.MambuStruct.util_date_format
        orig_serialize_struct = mambustruct.MambuStruct.serialize_struct

        mambustruct.MambuStruct.preprocess = mock.Mock()
        mambustruct.MambuStruct.convertDict2Attrs = mock.Mock()
        mambustruct.MambuStruct.postprocess = mock.Mock()
        mambustruct.MambuStruct.util_date_format = mock.Mock()
        mambustruct.MambuStruct.serialize_struct = mock.Mock()

        # init calls preprocess, convertDict2Attrs, postprocess methods, on that order
        json.loads.return_value = {"hello": "goodbye"}
        mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: ""
        )
        mambustruct.MambuStruct.preprocess.assert_called_with()
        mambustruct.MambuStruct.convertDict2Attrs.assert_called_with()
        mambustruct.MambuStruct.postprocess.assert_called_with()

        # 'methods' kwarg makes init call the methods on it
        json.loads.return_value = {"hello": "goodbye"}
        mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            methods=["util_date_format", "serialize_struct"],
        )
        mambustruct.MambuStruct.util_date_format.assert_called_with()
        mambustruct.MambuStruct.serialize_struct.assert_called_with()
        # non-existent method is just not called, no exception raised
        mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            methods=["blah_method"],
        )
        mambustruct.MambuStruct.preprocess.assert_called_with()
        mambustruct.MambuStruct.convertDict2Attrs.assert_called_with(
            methods=["blah_method"]
        )
        mambustruct.MambuStruct.postprocess.assert_called_with()

        # 'properties' kwarg makes init set additional attrs properties
        ms = mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            properties={"prop1": "val1", "prop2": "val2"},
        )
        self.assertEqual(ms.prop1, "val1")
        self.assertEqual(ms.prop2, "val2")

        mambustruct.MambuStruct.preprocess = orig_preprocess
        mambustruct.MambuStruct.convertDict2Attrs = orig_convertDict2Attrs
        mambustruct.MambuStruct.postprocess = orig_postprocess
        mambustruct.MambuStruct.util_date_format = orig_util_date_format
        mambustruct.MambuStruct.serialize_struct = orig_serialize_struct

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_convertDict2Attrs(self, requests, json, iri_to_uri):
        """Test conversion of dictionary elements (strings) in to proper datatypes"""
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: ""
        )

        # string remains string
        ms.attrs = {"prop1": "string"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop1, "string")

        # integer transforms in to int
        ms.attrs = {"prop2": "1"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop2, 1)

        # integer with trailing 0's remains as string
        ms.attrs = {"prop2b": "0001"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop2b, "0001")

        # floating point transforms in to float
        ms.attrs = {"prop3": "3.141592"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop3, 3.141592)

        # datetime transforms in to datetime object
        from datetime import datetime

        ms.attrs = {"prop4": "2017-10-23T00:00:00+0000"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop4, datetime.strptime("2017-10-23", "%Y-%m-%d"))

        # lists recursively convert each of its elements
        ms.attrs = {"prop5": ["foo", "1", "001", "2.78", "2017-10-23T00:00:00+0000"]}
        ms.convertDict2Attrs()
        self.assertEqual(
            ms.prop5,
            ["foo", 1, "001", 2.78, datetime.strptime("2017-10-23", "%Y-%m-%d")],
        )

        ms.attrs = {
            "prop5": ["foo", "1", "001", "2.78", "2017-10-23T00:00:00+0000", ["bar"]]
        }
        ms.convertDict2Attrs()
        self.assertEqual(
            ms.prop5,
            [
                "foo",
                1,
                "001",
                2.78,
                datetime.strptime("2017-10-23", "%Y-%m-%d"),
                ["bar"],
            ],
        )

        ms.attrs = {
            "prop5": [
                "foo",
                "1",
                "001",
                "2.78",
                "2017-10-23T00:00:00+0000",
                {"foo": "bar"},
            ]
        }
        ms.convertDict2Attrs()
        self.assertEqual(
            ms.prop5,
            [
                "foo",
                1,
                "001",
                2.78,
                datetime.strptime("2017-10-23", "%Y-%m-%d"),
                {"foo": "bar"},
            ],
        )

        # dictonaries recursively convert each of its elements
        ms.attrs = {
            "prop6": {
                "a": "1",
                "b": "001",
                "c": "2.78",
                "d": "2017-10-23T00:00:00+0000",
                "e": "foo",
            }
        }
        ms.convertDict2Attrs()
        self.assertEqual(
            ms.prop6,
            {
                "a": 1,
                "b": "001",
                "c": 2.78,
                "d": datetime.strptime("2017-10-23", "%Y-%m-%d"),
                "e": "foo",
            },
        )

        ms.attrs = {
            "prop6": {
                "a": "1",
                "b": "001",
                "c": "2.78",
                "d": "2017-10-23T00:00:00+0000",
                "e": "foo",
                "f": {"g": "h"},
            }
        }
        ms.convertDict2Attrs()
        self.assertEqual(
            ms.prop6,
            {
                "a": 1,
                "b": "001",
                "c": 2.78,
                "d": datetime.strptime("2017-10-23", "%Y-%m-%d"),
                "e": "foo",
                "f": {"g": "h"},
            },
        )

        ms.attrs = {
            "prop6": {
                "a": "1",
                "b": "001",
                "c": "2.78",
                "d": "2017-10-23T00:00:00+0000",
                "e": "foo",
                "f": ["bar"],
            }
        }
        ms.convertDict2Attrs()
        self.assertEqual(
            ms.prop6,
            {
                "a": 1,
                "b": "001",
                "c": 2.78,
                "d": datetime.strptime("2017-10-23", "%Y-%m-%d"),
                "e": "foo",
                "f": ["bar"],
            },
        )

        # certain fields remain as-is with no conversion to anything
        ms.attrs = {"id": "12345"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.id, "12345")

        ms.attrs = {"groupName": "12.34"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.groupName, "12.34")

        ms.attrs = {"name": "1979-10-23T10:23:00+0000"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.name, "1979-10-23T10:23:00+0000")

        ms.attrs = {"homePhone": "12345"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.homePhone, "12345")

        ms.attrs = {"mobilePhone1": "12.345"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.mobilePhone1, "12.345")

        ms.attrs = {"phoneNumber": "1979-10-23T10:23:00+0000"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.phoneNumber, "1979-10-23T10:23:00+0000")

        ms.attrs = {"postcode": "12345"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.postcode, "12345")

        ms.attrs = {"description": "12345"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.description, "12345")

        ms.attrs = {"emailAddress": "12345"}
        ms.convertDict2Attrs()
        self.assertEqual(ms.emailAddress, "12345")

    def test_RequestsCounter(self):
        """Tests that MambuStruct instance has a RequestsCounter singleton"""
        self.assertEqual(getattr(self.ms, "rc"), mambustruct.RequestsCounter())
        ms = mambustruct.MambuStruct(urlfunc=None)
        self.assertEqual(getattr(self.ms, "rc"), getattr(ms, "rc"))

    def test_urlfunc(self):
        """Tests setting an urlfunc"""
        self.assertEqual(getattr(self.ms, "_MambuStruct__urlfunc"), None)
        fun = lambda x: x
        ms = mambustruct.MambuStruct(urlfunc=fun, entid="", connect=False)
        ms.attrs = {}
        self.assertEqual(getattr(ms, "_MambuStruct__urlfunc"), fun)

    def test_custom_field_name(self):
        """Tests setting custom field name"""
        self.assertEqual(hasattr(self.ms, "custom_field_name"), False)
        ms = mambustruct.MambuStruct(urlfunc=None, custom_field_name="test")
        self.assertEqual(hasattr(ms, "custom_field_name"), True)
        self.assertEqual(getattr(ms, "custom_field_name"), "test")

    def test_private_props(self):
        """Tests private properties"""
        self.assertEqual(getattr(self.ms, "_MambuStruct__debug"), False)
        ms = mambustruct.MambuStruct(urlfunc=None, debug=True)
        self.assertEqual(getattr(ms, "_MambuStruct__debug"), True)

        self.assertEqual(
            getattr(self.ms, "_MambuStruct__formato_fecha"), "%Y-%m-%dT%H:%M:%S+0000"
        )
        ms = mambustruct.MambuStruct(urlfunc=None, date_format="%Y%m%d")
        self.assertEqual(getattr(ms, "_MambuStruct__formato_fecha"), "%Y%m%d")

        self.assertEqual(getattr(self.ms, "_MambuStruct__data"), None)
        data = {"postdata": "value"}
        ms = mambustruct.MambuStruct(urlfunc=None, data=data)
        self.assertEqual(getattr(ms, "_MambuStruct__data"), data)

        self.assertEqual(getattr(self.ms, "_MambuStruct__method"), "GET")
        ms = mambustruct.MambuStruct(urlfunc=None, method="PATCH")
        self.assertEqual(getattr(ms, "_MambuStruct__method"), "PATCH")
        ms = mambustruct.MambuStruct(urlfunc=None, method="DELETE")
        self.assertEqual(getattr(ms, "_MambuStruct__method"), "DELETE")

        self.assertEqual(getattr(self.ms, "_MambuStruct__limit"), 0)
        ms = mambustruct.MambuStruct(urlfunc=None, limit=123)
        self.assertEqual(getattr(ms, "_MambuStruct__limit"), 123)
        self.assertEqual(getattr(ms, "_MambuStruct__inilimit"), 123)

        self.assertEqual(getattr(self.ms, "_MambuStruct__offset"), 0)
        ms = mambustruct.MambuStruct(urlfunc=None, offset=321)
        self.assertEqual(getattr(ms, "_MambuStruct__offset"), 321)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test__process_fields(self, requests, json, iri_to_uri):
        """Test default fields (pre/post)processing"""
        # preprocess strips spaces from beginning/end of values
        json.loads.return_value = {"hello": "   goodbye   "}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms._process_fields()
        self.assertEqual(ms.hello, "goodbye")

        # custom fields are set as properties directly under attrs,
        # instead of buried down on the customFields property
        json.loads.return_value = {
            "customFields": [
                {
                    "customField": {
                        "state": "",
                        "name": "field",
                        "id": "fieldid",
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
        self.assertEqual(ms.field, "val")
        self.assertEqual(ms.fieldid, "val")

        # setGroupindex allows custom fields to be part of a list of
        # indexed custom fields. This sets are then named with an
        # index as a way to allow counting them.
        json.loads.return_value = {
            "customFields": [
                {
                    "customField": {
                        "state": "",
                        "name": "field",
                        "id": "fieldid",
                    },
                    "customFieldSetGroupIndex": 0,
                    "value": "val0",
                },
                {
                    "customField": {
                        "state": "",
                        "name": "field",
                        "id": "fieldid",
                    },
                    "customFieldSetGroupIndex": 1,
                    "value": "val1",
                },
            ]
        }
        ms = mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            custom_field_name="customFields",
        )
        self.assertEqual(ms.field_0, "val0")
        self.assertEqual(ms.field_1, "val1")
        self.assertEqual(ms.fieldid_0, "val0")
        self.assertEqual(ms.fieldid_1, "val1")

        # linkedEntityKeyValue creates a 'value' key with the value of
        # the entity key, an entity key is a pointer to some enttity
        # on Mambu, it's value is its encodingKey
        json.loads.return_value = {
            "customFields": [
                {
                    "customField": {
                        "state": "",
                        "name": "field",
                        "id": "fieldid",
                    },
                    "customFieldSetGroupIndex": -1,
                    "linkedEntityKeyValue": "abc123",
                },
            ]
        }
        ms = mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            custom_field_name="customFields",
        )
        self.assertEqual(ms.field, "abc123")
        self.assertEqual(ms.fieldid, "abc123")
        self.assertEqual(ms.customFields[0]["value"], "abc123")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_util_date_format(self, requests, json, iri_to_uri):
        """Test date_format"""
        from datetime import datetime

        today = datetime.now()
        # default date_format
        self.assertEqual(
            self.ms.util_date_format(
                field=today.strftime("%Y-%m-%dT%H:%M:%S+0000")
            ).strftime("%Y%m%d%H%M%S"),
            today.strftime("%Y%m%d%H%M%S"),
        )
        # given format
        self.assertEqual(
            self.ms.util_date_format(
                field=today.strftime("%Y-%m-%dT%H:%M:%S+0000"), formato="%Y%m%d"
            ).strftime("%Y%m%d"),
            today.strftime("%Y%m%d"),
        )
        # format given on instantiation
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            date_format="%Y%m%d",
        )
        self.assertEqual(
            ms.util_date_format(
                field=today.strftime("%Y-%m-%dT%H:%M:%S+0000"), formato="%Y%m%d"
            ).strftime("%Y%m%d"),
            today.strftime("%Y%m%d"),
        )

        del self.ms._MambuStruct__formato_fecha
        self.assertEqual(
            self.ms.util_date_format(
                field=today.strftime("%Y-%m-%dT%H:%M:%S+0000")
            ).strftime("%Y%m%d%H%M%S"),
            today.strftime("%Y%m%d%H%M%S"),
        )

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_preprocess_postprocess(self, requests, json, iri_to_uri):
        """Test default preprocess and postprocess"""
        orig__process_fields = mambustruct.MambuStruct._process_fields
        mambustruct.MambuStruct._process_fields = mock.Mock()

        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms._process_fields.assert_called_with()
        self.assertEqual(ms._process_fields.call_count, 2)

        mambustruct.MambuStruct._process_fields = orig__process_fields

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_serialize_struct(self, requests, json, iri_to_uri):
        """Test serialize_struct method"""
        json.loads.return_value = {"att1": "1"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = ms.serialize_struct()
        self.assertEqual(serial, {"att1": "1"})

        orig_serialize_fields = mambustruct.MambuStruct.serialize_fields
        mambustruct.MambuStruct.serialize_fields = mock.Mock()

        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms.serialize_struct()
        ms.serialize_fields.assert_called_with(ms.attrs)
        ms.serialize_fields.assert_called_with({"att1": 1})

        mambustruct.MambuStruct.serialize_fields = orig_serialize_fields

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test__serialize_fields(self, requests, json, iri_to_uri):
        """Test serialize_fields method"""
        # every 'normal' data type is converted to its string version
        json.loads.return_value = {
            "att1": 1,
            "att2": 1.23,
            "att3": "001",
            "att4": "string",
        }
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(serial["att1"], "1")
        self.assertEqual(serial["att2"], "1.23")
        self.assertEqual(serial["att3"], "001")
        self.assertEqual(serial["att4"], "string")

        # on lists, each of its elements is recursively converted
        json.loads.return_value = {"att": [1, 1.23, "001", "string"]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(serial["att"], ["1", "1.23", "001", "string"])

        json.loads.return_value = {"att": [1, 1.23, "001", "string", ["foo", "bar"]]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(serial["att"], ["1", "1.23", "001", "string", ["foo", "bar"]])

        json.loads.return_value = {"att": [1, 1.23, "001", "string", {"foo": "bar"}]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(serial["att"], ["1", "1.23", "001", "string", {"foo": "bar"}])

        # on dictionaries, each of its elements is recursively converted
        json.loads.return_value = {"att": {"a": 1, "b": 1.23, "c": "001", "d": "string"}}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(
            serial["att"], {"a": "1", "b": "1.23", "c": "001", "d": "string"}
        )

        json.loads.return_value = {
            "att": {"a": 1, "b": 1.23, "c": "001", "d": "string", "e": {"foo": "bar"}}
        }
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(
            serial["att"],
            {"a": "1", "b": "1.23", "c": "001", "d": "string", "e": {"foo": "bar"}},
        )

        json.loads.return_value = {
            "att": {"a": 1, "b": 1.23, "c": "001", "d": "string", "e": ["foo", "bar"]}
        }
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms.attrs)
        self.assertEqual(
            serial["att"],
            {"a": "1", "b": "1.23", "c": "001", "d": "string", "e": ["foo", "bar"]},
        )

        # recursively serialize MambuStruct objects
        json.loads.return_value = {"att1": 1, "att2": 1.23}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        json.loads.return_value = {"att1": ms, "att2": "001"}
        ms2 = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        serial = mambustruct.MambuStruct.serialize_fields(ms2.attrs)
        self.assertEqual(serial["att1"], {"att1": "1", "att2": "1.23"})
        self.assertEqual(serial["att2"], "001")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_create(self, requests, json, iri_to_uri):
        """Test create"""
        # inside __init__ if urlfunc is None connect is False
        ms = mambustruct.MambuStruct(
            connect=False, urlfunc=lambda entid, limit, offset: ""
        )
        data = {"user": {"user": "moreData"}, "customInformation": ["customFields"]}
        iri_to_uri.return_value = "http://example.com"
        requests.post.return_value = mock.Mock()
        responsePOST = {
            "user": {"user": "moreData"},
            "customInformation": [{"customId": "id", "customValue": "value"}],
        }
        json.loads.return_value = responsePOST

        self.assertEqual(ms.create(data), 1)
        self.assertEqual(ms.attrs, responsePOST)
        self.assertEqual(ms.keys(), responsePOST.keys())
        self.assertEqual(ms._MambuStruct__args, ())
        self.assertEqual(ms._MambuStruct__kwargs, {})

        # if the class who call method create is direfent who implemented it
        ms.create.__func__.__module__ = "mambupy.mambuNOTSTRUCT"
        with self.assertRaisesRegexp(Exception, r"^Child method not implemented$"):
            ms.create(data)

        self.assertEqual(ms._MambuStruct__method, "GET")
        self.assertEqual(ms._MambuStruct__data, None)
        self.assertTrue(ms._MambuStruct__urlfunc)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_update(self, requests, json, iri_to_uri):
        """Test update"""
        # inside __init__ if urlfunc is None connect is False
        ms = mambustruct.MambuStruct(
            connect=False, urlfunc=lambda entid, limit, offset: ""
        )
        data = {"user": {"user": "moreData"}, "customInformation": ["customFields"]}
        iri_to_uri.return_value = "http://example.com"
        requests.patch.return_value = Response(str(data))

        self.assertEqual(ms.update(data), 1)
        self.assertEqual(ms._MambuStruct__args, ())
        self.assertEqual(ms._MambuStruct__kwargs, {})

        # if the class who call method update is direfent who implemented it
        ms.update.__func__.__module__ = "mambupy.mambuNOTSTRUCT"
        with self.assertRaises(NotImplementedError):
            ms.update(data)

        # ensures that connect() was called to refresh the info in the entity
        iri_to_uri.assert_called_with("")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_update_patch(self, requests, json, iri_to_uri):
        """Test update"""
        # inside __init__ if urlfunc is None connect is False
        ms = mambustruct.MambuStruct(
            connect=False, urlfunc=lambda entid, limit, offset: ""
        )
        data = {"user": {"user": "moreData"}, "customInformation": ["customFields"]}
        iri_to_uri.return_value = "http://example.com"
        requests.patch.return_value = Response(str(data))

        self.assertEqual(ms.update_patch(data), 1)
        self.assertEqual(ms._MambuStruct__args, ())
        self.assertEqual(ms._MambuStruct__kwargs, {})

        # if not send any data raises an Exception
        with self.assertRaisesRegexp(Exception, r"^Requires data to update$"):
            ms.update_patch({})
        # if the class who call method update is direfent who implemented it
        ms.update_patch.__func__.__module__ = "mambupy.mambuNOTSTRUCT"
        with self.assertRaises(NotImplementedError):
            ms.update_patch(data)

        self.assertEqual(ms._MambuStruct__method, "GET")
        self.assertEqual(ms._MambuStruct__data, None)
        self.assertTrue(ms._MambuStruct__urlfunc)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_update_post(self, requests, json, iri_to_uri):
        """Test update"""
        # inside __init__ if urlfunc is None connect is False
        ms = mambustruct.MambuStruct(
            connect=False, urlfunc=lambda entid, limit, offset: ""
        )
        data = {"user": {"user": "moreData"}, "customInformation": ["customFields"]}
        iri_to_uri.return_value = "http://example.com"
        requests.post.return_value = Response(str(data))

        self.assertEqual(ms.update_post(data), 1)
        self.assertEqual(ms._MambuStruct__args, ())
        self.assertEqual(ms._MambuStruct__kwargs, {})

        # if not send any data raises an Exception
        with self.assertRaisesRegexp(Exception, r"^Requires data to update$"):
            ms.update_post({})
        # if the class who call method update is direfent who implemented it
        ms.update_post.__func__.__module__ = "mambupy.mambuNOTSTRUCT"
        with self.assertRaisesRegexp(Exception, r"^Child method not implemented$"):
            ms.update_post(data)

        self.assertEqual(ms._MambuStruct__method, "GET")
        self.assertEqual(ms._MambuStruct__data, None)
        self.assertTrue(ms._MambuStruct__urlfunc)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_upload_document(self, requests, json, iri_to_uri):
        """Test update"""
        # inside __init__ if urlfunc is None connect is False
        ms = mambustruct.MambuStruct(
            connect=False, urlfunc=lambda entid, limit, offset: ""
        )
        data = {
            "document": {
                "documentHolderKey": "XencodedKey",
                "documentHolderType": "LOAN_ACCOUNT",  # CLIENT, GROUP, USER, BRANCH...
                "name": "loan_resume",
                "type": "pdf",
            },
            "documentContent": "['encodedBase64_file']",
        }
        iri_to_uri.return_value = "http://example.com/api/documents"
        requests.post.return_value = Response(str(data))

        self.assertEqual(ms.upload_document(data), 1)
        self.assertEqual(ms._MambuStruct__args, ())
        self.assertEqual(ms._MambuStruct__kwargs, {})

        # if not send any data raises an Exception
        with self.assertRaisesRegexp(Exception, r"^Requires data to upload$"):
            ms.upload_document({})
        # if the class who call method update is direfent who implemented it
        ms.upload_document.__func__.__module__ = "mambupy.mambuNOTSTRUCT"
        with self.assertRaisesRegexp(Exception, r"^Child method not implemented$"):
            ms.upload_document(data)

        self.assertEqual(ms._MambuStruct__method, "GET")
        self.assertEqual(ms._MambuStruct__data, None)
        self.assertTrue(ms._MambuStruct__urlfunc)

if __name__ == "__main__":
    unittest.main()
