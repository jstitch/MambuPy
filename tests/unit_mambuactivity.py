# coding: utf-8

import json
import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("."))

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

import unittest

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)
from MambuPy.rest import mambuactivity

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead

logging.disable(logging.CRITICAL)


class RequestsCounterTests(unittest.TestCase):
    """Tests for RequestsCounter singleton."""

    def setUp(self):
        # Reset the singleton for each test
        mambuactivity.RequestsCounter._RequestsCounter__instance = None

    def test_singleton(self):
        """Test that RequestsCounter is a singleton."""
        rc1 = mambuactivity.RequestsCounter()
        rc2 = mambuactivity.RequestsCounter()
        self.assertIs(rc1, rc2)

    def test_add(self):
        """Test add method increases counter."""
        rc = mambuactivity.RequestsCounter()
        self.assertEqual(rc.cnt, 0)
        rc.add(datetime.now())
        self.assertEqual(rc.cnt, 1)
        rc.add(datetime.now())
        self.assertEqual(rc.cnt, 2)
        self.assertEqual(len(rc.requests), 2)

    def test_reset(self):
        """Test reset method clears counter."""
        rc = mambuactivity.RequestsCounter()
        rc.add(datetime.now())
        rc.add(datetime.now())
        self.assertEqual(rc.cnt, 2)
        rc.reset()
        self.assertEqual(rc.cnt, 0)
        self.assertEqual(len(rc.requests), 0)


class MambuStructIteratorTests(unittest.TestCase):
    """Tests for MambuStructIterator."""

    def test_iteration(self):
        """Test basic iteration."""
        items = [1, 2, 3]
        it = mambuactivity.MambuStructIterator(items)
        result = list(it)
        self.assertEqual(result, items)

    def test_next_method(self):
        """Test next() method (Python 2 compatibility)."""
        items = ["a", "b"]
        it = mambuactivity.MambuStructIterator(items)
        self.assertEqual(it.next(), "a")
        self.assertEqual(it.next(), "b")
        with self.assertRaises(StopIteration):
            it.next()

    def test_iter_returns_self(self):
        """Test __iter__ returns self."""
        it = mambuactivity.MambuStructIterator([1])
        self.assertIs(iter(it), it)


class GetActivitiesUrlTests(unittest.TestCase):
    """Tests for _get_parameters_url and getactivitiesurl functions."""

    def test_get_parameters_url(self):
        """Test _get_parameters_url builds URL parameters."""
        params = mambuactivity._get_parameters_url({"key1": "val1", "key2": "val2"})
        self.assertIn("key1=val1", params)
        self.assertIn("key2=val2", params)

    def test_get_parameters_url_skips_none(self):
        """Test _get_parameters_url skips None values."""
        params = mambuactivity._get_parameters_url({"key1": "val1", "key2": None})
        self.assertEqual(len(params), 1)
        self.assertIn("key1=val1", params)

    @mock.patch("MambuPy.rest.mambuactivity.getmambuurl")
    def test_getactivitiesurl_no_kwargs(self, mock_getmambuurl):
        """Test getactivitiesurl without kwargs."""
        mock_getmambuurl.return_value = "https://test.mambu.com/api/"
        url = mambuactivity.getactivitiesurl()
        self.assertEqual(url, "https://test.mambu.com/api/activities")

    @mock.patch("MambuPy.rest.mambuactivity.getmambuurl")
    def test_getactivitiesurl_with_dates(self, mock_getmambuurl):
        """Test getactivitiesurl with fromDate and toDate."""
        mock_getmambuurl.return_value = "https://test.mambu.com/api/"
        url = mambuactivity.getactivitiesurl(
            fromDate="2024-01-01", toDate="2024-01-31"
        )
        self.assertIn("from=2024-01-01", url)
        self.assertIn("to=2024-01-31", url)

    @mock.patch("MambuPy.rest.mambuactivity.getmambuurl")
    def test_getactivitiesurl_defaults_from_date(self, mock_getmambuurl):
        """Test getactivitiesurl defaults from date to 1900-01-01."""
        mock_getmambuurl.return_value = "https://test.mambu.com/api/"
        url = mambuactivity.getactivitiesurl(toDate="2024-01-31")
        self.assertIn("from=1900-01-01", url)

    @mock.patch("MambuPy.rest.mambuactivity.getmambuurl")
    def test_getactivitiesurl_defaults_to_date(self, mock_getmambuurl):
        """Test getactivitiesurl defaults to date to today."""
        mock_getmambuurl.return_value = "https://test.mambu.com/api/"
        url = mambuactivity.getactivitiesurl(fromDate="2024-01-01")
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertIn("to=%s" % today, url)

    @mock.patch("MambuPy.rest.mambuactivity.getmambuurl")
    def test_getactivitiesurl_with_extra_params(self, mock_getmambuurl):
        """Test getactivitiesurl with additional filter parameters."""
        mock_getmambuurl.return_value = "https://test.mambu.com/api/"
        url = mambuactivity.getactivitiesurl(
            fromDate="2024-01-01", toDate="2024-01-31", clientId="ABC123"
        )
        self.assertIn("clientId=ABC123", url)


