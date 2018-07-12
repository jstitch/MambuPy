# coding: utf-8

import mock
import unittest
from datetime import datetime

import mambustruct



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

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___getattribute__(self, requests, json, iriToUri):
        """Get MambuStruct's attrs values as if they were properties of the object itself.

        Using dot notation"""
        # with no attrs: get object attributes, if not raise exception
        self.assertEqual(self.ms.RETRIES, 5)
        with self.assertRaises(AttributeError) as e:
            self.ms.bla


        # with attrs, try get object attribute, if not, try to get attrs element, if not raise exception
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")

        self.assertEqual(ms.RETRIES, 5)
        self.assertEqual(ms.hello, 'goodbye')
        self.assertEqual(ms.attrs['hello'], 'goodbye')
        with self.assertRaises(AttributeError) as e:
            ms.bla


        # with attrs not dict-like, get object attribute, if not raise exception
        json.loads.return_value = []
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(ms.RETRIES, 5)
        with self.assertRaises(AttributeError) as e:
            ms.bla

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___setattr__(self, requests, json, iriToUri):
        """Set MambuStruct's attrs keys as if they were properties of the object itself.

        Using dot notation"""
        # with no attrs
        self.ms.bla = "helloworld"
        self.assertEqual(self.ms.bla, "helloworld")


        # with attrs not dict-like, set attr
        json.loads.return_value = []
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms.bla = "helloworld"
        self.assertEqual(ms.bla, "helloworld")


        # if not prop of object, set it as new key on attrs dict
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms.bla = "helloworld"
        self.assertEqual(ms.bla, "helloworld")
        self.assertEqual(ms.attrs['bla'], "helloworld")

        # is not prop of object, and key already exists, update it
        ms.hello = "world"
        self.assertEqual(ms.hello, "world")
        self.assertEqual(ms.attrs['hello'], "world")

        # if prop is already a prop of the object, just set it
        ms.RETRIES = 6
        self.assertEqual(ms.RETRIES, 6)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___getitem__(self, requests, json, iriToUri):
        """Get an item from the attrs dict"""
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertTrue(ms.attrs.has_key('hello'))
        self.assertEqual(ms.attrs['hello'], 'goodbye')
        self.assertEqual(ms['hello'], 'goodbye')

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___setitem__(self, requests, json, iriToUri):
        """Set an item in the attrs dict"""
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms['hello'] = 'world'
        self.assertEqual(ms.attrs['hello'], 'world')
        self.assertEqual(ms['hello'], 'world')

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___delitem__(self, requests, json, iriToUri):
        """Del an item from the attrs dict"""
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms['hello'] = 'world'
        del ms['hello']
        self.assertFalse(ms.attrs.has_key('hello'))

        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        del ms[1]
        self.assertEqual(len(ms.attrs), 2)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test__hash__(self, requests, json, iriToUri):
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(ms.__hash__(), hash(repr(ms)))

        json.loads.return_value = {'id':'12345'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "abcd")
        self.assertEqual(ms.__hash__(), hash(ms.id))

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___str__(self, requests, json, iriToUri):
        """String representation of MambuStruct"""
        # when urlfunc is None, or not connected yet connected to Mambu
        self.assertEqual(str(self.ms), repr(self.ms))
        ms = mambustruct.MambuStruct(urlfunc=None, connect=False)
        self.assertEqual(str(ms), repr(ms))

        # when attrs exists
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(str(ms), "MambuStruct - {'hello': 'goodbye'}")
        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(str(ms), "MambuStruct - [1, 2, 3]")

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___repr__(self, requests, json, iriToUri):
        """Repr of MambuStruct"""
        # when urlfunc is None, or not connected yet connected to Mambu
        self.assertEqual(repr(self.ms), "MambuStruct - id: '' (not synced with Mambu)")
        ms = mambustruct.MambuStruct(urlfunc=None, connect=False)
        self.assertEqual(repr(ms), "MambuStruct - id: '' (not synced with Mambu)")

        # when attrs is a dict
        json.loads.return_value = {'id':'12345'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(repr(ms), "MambuStruct - id: 12345")

        # when attrs is a dict with no id
        json.loads.return_value = {}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(repr(ms), "MambuStruct (no standard entity)")

        # when attrs is a list
        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(repr(ms), "MambuStruct - len: 3")

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___len__(self, requests, json, iriToUri):
        """Len of MambuStruct"""
        # on attrs=dict-like, len is number of keys
        json.loads.return_value = {'id':'12345', 'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(len(ms), 2)

        # on attrs=list-like, len is length of list
        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(len(ms), 3)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test___eq__(self, requests, json, iriToUri):
        """Equivalence between MambuStructs"""
        # if comparing to anything other than MambuStruct
        self.assertEqual(self.ms==object, None)

        # when any MambuStruct has no 'encodedkey' field, raises NotImplemented
        ms = mambustruct.MambuStruct(urlfunc=None)
        with self.assertRaises(NotImplementedError) as ex:
            ms == self.ms
        json.loads.return_value = {'encodedKey':'abc123'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        with self.assertRaises(NotImplementedError) as ex:
            ms == self.ms
        with self.assertRaises(NotImplementedError) as ex:
            self.ms == ms

        # when both have an encodedkey, compare both
        json.loads.return_value = {'encodedKey':'abc123'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        json.loads.return_value = {'encodedKey':'def456'}
        ms2 = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertNotEqual(ms, ms2)
        self.assertNotEqual(ms2, ms)

        self.assertEqual(ms, ms)
        json.loads.return_value = {'encodedKey':'abc123'}
        ms2 = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(ms, ms2)
        self.assertEqual(ms2, ms)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_has_key(self, requests, json, iriToUri):
        """Dictionary-like has_key method"""
        # when no attrs or not dict-like, raises NotImplementedError
        with self.assertRaises(NotImplementedError) as ex:
            self.ms.has_key('bla')

        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        with self.assertRaises(NotImplementedError) as ex:
            ms.has_key('bla')

        # when attrs dict-like, return what attrs.has_key returns
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(ms.has_key('hello'), True)
        self.assertEqual(ms.has_key('bla'), False)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_keys(self, requests, json, iriToUri):
        """Dictionary-like keys method"""
        # when no attrs or not dict-like, raises NotImplementedError
        with self.assertRaises(NotImplementedError) as ex:
            self.ms.keys()

        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        with self.assertRaises(NotImplementedError) as ex:
            ms.keys()

        # when attrs dict-like, return what attrs.keys returns
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(ms.keys(), ['hello'])

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_items(self, requests, json, iriToUri):
        """Dictionary-like items method"""
        # when no attrs or not dict-like, raises NotImplementedError
        with self.assertRaises(NotImplementedError) as ex:
            self.ms.has_key('bla')

        json.loads.return_value = [1,2,3]
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        with self.assertRaises(NotImplementedError) as ex:
            ms.has_key('bla')

        # when attrs dict-like, return what attrs.items returns
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        self.assertEqual(ms.items(), [('hello','goodbye')])

    def test___init__(self):
        """Build MambuStruct object"""
        ms = mambustruct.MambuStruct(urlfunc=None, entid='12345')
        self.assertEqual(getattr(ms, 'entid'), '12345')
        ms = mambustruct.MambuStruct(urlfunc={}, entid='12345', connect=True)
        self.assertEqual(getattr(ms, 'entid'), '12345')


class MambuStructMethodsTests(unittest.TestCase):
    """MambuStruct Methods Tests"""
    def setUp(self):
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_init(self, requests, json, iriToUri):
        """Test init method, which is called by the connect method"""
        orig_preprocess        = mambustruct.MambuStruct.preprocess
        orig_convertDict2Attrs = mambustruct.MambuStruct.convertDict2Attrs
        orig_postprocess       = mambustruct.MambuStruct.postprocess
        orig_util_dateFormat   = mambustruct.MambuStruct.util_dateFormat
        orig_serializeStruct   = mambustruct.MambuStruct.serializeStruct

        mambustruct.MambuStruct.preprocess        = mock.Mock()
        mambustruct.MambuStruct.convertDict2Attrs = mock.Mock()
        mambustruct.MambuStruct.postprocess       = mock.Mock()
        mambustruct.MambuStruct.util_dateFormat   = mock.Mock()
        mambustruct.MambuStruct.serializeStruct   = mock.Mock()

        # init calls preprocess, convertDict2Attrs, postprocess methods, on that order
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "")
        mambustruct.MambuStruct.preprocess.assert_called_with()
        mambustruct.MambuStruct.convertDict2Attrs.assert_called_with()
        mambustruct.MambuStruct.postprocess.assert_called_with()

        # 'methods' kwarg makes init call the methods on it
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "", methods=['util_dateFormat', 'serializeStruct'])
        mambustruct.MambuStruct.util_dateFormat.assert_called_with()
        mambustruct.MambuStruct.serializeStruct.assert_called_with()
        # non-existent method is just not called, no exception raised
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "", methods=['blah_method'])
        mambustruct.MambuStruct.preprocess.assert_called_with()
        mambustruct.MambuStruct.convertDict2Attrs.assert_called_with(methods=['blah_method'])
        mambustruct.MambuStruct.postprocess.assert_called_with()

        # 'properties' kwarg makes init set additional attrs properties
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "", properties={'prop1':'val1', 'prop2':'val2'})
        self.assertEqual(ms.prop1, 'val1')
        self.assertEqual(ms.prop2, 'val2')

        mambustruct.MambuStruct.preprocess       = orig_preprocess
        mambustruct.MambuStruct.convertDict2Arrs = orig_convertDict2Attrs
        mambustruct.MambuStruct.postprocess      = orig_postprocess
        mambustruct.MambuStruct.util_dateFormat  = orig_util_dateFormat
        mambustruct.MambuStruct.serializeStruct  = orig_serializeStruct

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_convertDict2Attrs(self, requests, json, iriToUri):
        """Test conversion of dictionary elements (strings) in to proper datatypes"""
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "")

        # string remains string
        ms.attrs = {'prop1' : 'string'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop1, 'string')

        # integer transforms in to int
        ms.attrs = {'prop2' : '1'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop2, 1)

        # integer with trailing 0's remains as string
        ms.attrs = {'prop2b' : '0001'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop2b, '0001')

        # floating point transforms in to float
        ms.attrs = {'prop3' : '3.141592'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop3, 3.141592)

        # datetime transforms in to datetime object
        from datetime import datetime
        ms.attrs = {'prop4' : '2017-10-23T00:00:00+0000'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop4, datetime.strptime("2017-10-23", '%Y-%m-%d'))

        # lists recursively convert each of its elements
        ms.attrs = {'prop5' : ['foo', '1', '001', '2.78', '2017-10-23T00:00:00+0000']}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop5, ['foo', 1, '001', 2.78, datetime.strptime("2017-10-23", '%Y-%m-%d')])

        ms.attrs = {'prop5' : ['foo', '1', '001', '2.78', '2017-10-23T00:00:00+0000', ['bar']]}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop5, ['foo', 1, '001', 2.78, datetime.strptime("2017-10-23", '%Y-%m-%d'), ['bar']])

        ms.attrs = {'prop5' : ['foo', '1', '001', '2.78', '2017-10-23T00:00:00+0000', {'foo':'bar'}]}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop5, ['foo', 1, '001', 2.78, datetime.strptime("2017-10-23", '%Y-%m-%d'), {'foo':'bar'}])

        # dictonaries recursively convert each of its elements
        ms.attrs = {'prop6' : {'a':'1', 'b':'001', 'c':'2.78', 'd':'2017-10-23T00:00:00+0000', 'e':'foo'}}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop6, {'a':1, 'b':'001', 'c':2.78, 'd':datetime.strptime("2017-10-23", '%Y-%m-%d'), 'e':'foo'})

        ms.attrs = {'prop6' : {'a':'1', 'b':'001', 'c':'2.78', 'd':'2017-10-23T00:00:00+0000', 'e':'foo', 'f':{'g':'h'}}}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop6, {'a':1, 'b':'001', 'c':2.78, 'd':datetime.strptime("2017-10-23", '%Y-%m-%d'), 'e':'foo', 'f':{'g':'h'}})

        ms.attrs = {'prop6' : {'a':'1', 'b':'001', 'c':'2.78', 'd':'2017-10-23T00:00:00+0000', 'e':'foo', 'f':['bar']}}
        ms.convertDict2Attrs()
        self.assertEqual(ms.prop6, {'a':1, 'b':'001', 'c':2.78, 'd':datetime.strptime("2017-10-23", '%Y-%m-%d'), 'e':'foo', 'f':['bar']})

        # certain fields remain as-is with no conversion to anything
        ms.attrs = {'id' : '12345'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.id, '12345')

        ms.attrs = {'groupName' : '12.34'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.groupName, '12.34')

        ms.attrs = {'name' : '1979-10-23T10:23:00+0000'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.name, '1979-10-23T10:23:00+0000')

        ms.attrs = {'homePhone' : '12345'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.homePhone, '12345')

        ms.attrs = {'mobilePhone1' : '12.345'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.mobilePhone1, '12.345')

        ms.attrs = {'phoneNumber' : '1979-10-23T10:23:00+0000'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.phoneNumber, '1979-10-23T10:23:00+0000')

        ms.attrs = {'postcode' : '12345'}
        ms.convertDict2Attrs()
        self.assertEqual(ms.postcode, '12345')

    def test_RequestsCounter(self):
        """Tests that MambuStruct instance has a RequestsCounter singleton"""
        self.assertEqual(getattr(self.ms, 'rc'), mambustruct.RequestsCounter())
        ms = mambustruct.MambuStruct(urlfunc=None)
        self.assertEqual(getattr(self.ms, 'rc'), getattr(ms, 'rc'))

    def test_urlfunc(self):
        """Tests setting an urlfunc"""
        self.assertEqual(getattr(self.ms, '_MambuStruct__urlfunc'), None)
        fun = lambda x:x
        ms = mambustruct.MambuStruct(urlfunc=fun, entid='', connect=False)
        ms.attrs={}
        self.assertEqual(getattr(ms, '_MambuStruct__urlfunc'), fun)

    def test_customFieldName(self):
        """Tests setting custom field name"""
        self.assertEqual(hasattr(self.ms, 'customFieldName'), False)
        ms = mambustruct.MambuStruct(urlfunc=None, customFieldName='test')
        self.assertEqual(hasattr(ms, 'customFieldName'), True)
        self.assertEqual(getattr(ms, 'customFieldName'), 'test')

    def test_private_props(self):
        """Tests private properties"""
        self.assertEqual(getattr(self.ms,'_MambuStruct__debug'), False)
        ms = mambustruct.MambuStruct(urlfunc=None, debug=True)
        self.assertEqual(getattr(ms, '_MambuStruct__debug'), True)

        self.assertEqual(getattr(self.ms,'_MambuStruct__formatoFecha'), "%Y-%m-%dT%H:%M:%S+0000")
        ms = mambustruct.MambuStruct(urlfunc=None, dateFormat="%Y%m%d")
        self.assertEqual(getattr(ms, '_MambuStruct__formatoFecha'), "%Y%m%d")

        self.assertEqual(getattr(self.ms,'_MambuStruct__data'), None)
        data={'postdata':'value'}
        ms = mambustruct.MambuStruct(urlfunc=None, data=data)
        self.assertEqual(getattr(ms, '_MambuStruct__data'), data)

        self.assertEqual(getattr(self.ms,'_MambuStruct__method'), "GET")
        ms = mambustruct.MambuStruct(urlfunc=None, method="PATCH")
        self.assertEqual(getattr(ms, '_MambuStruct__method'), "PATCH")

        self.assertEqual(getattr(self.ms,'_MambuStruct__limit'), 0)
        ms = mambustruct.MambuStruct(urlfunc=None, limit=123)
        self.assertEqual(getattr(ms, '_MambuStruct__limit'), 123)
        self.assertEqual(getattr(ms, '_MambuStruct__inilimit'), 123)

        self.assertEqual(getattr(self.ms,'_MambuStruct__offset'), 0)
        ms = mambustruct.MambuStruct(urlfunc=None, offset=321)
        self.assertEqual(getattr(ms, '_MambuStruct__offset'), 321)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test__process_fields(self, requests, json, iriToUri):
        """Test default fields (pre/post)processing"""
        # preprocess strips spaces from beginning/end of values
        json.loads.return_value = {'hello':'   goodbye   '}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms._process_fields()
        self.assertEqual(ms.hello, 'goodbye')

        # custom fields are set as properties directly under attrs,
        # instead of buried down on the customFields property
        json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                     'name': 'field',
                                                                     'id': 'fieldid',
                                                                    },
                                                    'customFieldSetGroupIndex': -1,
                                                    'value' : 'val'
                                                    },
                                                  ]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                     customFieldName='customFields')
        self.assertEqual(ms.field, 'val')
        self.assertEqual(ms.fieldid, 'val')

        # setGroupindex allows custom fields to be part of a list of
        # indexed custom fields. This sets are then named with an
        # index as a way to allow counting them.
        json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                     'name': 'field',
                                                                     'id': 'fieldid',
                                                                    },
                                                    'customFieldSetGroupIndex': 0,
                                                    'value' : 'val0'
                                                    },
                                                    {'customField' : {'state':'',
                                                                     'name': 'field',
                                                                     'id': 'fieldid',
                                                                    },
                                                    'customFieldSetGroupIndex': 1,
                                                    'value' : 'val1'
                                                    },
                                                  ]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                     customFieldName='customFields')
        self.assertEqual(ms.field_0, 'val0')
        self.assertEqual(ms.field_1, 'val1')
        self.assertEqual(ms.fieldid_0, 'val0')
        self.assertEqual(ms.fieldid_1, 'val1')

        # linkedEntityKeyValue creates a 'value' key with the value of
        # the entity key, an entity key is a pointer to some enttity
        # on Mambu, it's value is its encodingKey
        json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                     'name': 'field',
                                                                     'id': 'fieldid',
                                                                    },
                                                    'customFieldSetGroupIndex': -1,
                                                    'linkedEntityKeyValue' : 'abc123'
                                                    },
                                                  ]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                     customFieldName='customFields')
        self.assertEqual(ms.field, 'abc123')
        self.assertEqual(ms.fieldid, 'abc123')
        self.assertEqual(ms.customFields[0]['value'], 'abc123')

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_util_dateFormat(self, requests, json, iriToUri):
        """Test dateFormat"""
        from datetime import datetime
        today = datetime.now()
        # default dateFormat
        self.assertEqual(self.ms.util_dateFormat(field=today.strftime("%Y-%m-%dT%H:%M:%S+0000")).strftime("%Y%m%d%H%M%S"),
                         today.strftime("%Y%m%d%H%M%S"))
        # given format
        self.assertEqual(self.ms.util_dateFormat(field=today.strftime("%Y-%m-%dT%H:%M:%S+0000"), formato="%Y%m%d").strftime("%Y%m%d"),
                         today.strftime("%Y%m%d"))
        # format given on instantiation
        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "", dateFormat="%Y%m%d")
        self.assertEqual(ms.util_dateFormat(field=today.strftime("%Y-%m-%dT%H:%M:%S+0000"), formato="%Y%m%d").strftime("%Y%m%d"),
                         today.strftime("%Y%m%d"))

        del(self.ms._MambuStruct__formatoFecha)
        self.assertEqual(self.ms.util_dateFormat(field=today.strftime("%Y-%m-%dT%H:%M:%S+0000")).strftime("%Y%m%d%H%M%S"),
                         today.strftime("%Y%m%d%H%M%S"))

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_preprocess_postprocess(self, requests, json, iriToUri):
        """Test default preprocess and postprocess"""
        orig__process_fields                    = mambustruct.MambuStruct._process_fields
        mambustruct.MambuStruct._process_fields = mock.Mock()

        json.loads.return_value = {'hello':'goodbye'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms._process_fields.assert_called_with()
        self.assertEqual(ms._process_fields.call_count, 2)

        mambustruct.MambuStruct._process_fields = orig__process_fields

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_serializeStruct(self, requests, json, iriToUri):
        """Test serializeStruct method"""
        json.loads.return_value = {'att1':'1'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = ms.serializeStruct()
        self.assertEqual(serial, {'att1':'1'})

        orig_serializeFields                    = mambustruct.MambuStruct.serializeFields
        mambustruct.MambuStruct.serializeFields = mock.Mock()

        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        ms.serializeStruct()
        ms.serializeFields.assert_called_with(ms.attrs)
        ms.serializeFields.assert_called_with({'att1':'1'})

        mambustruct.MambuStruct.serializeFields = orig_serializeFields

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_serializeFields(self, requests, json, iriToUri):
        """Test serializeFields method"""
        # every 'normal' data type is converted to its string version
        json.loads.return_value = {'att1':1, 'att2':1.23, 'att3':'001', 'att4':'string'}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att1'], '1')
        self.assertEqual(serial['att2'], '1.23')
        self.assertEqual(serial['att3'], '001')
        self.assertEqual(serial['att4'], 'string')

        # on lists, each of its elements is recursively converted
        json.loads.return_value = {'att': [1, 1.23, '001', 'string']}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att'], ['1', '1.23', '001', 'string'])

        json.loads.return_value = {'att': [1, 1.23, '001', 'string', ['foo', 'bar']]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att'], ['1', '1.23', '001', 'string', ['foo', 'bar']])

        json.loads.return_value = {'att': [1, 1.23, '001', 'string', {'foo':'bar'}]}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att'], ['1', '1.23', '001', 'string', {'foo':'bar'}])

        # on dictionaries, each of its elements is recursively converted
        json.loads.return_value = {'att': {'a':1, 'b':1.23, 'c':'001', 'd':'string'}}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att'], {'a':'1', 'b':'1.23', 'c':'001', 'd':'string'})

        json.loads.return_value = {'att': {'a':1, 'b':1.23, 'c':'001', 'd':'string', 'e':{'foo':'bar'}}}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att'], {'a':'1', 'b':'1.23', 'c':'001', 'd':'string', 'e':{'foo':'bar'}})

        json.loads.return_value = {'att': {'a':1, 'b':1.23, 'c':'001', 'd':'string', 'e':['foo','bar']}}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms.attrs)
        self.assertEqual(serial['att'], {'a':'1', 'b':'1.23', 'c':'001', 'd':'string', 'e':['foo','bar']})

        # recursively serialize MambuStruct objects
        json.loads.return_value = {'att1':1, 'att2':1.23}
        ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        json.loads.return_value = {'att1':ms, 'att2': '001'}
        ms2 = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset : "")
        serial = mambustruct.MambuStruct.serializeFields(ms2.attrs)
        self.assertEqual(serial['att1'],{'att1':'1','att2':'1.23'})
        self.assertEqual(serial['att2'],'001')

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_create(self, requests, json, iriToUri):
        """Test create"""
        # inside __init__ if urlfunc is None connect is False
        ms = mambustruct.MambuStruct(connect=False, urlfunc=lambda entid, limit, offset : "")
        data = {"user":{"user":"moreData"}, "customInformation":["customFields"]}
        iriToUri.return_value = "http://example.com"
        requests.post.return_value = mock.Mock()
        responsePOST = {"user":{"user":"moreData"}, "customInformation":[{"customId":"id", "customValue":"value"}]}
        json.loads.return_value = responsePOST

        self.assertEqual(ms.create(data), None)
        self.assertEqual(ms.attrs, responsePOST)
        self.assertEqual(ms.keys(), responsePOST.keys())

        # if the class who call method create is direfent who implemented it
        ms.create.__func__.__module__ = "mambupy.mambuNOTSTRUCT"
        with self.assertRaisesRegexp(Exception, r"^Child method not implemented$") as ex:
            ms.create(data)

        self.assertEqual(ms._MambuStruct__method, "GET")
        self.assertEqual(ms._MambuStruct__data, None)
        self.assertTrue(ms._MambuStruct__urlfunc)


class MambuStructConnectTests(unittest.TestCase):
    """MambuStruct Connect Tests"""
    def setUp(self):
        self.tmp_bound_limit = mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    def tearDown(self):
        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = self.tmp_bound_limit

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_connect(self, requests, json, iriToUri):
        # urlfunc=None -> returns immediately
        ms = mambustruct.MambuStruct(entid='', urlfunc=None)
        self.assertIsNone(ms.connect())
        self.assertFalse(iriToUri.called)
        self.assertFalse(requests.get().called)
        self.assertFalse(json.loads.called)

        # normal load
        requests.reset_mock()
        rc_cnt = ms.rc.cnt
        iriToUri.return_value = "http://example.com"
        requests.get.return_value = mock.Mock()
        json.loads.return_value = {'field1':'value1', 'field2':'value2'}
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset, *args, **kwargs: "", user="my_user", pwd="my_password")
        requests.get.assert_called_with("http://example.com", auth=("my_user", "my_password"))
        self.assertEqual(ms.rc.cnt, rc_cnt+1)
        self.assertIsNone(ms.connect())
        self.assertEqual(ms.attrs, {'field1':'value1', 'field2':'value2'})

        # POST data
        requests.reset_mock()
        data = {'data1':'value1'}
        iriToUri.return_value = "http://example.com"
        json.dumps.return_value = data
        requests.post.return_value = mock.Mock()
        json.loads.return_value = {'field1':'value1', 'field2':'value2'}
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset, *args, **kwargs: "", data=data, user="my_user", pwd="my_password")
        requests.post.assert_called_with("http://example.com", data={'data1':'value1'}, headers={'content-type':'application/json'}, auth=("my_user", "my_password"))
        self.assertIsNone(ms.connect())
        self.assertEqual(ms.attrs, {'field1':'value1', 'field2':'value2'})

        from mambuutil import apiuser, apipwd
        requests.reset_mock()
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset, *args, **kwargs: "", data=data)
        requests.post.assert_called_with("http://example.com", data={'data1':'value1'}, headers={'content-type':'application/json'}, auth=(apiuser, apipwd))

        # PATCH data
        requests.reset_mock()
        data = {'data1':'value1'}
        iriToUri.return_value = "http://example.com"
        json.dumps.return_value = data
        requests.patch.return_value = mock.Mock()
        json.loads.return_value = {'field1':'value1', 'field2':'value2'}
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset, *args, **kwargs: "", data=data, method="PATCH", user="my_user", pwd="my_password")
        requests.patch.assert_called_with("http://example.com", data={'data1':'value1'}, headers={'content-type':'application/json'}, auth=("my_user", "my_password"))
        self.assertIsNone(ms.connect())
        self.assertEqual(getattr(ms, 'attrs', "Monty Python Flying Circus"), "Monty Python Flying Circus")

        # normal load with error
        iriToUri.return_value = ""
        requests.get.return_value = mock.Mock()
        json.loads.return_value = {'returnCode':'500', 'returnStatus':'TEST ERROR'}
        with self.assertRaisesRegexp(mambustruct.MambuError, r'^TEST ERROR$') as ex:
            ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "")

        # load list
        iriToUri.return_value = ""
        requests.get.return_value = mock.Mock()
        json.loads.return_value = [{'field1':'value1', 'field2':'value2'},
                                   {'field1':'value3', 'field2':'value4'}]
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.attrs, [{'field1':'value1', 'field2':'value2'},
                                    {'field1':'value3', 'field2':'value4'}])

        # retries mechanism
        # one Comm Error, but retrying solves it
        iriToUri.return_value = ""
        requests.get.side_effect = [ ValueError("TESTING RETRIES %s" % i) for i in range(1) ].extend( [ mock.Mock() ])
        json.loads.return_value = {'field1':'value1', 'field2':'value2'}
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "")
        self.assertEqual(ms.attrs, {'field1':'value1', 'field2':'value2'})

        # exceeds retry number
        iriToUri.return_value = ""
        requests.get.side_effect = [ ValueError("TESTING RETRIES") for i in range(mambustruct.MambuStruct.RETRIES) ]
        json.loads.return_value = {'field1':'value1', 'field2':'value2'}
        with self.assertRaisesRegexp(mambustruct.MambuCommError, r"^ERROR I can't communicate with Mambu") as ex:
            ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "")

        # MambuError
        iriToUri.return_value = ""
        requests.get.side_effect = [ mock.Mock() ]
        json.loads.side_effect = [ Exception("TEST ERROR") ]
        with self.assertRaisesRegexp(mambustruct.MambuError, r"^JSON Error: Exception\('TEST ERROR',\)$") as ex:
            ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "")

        # pagination mechanism
        mambustruct.OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1 # simulate as if Mambu could only returns one element per request
        iriToUri.return_value = ""
        requests.get.side_effect = [ mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock() ] # every time Mambu responds correctly
        json.loads.side_effect = [ [{'field1':'value1'}],
                                   [{'field2':'value2'}],
                                   [{'field3':'value3'}],
                                   [{'field4':'value4'}],
                                   [] # last time no elements means it's over
                                 ]
        # limit=0 means I want everything even though Mambu only returns 1 element per request
        # ie I want the result to have everything Mambu would send no matter its internal limit
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "", limit=0)
        self.assertEqual(len(ms.attrs), 4)

        # only get first 3 elements
        requests.get.side_effect = [ mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock() ] # every time Mambu responds correctly
        json.loads.side_effect = [ [{'field1':'value1'}],
                                   [{'field2':'value2'}],
                                   [{'field3':'value3'}],
                                   [{'field4':'value4'}],
                                   [] # last time no elements means it's over
                                 ]
        ms = mambustruct.MambuStruct(entid='12345', urlfunc=lambda entid, limit, offset: "", limit=3)
        self.assertEqual(len(ms.attrs), 3)


