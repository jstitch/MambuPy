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


class RequestsCounterTests(unittest.TestCase):
    """Requests Counter singleton tests"""

    def setUp(self):
        self.rc = mambustruct.RequestsCounter()
        self.rc.cnt = 0

    def test_rc(self):
        """Test counter of singleton"""
        rc = mambustruct.RequestsCounter()
        rc.reset()

        self.assertEqual(rc.cnt, 0)
        rc.add("hola")
        self.assertEqual(rc.cnt, 1)
        self.assertEqual(rc.requests, ["hola"])

        rc.reset()
        self.assertEqual(rc.cnt, 0)
        self.assertEqual(rc.requests, [])


class MambuStructTests(unittest.TestCase):
    """MambuStruct Tests"""

    def setUp(self):
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    def test_class(self):
        """MambuStruct's class tests"""
        self.assertEqual(mambustruct.MambuStruct.RETRIES, 5)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___getattribute__(self, requests, json, iri_to_uri):
        """Get MambuStruct's attrs values as if they were properties of the object itself.

        Using dot notation"""
        # with no attrs: get object attributes, if not raise exception
        self.assertEqual(self.ms.RETRIES, 5)
        with self.assertRaises(AttributeError):
            self.ms.bla

        # with attrs, try get object attribute, if not, try to get attrs element, if not raise exception
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")

        self.assertEqual(ms.RETRIES, 5)
        self.assertEqual(ms.hello, "goodbye")
        self.assertEqual(ms.attrs["hello"], "goodbye")
        with self.assertRaises(AttributeError):
            ms.bla

        # with attrs not dict-like, get object attribute, if not raise exception
        json.loads.return_value = []
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.RETRIES, 5)
        with self.assertRaises(AttributeError):
            ms.bla

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___setattr__(self, requests, json, iri_to_uri):
        """Set MambuStruct's attrs keys as if they were properties of the object itself.

        Using dot notation"""
        # with no attrs
        self.ms.bla = "helloworld"
        self.assertEqual(self.ms.bla, "helloworld")

        # with attrs not dict-like, set attr
        json.loads.return_value = []
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms.bla = "helloworld"
        self.assertEqual(ms.bla, "helloworld")

        # if not prop of object, set it as new key on attrs dict
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms.bla = "helloworld"
        self.assertEqual(ms.bla, "helloworld")
        self.assertEqual(ms.attrs["bla"], "helloworld")

        # is not prop of object, and key already exists, update it
        ms.hello = "world"
        self.assertEqual(ms.hello, "world")
        self.assertEqual(ms.attrs["hello"], "world")

        # if prop is already a prop of the object, just set it
        ms.RETRIES = 6
        self.assertEqual(ms.RETRIES, 6)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___getitem__(self, requests, json, iri_to_uri):
        """Get an item from the attrs dict"""
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertTrue("hello" in ms.attrs)
        self.assertEqual(ms.attrs["hello"], "goodbye")
        self.assertEqual(ms["hello"], "goodbye")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___setitem__(self, requests, json, iri_to_uri):
        """Set an item in the attrs dict"""
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms["hello"] = "world"
        self.assertEqual(ms.attrs["hello"], "world")
        self.assertEqual(ms["hello"], "world")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___delitem__(self, requests, json, iri_to_uri):
        """Del an item from the attrs dict"""
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        ms["hello"] = "world"
        del ms["hello"]
        self.assertFalse("hello" in ms.attrs)

        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        del ms[1]
        self.assertEqual(len(ms.attrs), 2)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test__hash__(self, requests, json, iri_to_uri):
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.__hash__(), hash(repr(ms)))

        json.loads.return_value = {"id": "12345"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "abcd")
        self.assertEqual(ms.__hash__(), hash(ms.id))

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___str__(self, requests, json, iri_to_uri):
        """String representation of MambuStruct"""
        # when urlfunc is None, or not connected yet connected to Mambu
        self.assertEqual(str(self.ms), repr(self.ms))
        ms = mambustruct.MambuStruct(urlfunc=None, connect=False)
        self.assertEqual(str(ms), repr(ms))

        # when attrs exists
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(str(ms), "MambuStruct - {'hello': 'goodbye'}")
        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(str(ms), "MambuStruct - [1, 2, 3]")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___repr__(self, requests, json, iri_to_uri):
        """Repr of MambuStruct"""
        # when urlfunc is None, or not connected yet connected to Mambu
        self.assertEqual(repr(self.ms), "MambuStruct - id: '' (not synced with Mambu)")
        ms = mambustruct.MambuStruct(urlfunc=None, connect=False)
        self.assertEqual(repr(ms), "MambuStruct - id: '' (not synced with Mambu)")

        # when attrs is a dict
        json.loads.return_value = {"id": "12345"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(repr(ms), "MambuStruct - id: 12345")

        # when attrs is a dict with no id
        json.loads.return_value = {}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(repr(ms), "MambuStruct (no standard entity)")

        # when attrs is a list
        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(repr(ms), "MambuStruct - len: 3")

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___len__(self, requests, json, iri_to_uri):
        """Len of MambuStruct"""
        # on attrs=dict-like, len is number of keys
        json.loads.return_value = {"id": "12345", "hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(len(ms), 2)

        # on attrs=list-like, len is length of list
        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(len(ms), 3)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test___eq__(self, requests, json, iri_to_uri):
        """Equivalence between MambuStructs"""
        # if comparing to anything other than MambuStruct
        self.assertEqual(self.ms == object, None)

        # when any MambuStruct has no 'encodedkey' field, raises NotImplemented
        ms = mambustruct.MambuStruct(urlfunc=None)
        self.assertEqual(ms.__eq__(self.ms), NotImplemented)
        json.loads.return_value = {"encodedKey": "abc123"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.__eq__(self.ms), NotImplemented)
        self.assertEqual(self.ms.__eq__(ms), NotImplemented)

        # when both have an encodedkey, compare both
        json.loads.return_value = {"encodedKey": "abc123"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        json.loads.return_value = {"encodedKey": "def456"}
        ms2 = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertNotEqual(ms, ms2)
        self.assertNotEqual(ms2, ms)

        self.assertEqual(ms, ms)
        json.loads.return_value = {"encodedKey": "abc123"}
        ms2 = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms, ms2)
        self.assertEqual(ms2, ms)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_has_key(self, requests, json, iri_to_uri):
        """Dictionary-like has_key method"""
        # when no attrs or not dict-like, raises NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.ms.has_key("bla")

        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        with self.assertRaises(NotImplementedError):
            ms.has_key("bla")

        # when attrs dict-like, return what attrs.has_key returns
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.has_key("hello"), True)
        self.assertEqual(ms.has_key("bla"), False)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_contains(self, requests, json, iri_to_uri):
        """__contains__ method"""
        # when no attrs, raises AttributeError
        with self.assertRaises(AttributeError):
            "bla" in self.ms

        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertFalse(0 in ms)
        self.assertTrue(1 in ms)
        self.assertTrue(2 in ms)
        self.assertTrue(3 in ms)

        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertTrue("hello" in ms)
        self.assertFalse("bla" in ms)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_get(self, requests, json, iri_to_uri):
        """Dictionary-like get method"""
        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        with self.assertRaises(NotImplementedError):
            ms.get("bla")

        json.loads.return_value = {"hello": "world"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.get("hello"), "world")
        self.assertEqual(ms.get("bla"), None)
        self.assertEqual(ms.get("bla", False), False)

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_keys(self, requests, json, iri_to_uri):
        """Dictionary-like keys method"""
        # when no attrs or not dict-like, raises NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.ms.keys()

        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        with self.assertRaises(NotImplementedError):
            ms.keys()

        # when attrs dict-like, return what attrs.keys returns
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual([k for k in ms.keys()], ["hello"])

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_items(self, requests, json, iri_to_uri):
        """Dictionary-like items method"""
        # when no attrs or not dict-like, raises NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.ms.has_key("bla")

        json.loads.return_value = [1, 2, 3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        with self.assertRaises(NotImplementedError):
            ms.has_key("bla")

        # when attrs dict-like, return what attrs.items returns
        json.loads.return_value = {"hello": "goodbye"}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset: "")
        self.assertEqual([k for k in ms.items()], [("hello", "goodbye")])

    def test___init__(self):
        """Build MambuStruct object"""
        ms = mambustruct.MambuStruct(urlfunc=None, entid="12345")
        self.assertEqual(getattr(ms, "entid"), "12345")
        ms = mambustruct.MambuStruct(urlfunc={}, entid="12345", connect=True)
        self.assertEqual(getattr(ms, "entid"), "12345")
        # MambuStruct saves parameter calls
        ms = mambustruct.MambuStruct(
            urlfunc={}, entid="12345", fullDetails=True, connect=False
        )
        self.assertEqual(ms._MambuStruct__kwargs, {"fullDetails": True})


class MambuStructConnectTests(unittest.TestCase):
    """MambuStruct Connect Tests"""

    def setUp(self):
        self.tmp_bound_limit = mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    def tearDown(self):
        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = self.tmp_bound_limit

    @mock.patch("MambuPy.rest.mambustruct.iri_to_uri")
    @mock.patch("MambuPy.rest.mambustruct.json")
    @mock.patch("MambuPy.rest.mambustruct.requests")
    def test_connect(self, requests, json, iri_to_uri):
        # urlfunc=None -> returns immediately
        ms = mambustruct.MambuStruct(entid="", urlfunc=None)
        self.assertIsNone(ms.connect())
        self.assertFalse(iri_to_uri.called)
        self.assertFalse(requests.get().called)
        self.assertFalse(json.loads.called)

        # normal load
        requests.reset_mock()
        rc_cnt = ms.rc.cnt
        iri_to_uri.return_value = "http://example.com"
        requests.get.return_value = mock.Mock()
        requests.get.return_value.content = "my raw response"
        json.loads.return_value = {"field1": "value1", "field2": "value2"}
        ms = mambustruct.MambuStruct(
            entid="12345",
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            user="my_user",
            pwd="my_password",
        )
        requests.get.assert_called_with(
            "http://example.com",
            headers={"Accept": "application/vnd.mambu.v1+json"},
            auth=("my_user", "my_password"),
        )
        self.assertEqual(ms.rc.cnt, rc_cnt + 1)
        self.assertIsNone(ms.connect())
        self.assertEqual(ms.attrs, {"field1": "value1", "field2": "value2"})
        self.assertEqual(ms._raw_response_data, "my raw response")
        # connect saves old parameter calls
        self.assertEqual(
            ms._MambuStruct__kwargs, {"user": "my_user", "pwd": "my_password"}
        )
        ms.connect()
        requests.get.assert_called_with(
            "http://example.com",
            headers={"Accept": "application/vnd.mambu.v1+json"},
            auth=("my_user", "my_password"),
        )

        # POST data
        requests.reset_mock()
        data = {"data1": "value1"}
        iri_to_uri.return_value = "http://example.com"
        json.dumps.return_value = data
        requests.post.return_value = mock.Mock()
        json.loads.return_value = {"field1": "value1", "field2": "value2"}
        ms = mambustruct.MambuStruct(
            entid="12345",
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            data=data,
            user="my_user",
            pwd="my_password",
        )
        requests.post.assert_called_with(
            "http://example.com",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
            data={"data1": "value1"},
            auth=("my_user", "my_password"),
        )
        self.assertIsNone(ms.connect())
        self.assertEqual(ms.attrs, {"field1": "value1", "field2": "value2"})

        from MambuPy.mambuutil import apipwd, apiuser

        requests.reset_mock()
        mambustruct.MambuStruct(
            entid="12345",
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            data=data,
        )
        requests.post.assert_called_with(
            "http://example.com",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
            data={"data1": "value1"},
            auth=(apiuser, apipwd),
        )

        # PATCH data
        requests.reset_mock()
        data = {"data1": "value1"}
        iri_to_uri.return_value = "http://example.com"
        json.dumps.return_value = data
        requests.patch.return_value = mock.Mock()
        json.loads.return_value = {"field1": "value1", "field2": "value2"}
        ms = mambustruct.MambuStruct(
            entid="12345",
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            data=data,
            method="PATCH",
            user="my_user",
            pwd="my_password",
        )
        requests.patch.assert_called_with(
            "http://example.com",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
            data={"data1": "value1"},
            auth=("my_user", "my_password"),
        )
        self.assertIsNone(ms.connect())
        self.assertEqual(
            getattr(ms, "attrs", "Monty Python Flying Circus"),
            "Monty Python Flying Circus",
        )

        # DELETE data
        requests.reset_mock()
        iri_to_uri.return_value = "http://example.com"
        json.dumps.return_value = data
        requests.delete.return_value = Response(
            '{"returnCode":0,"returnStatus":"SUCCESS"}'
        )
        ms = mambustruct.MambuStruct(
            entid="12345",
            urlfunc=lambda entid, limit, offset, *args, **kwargs: "",
            method="DELETE",
            user="my_user",
            pwd="my_password",
        )
        requests.delete.assert_called_with(
            "http://example.com",
            headers={"Accept": "application/vnd.mambu.v1+json"},
            auth=("my_user", "my_password"),
        )
        self.assertIsNone(ms.connect())
        self.assertEqual(
            ms._raw_response_data, '{"returnCode":0,"returnStatus":"SUCCESS"}'
        )
        self.assertEqual(
            getattr(ms, "attrs", "Monty Python Flying Circus"),
            "Monty Python Flying Circus",
        )

        # normal load with error
        iri_to_uri.return_value = ""
        requests.get.return_value = mock.Mock()
        json.loads.return_value = {"returnCode": "500", "returnStatus": "TEST ERROR"}
        with self.assertRaisesRegexp(mambustruct.MambuError, r"^TEST ERROR$"):
            mambustruct.MambuStruct(
                entid="12345", urlfunc=lambda entid, limit, offset: ""
            )

        # load list
        iri_to_uri.return_value = ""
        requests.get.return_value = mock.Mock()
        json.loads.return_value = [
            {"field1": "value1", "field2": "value2"},
            {"field1": "value3", "field2": "value4"},
        ]
        ms = mambustruct.MambuStruct(
            entid="12345", urlfunc=lambda entid, limit, offset: ""
        )
        self.assertEqual(
            ms.attrs,
            [
                {"field1": "value1", "field2": "value2"},
                {"field1": "value3", "field2": "value4"},
            ],
        )

        # retries mechanism
        # one Comm Error, but retrying solves it
        iri_to_uri.return_value = ""
        requests.get.side_effect = [
            ValueError("TESTING RETRIES %s" % i) for i in range(1)
        ].extend([mock.Mock()])
        json.loads.return_value = {"field1": "value1", "field2": "value2"}
        ms = mambustruct.MambuStruct(
            entid="12345", urlfunc=lambda entid, limit, offset: ""
        )
        self.assertEqual(ms.attrs, {"field1": "value1", "field2": "value2"})

        # exceeds retry number
        import requests as reqs

        mambustruct.requests.exceptions = reqs.exceptions
        iri_to_uri.return_value = ""
        requests.get.side_effect = [
            reqs.exceptions.RequestException("TESTING RETRIES")
            for _ in range(mambustruct.MambuStruct.RETRIES)
        ]
        json.loads.return_value = {"field1": "value1", "field2": "value2"}
        with self.assertRaisesRegexp(
            mambustruct.MambuCommError, r"^ERROR I can't communicate with Mambu"
        ):
            mambustruct.MambuStruct(
                entid="12345", urlfunc=lambda entid, limit, offset: ""
            )

        # MambuError
        iri_to_uri.return_value = ""
        requests.get.side_effect = [mock.Mock()]
        json.loads.side_effect = [Exception("TEST ERROR")]
        with self.assertRaisesRegexp(
            mambustruct.MambuError, r"^JSON Error: Exception\('TEST ERROR'"
        ):
            mambustruct.MambuStruct(
                entid="12345", urlfunc=lambda entid, limit, offset: ""
            )

        # MambuError
        requests.get.side_effect = None
        iri_to_uri.return_value = ""
        requests.get().content = b"""<html>\n<head><title>Oh My</title></head>
<body>\n<h1>One error</h1>\n<p>Watcha gonna do?</p></body></html>"""
        json.loads.side_effect = [ValueError("TEST ERROR")]
        with self.assertRaisesRegexp(
            mambustruct.MambuError, r"^Oh My: One error. Watcha gonna do?"
        ):
            mambustruct.MambuStruct(
                entid="12345", urlfunc=lambda entid, limit, offset: ""
            )

        # Mambu 500 Error
        requests.get.side_effect = None
        iri_to_uri.return_value = ""
        requests.get().content = b"""<html>\n<head><title>502 gateway error</title></head>
<body>\n<h1>502 gateway error</h1>\n<p>Should retry!</p></body></html>"""
        json.loads.side_effect = ValueError("TEST ERROR")
        requests.get.reset_mock()
        with self.assertRaisesRegexp(
            mambustruct.MambuError, r"^ERROR I can't communicate with Mambu"
        ):
            with mock.patch("MambuPy.rest.mambustruct.time"):
                mambustruct.MambuStruct(
                    entid="12345", urlfunc=lambda entid, limit, offset: ""
                )
        self.assertEqual(requests.get.call_count, mambustruct.MambuStruct.RETRIES)

        # pagination mechanism
        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = (
            1  # simulate as if Mambu could only returns one element per request
        )
        iri_to_uri.return_value = ""
        requests.get.side_effect = [
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
        ]  # every time Mambu responds correctly
        json.loads.side_effect = [
            [{"field1": "value1"}],
            [{"field2": "value2"}],
            [{"field3": "value3"}],
            [{"field4": "value4"}],
            [],  # last time no elements means it's over
        ]
        # limit=0 means I want everything even though Mambu only returns 1 element per request
        # ie I want the result to have everything Mambu would send no matter its internal limit
        ms = mambustruct.MambuStruct(
            entid="12345", urlfunc=lambda entid, limit, offset: "", limit=0
        )
        self.assertEqual(len(ms.attrs), 4)

        # only get first 3 elements
        requests.get.side_effect = [
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
            mock.Mock(),
        ]  # every time Mambu responds correctly
        json.loads.side_effect = [
            [{"field1": "value1"}],
            [{"field2": "value2"}],
            [{"field3": "value3"}],
            [{"field4": "value4"}],
            [],  # last time no elements means it's over
        ]
        ms = mambustruct.MambuStruct(
            entid="12345", urlfunc=lambda entid, limit, offset: "", limit=3
        )
        self.assertEqual(len(ms.attrs), 3)


from MambuPy.rest import mambuclient, mambuuser


class MambuStructFunctionTests(unittest.TestCase):
    """MambuStruct module Functions Tests"""

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
            mambustruct.set_custom_field(ms, customfield="field")
            self.assertEqual(ms.field, "val")
            mambustruct.set_custom_field(ms, customfield="fieldid")
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
            mambustruct.set_custom_field(ms, customfield="field")
            self.assertEqual(type(ms.field), dict)
            self.assertEqual(ms.field["id"], "user123")
            mambustruct.set_custom_field(ms, customfield="fieldid")
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
            mambustruct.set_custom_field(ms, customfield="field")
            self.assertEqual(type(ms.field), dict)
            self.assertEqual(ms.field["id"], "client123")
            mambustruct.set_custom_field(ms, customfield="fieldid")
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
            mambustruct.set_custom_field(ms, customfield="field_0")
            self.assertEqual(ms.field_0, "val")
            mambustruct.set_custom_field(ms, customfield="fieldid_0")
            self.assertEqual(ms.fieldid_0, "val")


class MambuStructIteratorTests(unittest.TestCase):
    def setUp(self):
        class test_class:
            def __init__(self, wrap):
                self.iterator = mambustruct.MambuStructIterator(wrap)

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


if __name__ == "__main__":
    unittest.main()