class MambuStructDictLikeTests(unittest.TestCase):
    """Tests for MambuStruct dict-like methods."""

    def test_getitem(self):
        """Test __getitem__."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        self.assertEqual(ms["key"], "value")

    def test_setitem(self):
        """Test __setitem__."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}
        ms["key"] = "value"
        self.assertEqual(ms.attrs["key"], "value")

    def test_delitem(self):
        """Test __delitem__."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        del ms["key"]
        self.assertNotIn("key", ms.attrs)

    def test_contains(self):
        """Test __contains__."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        self.assertIn("key", ms)
        self.assertNotIn("other", ms)

    def test_get(self):
        """Test get method."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        self.assertEqual(ms.get("key"), "value")
        self.assertEqual(ms.get("missing", "default"), "default")

    def test_get_raises_on_list(self):
        """Test get raises NotImplementedError for list attrs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = [1, 2, 3]
        with self.assertRaises(NotImplementedError):
            ms.get("key")

    def test_keys(self):
        """Test keys method."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"a": 1, "b": 2}
        self.assertEqual(set(ms.keys()), {"a", "b"})

    def test_keys_raises_on_missing_attrs(self):
        """Test keys raises NotImplementedError when attrs missing."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}  # Set it first
        object.__delattr__(ms, "attrs")
        with self.assertRaises(NotImplementedError):
            ms.keys()

    def test_items(self):
        """Test items method."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"a": 1, "b": 2}
        self.assertEqual(dict(ms.items()), {"a": 1, "b": 2})

    def test_items_raises_on_missing_attrs(self):
        """Test items raises NotImplementedError when attrs missing."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}  # Set it first
        object.__delattr__(ms, "attrs")
        with self.assertRaises(NotImplementedError):
            ms.items()

    def test_has_key_true(self):
        """Test has_key returns True for existing key."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        self.assertTrue(ms.has_key("key"))

    def test_has_key_false(self):
        """Test has_key returns False for missing key."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        self.assertFalse(ms.has_key("other"))

    def test_has_key_raises_on_list(self):
        """Test has_key raises NotImplementedError for list attrs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = [1, 2, 3]
        with self.assertRaises(NotImplementedError):
            ms.has_key("key")

    def test_has_key_raises_on_missing_attrs(self):
        """Test has_key raises NotImplementedError when attrs missing."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}  # Set it first
        object.__delattr__(ms, "attrs")
        with self.assertRaises(NotImplementedError):
            ms.has_key("key")

    def test_len(self):
        """Test __len__."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(len(ms), 3)


class MambuStructAttributeAccessTests(unittest.TestCase):
    """Tests for MambuStruct attribute access magic methods."""

    def test_getattribute_from_attrs(self):
        """Test __getattribute__ reads from attrs dict."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"custom_field": "custom_value"}
        self.assertEqual(ms.custom_field, "custom_value")

    def test_getattribute_list_attrs(self):
        """Test __getattribute__ with list attrs raises AttributeError."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = [1, 2, 3]
        with self.assertRaises(AttributeError):
            ms.nonexistent

    def test_setattr_to_attrs(self):
        """Test __setattr__ writes to attrs dict for new keys."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}
        ms.new_key = "new_value"
        self.assertEqual(ms.attrs["new_key"], "new_value")

    def test_setattr_list_attrs(self):
        """Test __setattr__ with list attrs sets object attribute."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = [1, 2, 3]
        ms.new_prop = "value"
        self.assertEqual(object.__getattribute__(ms, "new_prop"), "value")


class MambuStructReprStrTests(unittest.TestCase):
    """Tests for MambuStruct __repr__ and __str__ methods."""

    def test_repr_with_id(self):
        """Test __repr__ with id in attrs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"id": "12345"}
        self.assertEqual(repr(ms), "MambuStruct - id: 12345")

    def test_repr_no_id(self):
        """Test __repr__ without id (KeyError)."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"other": "value"}
        self.assertEqual(repr(ms), "MambuStruct (no standard entity)")

    def test_repr_no_attrs(self):
        """Test __repr__ without attrs (AttributeError)."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}  # Set it first
        ms.entid = "test_id"
        object.__delattr__(ms, "attrs")
        self.assertIn("not synced with Mambu", repr(ms))

    def test_repr_list_attrs(self):
        """Test __repr__ with list attrs (TypeError from id access)."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = [1, 2, 3]
        self.assertEqual(repr(ms), "MambuStruct - len: 3")

    def test_str_with_attrs(self):
        """Test __str__ with attrs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value"}
        self.assertIn("key", str(ms))

    def test_str_no_attrs(self):
        """Test __str__ without attrs falls back to repr."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {}  # Set it first
        ms.entid = "test"
        object.__delattr__(ms, "attrs")
        self.assertEqual(str(ms), repr(ms))


class MambuStructHashEqTests(unittest.TestCase):
    """Tests for MambuStruct __hash__ and __eq__ methods."""

    def test_hash_with_id(self):
        """Test __hash__ with id."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"id": "12345"}
        self.assertEqual(hash(ms), hash("12345"))

    def test_hash_without_id(self):
        """Test __hash__ without id uses repr."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"other": "value"}
        self.assertEqual(hash(ms), hash(repr(ms)))

    def test_eq_same_encodedkey(self):
        """Test __eq__ with same encodedKey."""
        ms1 = mambuactivity.MambuStruct(urlfunc=None)
        ms1.attrs = {"encodedKey": "ABC123"}
        ms2 = mambuactivity.MambuStruct(urlfunc=None)
        ms2.attrs = {"encodedKey": "ABC123"}
        self.assertEqual(ms1, ms2)

    def test_eq_different_encodedkey(self):
        """Test __eq__ with different encodedKey."""
        ms1 = mambuactivity.MambuStruct(urlfunc=None)
        ms1.attrs = {"encodedKey": "ABC123"}
        ms2 = mambuactivity.MambuStruct(urlfunc=None)
        ms2.attrs = {"encodedKey": "XYZ789"}
        self.assertNotEqual(ms1, ms2)

    def test_eq_missing_encodedkey(self):
        """Test __eq__ returns NotImplemented when encodedKey missing."""
        ms1 = mambuactivity.MambuStruct(urlfunc=None)
        ms1.attrs = {"other": "value"}
        ms2 = mambuactivity.MambuStruct(urlfunc=None)
        ms2.attrs = {"encodedKey": "ABC123"}
        self.assertEqual(ms1.__eq__(ms2), NotImplemented)

    def test_eq_no_attrs(self):
        """Test __eq__ returns NotImplemented when attrs missing."""
        ms1 = mambuactivity.MambuStruct(urlfunc=None)
        ms1.attrs = {}  # Set it first
        object.__delattr__(ms1, "attrs")
        ms2 = mambuactivity.MambuStruct(urlfunc=None)
        ms2.attrs = {"encodedKey": "ABC123"}
        self.assertEqual(ms1.__eq__(ms2), NotImplemented)

    def test_eq_not_mambustruct(self):
        """Test __eq__ with non-MambuStruct returns None (falsy)."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"encodedKey": "ABC123"}
        self.assertIsNone(ms.__eq__("string"))