import mambuuser
import mambuclient
class mambustructFunctionTests(unittest.TestCase):
    """mambustruct module Functions Tests"""
    def setUp(self):
        self.ms = mambustruct.MambuStruct(urlfunc=None)

    @mock.patch('mambustruct.iriToUri')
    @mock.patch('mambustruct.json')
    @mock.patch('mambustruct.requests')
    def test_setCustomField(self, requests, json, iriToUri):
        """Test setCustomField"""
        with mock.patch('mambuuser.MambuUser') as mock_mambuuser, mock.patch('mambuclient.MambuClient') as mock_mambuclient:
            mock_mambuuser.return_value = {'id':'user123'}
            mock_mambuclient.return_value = {'id':'client123'}

            # default case: any datatype
            json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                         'name': 'field',
                                                                         'id': 'fieldid',
                                                                         'dataType': 'STRING',
                                                                        },
                                                        'customFieldSetGroupIndex': -1,
                                                        'value' : 'val'
                                                       },
                                                      ]}
            ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                         customFieldName = 'customFields')
            mambustruct.setCustomField(ms, customfield="field")
            self.assertEqual(ms.field, "val")
            mambustruct.setCustomField(ms, customfield="fieldid")
            self.assertEqual(ms.fieldid, "val")

            # user_link custom field
            json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                         'name': 'field',
                                                                         'id': 'fieldid',
                                                                         'dataType': 'USER_LINK',
                                                                        },
                                                        'customFieldSetGroupIndex': -1,
                                                        'value' : 'user123'
                                                       },
                                                      ]}
            ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                         customFieldName = 'customFields')
            mambustruct.setCustomField(ms, customfield="field")
            self.assertEqual(type(ms.field), dict)
            self.assertEqual(ms.field['id'], 'user123')
            mambustruct.setCustomField(ms, customfield="fieldid")
            self.assertEqual(type(ms.fieldid), dict)
            self.assertEqual(ms.fieldid['id'], 'user123')

            # client_link custom field
            json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                         'name': 'field',
                                                                         'id': 'fieldid',
                                                                         'dataType': 'CLIENT_LINK',
                                                                        },
                                                        'customFieldSetGroupIndex': -1,
                                                        'value' : 'client123'
                                                       },
                                                      ]}
            ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                         customFieldName = 'customFields')
            mambustruct.setCustomField(ms, customfield="field")
            self.assertEqual(type(ms.field), dict)
            self.assertEqual(ms.field['id'], 'client123')
            mambustruct.setCustomField(ms, customfield="fieldid")
            self.assertEqual(type(ms.fieldid), dict)
            self.assertEqual(ms.fieldid['id'], 'client123')

            # grouped custom field
            json.loads.return_value = {'customFields':[{'customField' : {'state':'',
                                                                         'name': 'field',
                                                                         'id': 'fieldid',
                                                                         'dataType': 'STRING',
                                                                        },
                                                        'customFieldSetGroupIndex': 0,
                                                        'value' : 'val'
                                                       },
                                                      ]}
            ms = mambustruct.MambuStruct(urlfunc=lambda entid, limit, offset, *args, **kwargs : "",
                                         customFieldName = 'customFields')
            mambustruct.setCustomField(ms, customfield="field_0")
            self.assertEqual(ms.field_0, "val")
            mambustruct.setCustomField(ms, customfield="fieldid_0")
            self.assertEqual(ms.fieldid_0, "val")


class MambuStructIteratorTests(unittest.TestCase):
    def setUp(self):
        class test_class():
            def __init__(self, wrap):
                self.iterator = mambustruct.MambuStructIterator(wrap)
            def __iter__(self):
                return self.iterator
        self.test_class = test_class

    def test_iterator(self):
        it = self.test_class(range(7))
        self.assertEqual(it.iterator.wrapped, range(7))
        self.assertEqual(it.iterator.offset, 0)

        for i,j in zip(it, range(7)):
            self.assertEqual(i, j)

        with self.assertRaises(StopIteration) as ex:
            it.iterator.next()



if __name__ == '__main__':
    unittest.main()
