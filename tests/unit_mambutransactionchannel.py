# coding: utf-8

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
from MambuPy.rest import mambutransactionchannel

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuTransactionChannelTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import gettransactionchannelsurl

        self.assertEqual(mambutransactionchannel.mod_urlfunc, gettransactionchannelsurl)

    def test_class(self):
        a = mambutransactionchannel.MambuTransactionChannel(urlfunc=None)
        self.assertTrue(mambutransactionchannel.MambuStruct in a.__class__.__bases__)

    def test___init__(self):
        a = mambutransactionchannel.MambuTransactionChannel(urlfunc=None, entid="anything")
        self.assertEqual(a.entid, "anything")


class MambuTransactionChannelsTests(unittest.TestCase):
    def test_class(self):
        acs = mambutransactionchannel.MambuTransactionChannels(urlfunc=None)
        self.assertTrue(mambutransactionchannel.MambuStruct in acs.__class__.__bases__)

    def test_iterator(self):
        acs = mambutransactionchannel.MambuTransactionChannels(urlfunc=None)
        acs.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(acs), 3)
        for n, a in enumerate(acs):
            self.assertEqual(str(n), [k for k in a][0])
            self.assertEqual(n, a[str(n)])

    def test_convert_dict_to_attrs(self):
        from MambuPy.mambugeturl import gettransactionchannelsurl

        acs = mambutransactionchannel.MambuTransactionChannels(urlfunc=None)
        acs.attrs = [
            {"transaction_channel": "my_transaction_channel"},
            {"transaction_channel": "my_2_transaction_channel"},
        ]
        with self.assertRaisesRegex(
            AttributeError,
            "'MambuTransactionChannels' object has no attribute 'transaction_channel'",
        ):
            acs.transaction_channel
        acs.convert_dict_to_attrs()
        self.assertEqual(
            str(acs.itemclass),
            "<class 'MambuPy.rest.mambutransactionchannel.MambuTransactionChannel'>",
        )
        for a in acs:
            self.assertEqual(a.__class__.__name__, "MambuTransactionChannel")
            self.assertEqual(a._MambuStruct__urlfunc, gettransactionchannelsurl)


if __name__ == "__main__":
    unittest.main()