class MambuStructSerializationTests(unittest.TestCase):
    """Tests for MambuStruct serialization methods."""

    def test_serialize_struct(self):
        """Test serialize_struct."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "value", "num": 123}
        result = ms.serialize_struct()
        self.assertEqual(result["key"], "value")
        self.assertEqual(result["num"], "123")

    def test_serialize_fields_mambustruct(self):
        """Test serialize_fields with MambuStruct."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"nested": "data"}
        result = mambuactivity.MambuStruct.serialize_fields(ms)
        self.assertEqual(result["nested"], "data")

    def test_serialize_fields_list(self):
        """Test serialize_fields with list."""
        result = mambuactivity.MambuStruct.serialize_fields([1, 2, 3])
        self.assertEqual(result, ["1", "2", "3"])

    def test_serialize_fields_dict(self):
        """Test serialize_fields with dict."""
        result = mambuactivity.MambuStruct.serialize_fields({"a": 1, "b": 2})
        self.assertEqual(result, {"a": "1", "b": "2"})

    def test_serialize_fields_non_iterable(self):
        """Test serialize_fields with non-iterable (TypeError path)."""
        result = mambuactivity.MambuStruct.serialize_fields(42)
        self.assertEqual(result, "42")


class MambuStructInitTests(unittest.TestCase):
    """Tests for MambuStruct __init__ with various kwargs."""

    def setUp(self):
        mambuactivity.RequestsCounter._RequestsCounter__instance = None

    def test_init_with_debug(self):
        """Test __init__ with debug kwarg."""
        ms = mambuactivity.MambuStruct(urlfunc=None, debug=True)
        self.assertTrue(ms._MambuStruct__debug)

    def test_init_with_date_format(self):
        """Test __init__ with date_format kwarg."""
        ms = mambuactivity.MambuStruct(urlfunc=None, date_format="%Y-%m-%d")
        self.assertEqual(ms._MambuStruct__formato_fecha, "%Y-%m-%d")

    def test_init_with_data_sets_post(self):
        """Test __init__ with data kwarg sets POST method."""
        ms = mambuactivity.MambuStruct(urlfunc=None, data={"key": "value"})
        self.assertEqual(ms._MambuStruct__method, "POST")

    def test_init_with_method(self):
        """Test __init__ with explicit method kwarg."""
        ms = mambuactivity.MambuStruct(urlfunc=None, method="DELETE")
        self.assertEqual(ms._MambuStruct__method, "DELETE")

    def test_init_with_limit(self):
        """Test __init__ with limit kwarg."""
        ms = mambuactivity.MambuStruct(urlfunc=None, limit=100)
        self.assertEqual(ms._MambuStruct__limit, 100)

    def test_init_with_offset(self):
        """Test __init__ with offset kwarg."""
        ms = mambuactivity.MambuStruct(urlfunc=None, offset=50)
        self.assertEqual(ms._MambuStruct__offset, 50)

    def test_init_with_custom_field_name(self):
        """Test __init__ with custom_field_name kwarg."""
        ms = mambuactivity.MambuStruct(urlfunc=None, custom_field_name="customFields")
        self.assertEqual(ms.custom_field_name, "customFields")

    def test_init_with_user_pwd(self):
        """Test __init__ with user and pwd kwargs."""
        ms = mambuactivity.MambuStruct(urlfunc=None, user="testuser", pwd="testpwd")
        self.assertEqual(ms._MambuStruct__user, "testuser")
        self.assertEqual(ms._MambuStruct__pwd, "testpwd")

    def test_init_connect_false(self):
        """Test __init__ with connect=False doesn't call connect."""
        with mock.patch.object(
            mambuactivity.MambuStruct, "connect"
        ) as mock_connect:
            ms = mambuactivity.MambuStruct(
                urlfunc=lambda x: "http://test", connect=False
            )
            mock_connect.assert_not_called()

    def test_init_connect_true_calls_connect(self):
        """Test __init__ with urlfunc and connect=True calls connect."""
        with mock.patch.object(
            mambuactivity.MambuStruct, "connect"
        ) as mock_connect:
            ms = mambuactivity.MambuStruct(
                urlfunc=lambda x: "http://test", connect=True
            )
            mock_connect.assert_called_once()


