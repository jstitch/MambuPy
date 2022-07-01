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
from MambuPy.rest import mambuproduct

try:
    unittest.TestCase.assertRegexpMatches = unittest.TestCase.assertRegex  # python3
except Exception as e:
    pass  # DeprecationWarning: Please use assertRegex instead


class MambuProductTests(unittest.TestCase):
    def test_mod_urlfunc(self):
        from MambuPy.mambugeturl import getproductsurl

        self.assertEqual(mambuproduct.mod_urlfunc, getproductsurl)

    def test_class(self):
        p = mambuproduct.MambuProduct(urlfunc=None)
        self.assertTrue(mambuproduct.MambuStruct in p.__class__.__bases__)

    def test___init__(self):
        p = mambuproduct.MambuProduct(urlfunc=None, entid="anything")
        self.assertEqual(p.entid, "anything")

    def test___repr__(self):
        from MambuPy.mambugeturl import getproductsurl

        def build_mock_prod_1(self, *args, **kwargs):
            self.attrs = {"id": args[1]}

        with mock.patch.object(mambuproduct.MambuStruct, "__init__", build_mock_prod_1):
            p = mambuproduct.MambuProduct(urlfunc=getproductsurl, entid="mockproduct")
            self.assertRegexpMatches(repr(p), r"^MambuProduct - id: mockproduct")


class MambuProductsTests(unittest.TestCase):
    def test_class(self):
        prods = mambuproduct.MambuProducts(urlfunc=None)
        self.assertTrue(mambuproduct.MambuStruct in prods.__class__.__bases__)

    def test_iterator(self):
        prods = mambuproduct.MambuProducts(urlfunc=None)
        prods.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(prods), 3)
        for n, p in enumerate(prods):
            self.assertEqual(str(n), [k for k in p][0])
            self.assertEqual(n, p[str(n)])

    def test_convertDict2Attrs(self):
        prods = mambuproduct.MambuProducts(urlfunc=None)
        prods.attrs = [
            {"id": "1", "name": "my_product"},
            {"id": "2", "name": "my_2_product"},
        ]
        with self.assertRaisesRegexp(
            AttributeError,
            "'MambuProducts' object has no attribute 'mambuproductclass'",
        ):
            prods.mambuproductclass
        prods.convertDict2Attrs()
        self.assertEqual(
            str(prods.mambuproductclass),
            "<class 'MambuPy.rest.mambuproduct.MambuProduct'>",
        )
        for p in prods:
            self.assertEqual(p.__class__.__name__, "MambuProduct")


class AllMambuProductsTests(unittest.TestCase):
    def test_Singleton(self):
        """Tests that AllMambuProducts instance is a singleton"""

        def build_mock_prod_1(self, *args, **kwargs):
            self.attrs = {"encodedKey": args[1]}

        with mock.patch.object(mambuproduct.MambuStruct, "__init__", build_mock_prod_1):
            prods = mambuproduct.AllMambuProducts(urlfunc=None)
            prods2 = mambuproduct.AllMambuProducts(urlfunc=None)
            self.assertEqual(prods, prods2)

    def test_noinit(self):
        """Test noinit property"""
        prods = mambuproduct.AllMambuProducts(urlfunc=None)

        self.assertEqual(prods.noinit, True)

    def test_class(self):
        prods = mambuproduct.AllMambuProducts(urlfunc=None)
        self.assertTrue(mambuproduct.MambuStruct in prods.__class__.__bases__)

    def test_getattribute(self):
        prods = mambuproduct.AllMambuProducts(urlfunc=None)
        prods.attr1 = "hello"
        del prods.noinit
        del prods.mambuproductclass
        self.assertEqual(prods.attr1, "hello")
        with self.assertRaises(AttributeError):
            prods.params
        with self.assertRaises(AttributeError):
            prods.noinit
        with self.assertRaises(AttributeError):
            prods.mambuproductclass

    def test_iterator(self):
        prods = mambuproduct.AllMambuProducts(urlfunc=None)
        prods.attrs = [{"0": 0}, {"1": 1}, {"2": 2}]
        self.assertEqual(len(prods), 3)
        for n, p in enumerate(prods):
            self.assertEqual(str(n), [k for k in p][0])
            self.assertEqual(n, p[str(n)])

    def test_convertDict2Attrs(self):
        from MambuPy.mambugeturl import getproductsurl

        prods = mambuproduct.AllMambuProducts(urlfunc=None)
        prods.attrs = [
            {"id": "1", "name": "my_product"},
            {"id": "2", "name": "my_2_product"},
        ]
        prods.convertDict2Attrs()
        self.assertEqual(
            str(prods.mambuproductclass),
            "<class 'MambuPy.rest.mambuproduct.MambuProduct'>",
        )
        for p in prods:
            self.assertEqual(p.__class__.__name__, "MambuProduct")
            self.assertEqual(p._MambuStruct__urlfunc, getproductsurl)


if __name__ == "__main__":
    unittest.main()