class MambuStructInitMethodTests(unittest.TestCase):
    """Tests for MambuStruct init() method (not __init__)."""

    def test_init_sets_attrs(self):
        """Test init sets attrs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.init(attrs={"key": "value"})
        self.assertEqual(ms.attrs["key"], "value")

    def test_init_sets_entid_from_id(self):
        """Test init sets entid from id in attrs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.init(attrs={"id": "12345"})
        self.assertEqual(ms.entid, "12345")

    def test_init_with_methods_kwarg(self):
        """Test init calls methods from kwargs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.test_method_called = False

        def test_method(self):
            self.test_method_called = True

        ms.test_method = lambda: test_method(ms)
        ms.init(attrs={}, methods=["test_method"])
        self.assertTrue(ms.test_method_called)

    def test_init_with_properties_kwarg(self):
        """Test init sets properties from kwargs."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.init(attrs={}, properties={"custom_prop": "custom_val"})
        self.assertEqual(ms.custom_prop, "custom_val")


class MambuStructConnectTests(unittest.TestCase):
    """Tests for MambuStruct connect and request methods."""

    def setUp(self):
        mambuactivity.RequestsCounter._RequestsCounter__instance = None

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    def test_connect_get_request(self, mock_iri, mock_session_class):
        """Test connect makes GET request."""
        mock_iri.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = json.dumps([{"activity": "test"}]).encode()
        mock_response.raise_for_status = mock.MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            connect=False,
        )
        ms.connect()

        mock_session.get.assert_called()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    @mock.patch("MambuPy.rest.mambuactivity.encoded_dict")
    def test_connect_post_request(self, mock_encoded, mock_iri, mock_session_class):
        """Test connect makes POST request when data provided."""
        mock_iri.side_effect = lambda x: x
        mock_encoded.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = json.dumps({"result": "ok"}).encode()
        mock_response.raise_for_status = mock.MagicMock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            data={"key": "value"},
            connect=False,
        )
        ms.connect()

        mock_session.post.assert_called()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    @mock.patch("MambuPy.rest.mambuactivity.encoded_dict")
    def test_connect_patch_request(self, mock_encoded, mock_iri, mock_session_class):
        """Test connect makes PATCH request."""
        mock_iri.side_effect = lambda x: x
        mock_encoded.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = json.dumps({"result": "ok"}).encode()
        mock_response.raise_for_status = mock.MagicMock()
        mock_session.patch.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            data={"key": "value"},
            method="PATCH",
            connect=False,
        )
        ms.connect()

        mock_session.patch.assert_called()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    def test_connect_delete_request(self, mock_iri, mock_session_class):
        """Test connect makes DELETE request."""
        mock_iri.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = json.dumps({"result": "ok"}).encode()
        mock_response.raise_for_status = mock.MagicMock()
        mock_session.delete.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            method="DELETE",
            connect=False,
        )
        ms.connect()

        mock_session.delete.assert_called()

    def test_connect_no_urlfunc(self):
        """Test connect returns early when urlfunc is None."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        # Should not raise
        ms._MambuStruct__urlfunc = None
        ms.connect()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    def test_connect_http_error_mambu_error(self, mock_iri, mock_session_class):
        """Test connect raises MambuError on HTTP error with Mambu response."""
        mock_iri.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = json.dumps(
            {"returnCode": 1, "returnStatus": "Error message"}
        ).encode()
        mock_response.raise_for_status.side_effect = (
            mambuactivity.requests.exceptions.HTTPError()
        )
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            connect=False,
        )
        with self.assertRaises(mambuactivity.MambuError):
            ms.connect()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    @mock.patch("MambuPy.rest.mambuactivity.strip_tags")
    def test_connect_http_error_invalid_json(self, mock_strip, mock_iri, mock_session_class):
        """Test connect raises MambuError on HTTP error with invalid JSON."""
        mock_iri.side_effect = lambda x: x
        mock_strip.return_value = "Error page"
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = b"<html>Error</html>"
        mock_response.raise_for_status.side_effect = (
            mambuactivity.requests.exceptions.HTTPError()
        )
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            connect=False,
        )
        with self.assertRaises(mambuactivity.MambuError):
            ms.connect()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    def test_connect_retry_error(self, mock_iri, mock_session_class):
        """Test connect raises MambuCommError on RetryError."""
        mock_iri.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_session.get.side_effect = mambuactivity.requests.exceptions.RetryError()
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            connect=False,
        )
        with self.assertRaises(mambuactivity.MambuCommError):
            ms.connect()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    def test_connect_generic_exception(self, mock_iri, mock_session_class):
        """Test connect re-raises generic exceptions."""
        mock_iri.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_session.get.side_effect = ValueError("Unexpected error")
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            connect=False,
        )
        with self.assertRaises(ValueError):
            ms.connect()

    @mock.patch("MambuPy.rest.mambuactivity.requests.Session")
    @mock.patch("MambuPy.rest.mambuactivity.iri_to_uri")
    def test_connect_with_limit_pagination(self, mock_iri, mock_session_class):
        """Test connect respects limit for pagination."""
        mock_iri.side_effect = lambda x: x
        mock_session = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.content = json.dumps([{"activity": "test"}]).encode()
        mock_response.raise_for_status = mock.MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        ms = mambuactivity.MambuStruct(
            urlfunc=lambda x, **kw: "http://test/activities",
            limit=10,
            connect=False,
        )
        ms.connect()

        mock_session.get.assert_called()


class MambuStructIsMambuErrorTests(unittest.TestCase):
    """Tests for MambuStruct _is_mambu_error method."""

    def test_is_mambu_error_true(self):
        """Test _is_mambu_error raises on error response."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        with self.assertRaises(mambuactivity.MambuError):
            ms._is_mambu_error({"returnCode": 1, "returnStatus": "Error"})

    def test_is_mambu_error_false(self):
        """Test _is_mambu_error returns False on success."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._is_mambu_error({"returnCode": 0, "returnStatus": "OK"})
        self.assertFalse(result)

    def test_is_mambu_error_no_return_code(self):
        """Test _is_mambu_error returns False when returnCode missing."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._is_mambu_error({"other": "data"})
        self.assertFalse(result)


class MambuStructProcessFieldsTests(unittest.TestCase):
    """Tests for MambuStruct _process_fields method."""

    def test_process_fields_strips_strings(self):
        """Test _process_fields strips whitespace from string values."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"key": "  value  ", "other": "  trimmed  "}
        ms._process_fields()
        self.assertEqual(ms.attrs["key"], "value")
        self.assertEqual(ms.attrs["other"], "trimmed")

    def test_process_fields_handles_non_strings(self):
        """Test _process_fields handles non-string values."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = {"num": 123, "str": "  text  "}
        ms._process_fields()
        self.assertEqual(ms.attrs["num"], 123)
        self.assertEqual(ms.attrs["str"], "text")

    def test_process_fields_handles_list_attrs(self):
        """Test _process_fields handles list attrs (NotImplementedError)."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        ms.attrs = [1, 2, 3]
        # Should not raise
        ms._process_fields()


class MambuStructTypeConversionTests(unittest.TestCase):
    """Tests for MambuStruct type conversion methods."""

    def test_convert_data_to_pytype_int(self):
        """Test _convert_data_to_pytype converts to int."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._convert_data_to_pytype("123")
        self.assertEqual(result, 123)
        self.assertIsInstance(result, int)

    def test_convert_data_to_pytype_int_with_leading_zeros(self):
        """Test _convert_data_to_pytype preserves strings with leading zeros."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._convert_data_to_pytype("00123")
        self.assertEqual(result, "00123")

    def test_convert_data_to_pytype_float(self):
        """Test _convert_data_to_pytype converts to float."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._convert_data_to_pytype("123.45")
        self.assertEqual(result, 123.45)
        self.assertIsInstance(result, float)

    def test_convert_data_to_pytype_datetime(self):
        """Test _convert_data_to_pytype converts to datetime."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._convert_data_to_pytype("2024-01-15T10:30:00+0000")
        self.assertIsInstance(result, datetime)

    def test_convert_data_to_pytype_string(self):
        """Test _convert_data_to_pytype returns string for non-convertible."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms._convert_data_to_pytype("plain text")
        self.assertEqual(result, "plain text")

    def test_convert_dict_to_pytypes_dict(self):
        """Test _convert_dict_to_pytypes converts dict values."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        data = {"num": "123", "text": "hello"}
        result = ms._convert_dict_to_pytypes(data)
        self.assertEqual(result["num"], 123)
        self.assertEqual(result["text"], "hello")

    def test_convert_dict_to_pytypes_list(self):
        """Test _convert_dict_to_pytypes converts list elements."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        data = ["123", "456"]
        result = ms._convert_dict_to_pytypes(data)
        self.assertEqual(result, [123, 456])

    def test_convert_dict_to_pytypes_constant_fields(self):
        """Test _convert_dict_to_pytypes preserves constant fields."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        data = {"id": "00123", "name": "Test Name", "num": "456"}
        result = ms._convert_dict_to_pytypes(data)
        self.assertEqual(result["id"], "00123")  # preserved as string
        self.assertEqual(result["name"], "Test Name")
        self.assertEqual(result["num"], 456)  # converted

    def test_util_date_format_custom_format(self):
        """Test util_date_format with custom format."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        result = ms.util_date_format("2024-01-15T10:30:00+0000", "%Y-%m-%d")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_util_date_format_default_format(self):
        """Test util_date_format with default format when __formato_fecha missing."""
        ms = mambuactivity.MambuStruct(urlfunc=None)
        object.__delattr__(ms, "_MambuStruct__formato_fecha")
        result = ms.util_date_format("2024-01-15T10:30:00+0000")
        self.assertIsInstance(result, datetime)


class MambuActivityTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        self.assertEqual(
            mambuactivity.mod_urlfunc, mambuactivity.getactivitiesurl
        )

    def test_class(self):
        a = mambuactivity.MambuActivity(urlfunc=None)
        self.assertTrue(mambuactivity.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambuactivity.MambuActivity(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")

    def test___repr__(self):
        def build_mock_act_1(self, *args, **kwargs):
            self.attrs = {"activity": args[1]}

        with mock.patch.object(mambuactivity.MambuStruct, "__init__", build_mock_act_1):
            a = mambuactivity.MambuActivity(
                urlfunc=mambuactivity.getactivitiesurl, entid="mockactivity"
            )
            self.assertRegexpMatches(
                repr(a), r"^MambuActivity - activityid: mockactivity"
            )

    def test___repr___no_activity_key(self):
        """Test __repr__ when activity key is missing."""
        def build_mock_act_no_key(self, *args, **kwargs):
            self.attrs = {"other": "value"}

        with mock.patch.object(mambuactivity.MambuStruct, "__init__", build_mock_act_no_key):
            a = mambuactivity.MambuActivity(urlfunc=None, entid="test")
            self.assertEqual(repr(a), "MambuActivity (no activity key)")


class MambuActivitiesTests(unittest.TestCase):
    def test_class(self):
        acs = mambuactivity.MambuActivities(urlfunc=None)
        self.assertTrue(mambuactivity.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambuactivity.MambuActivities(urlfunc=None)
        acs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(acs), 3)
        for n, a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        acs = mambuactivity.MambuActivities(urlfunc=None)
        acs.attrs = [
            {"activity": "my_act"},
            {"activity": "my_2_act"},
        ]
        with self.assertRaisesRegex(
            AttributeError,
            "'MambuActivities' object has no attribute 'mambuactivityclass'",
        ):
            acs.mambuactivityclass
        acs.convert_dict_to_attrs()
        self.assertEqual(
            str(acs.mambuactivityclass),
            "<class 'MambuPy.rest.mambuactivity.MambuActivity'>",
        )
        for a in acs:
            self.assertEqual(a.__class__.__name__, "MambuActivity")
            self.assertEqual(a._MambuStruct__urlfunc, mambuactivity.getactivitiesurl)


if __name__ == "__main__":
    unittest.main()
