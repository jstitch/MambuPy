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


class MambuConfigTests(unittest.TestCase):
    def setUp(self):
        with open("/tmp/test.ini", "w") as f:
            f.write(
                """[SECTION1]
Test=Value
Hello=World
[SECTION2]
Another=BrickInTheWall
"""
            )
        defaults = {"AllInAll": "You'reJust"}
        import sys

        if sys.version_info.major < 3:
            import ConfigParser

            self.config = ConfigParser.ConfigParser(defaults=defaults)
        else:
            import configparser

            self.config = configparser.ConfigParser(defaults=defaults)

    def test_api_attrs(self):
        try:
            mambuconfig.apiurl
        except AttributeError:
            self.fail("No apiurl attribute in mambuconfig")
        try:
            mambuconfig.apiuser
        except AttributeError:
            self.fail("No apiuser attribute in mambuconfig")
        try:
            mambuconfig.apipwd
        except AttributeError:
            self.fail("No apipwd attribute in mambuconfig")
        try:
            mambuconfig.apipagination
        except AttributeError:
            self.fail("No apipagination attribute in mambuconfig")

    def test_db_attrs(self):
        try:
            mambuconfig.dbname
        except AttributeError:
            self.fail("No dbname attribute in mambuconfig")
        try:
            mambuconfig.dbuser
        except AttributeError:
            self.fail("No dbuser attribute in mambuconfig")
        try:
            mambuconfig.dbpwd
        except AttributeError:
            self.fail("No dbpwd attribute in mambuconfig")
        try:
            mambuconfig.dbhost
        except AttributeError:
            self.fail("No dbhost attribute in mambuconfig")
        try:
            mambuconfig.dbport
        except AttributeError:
            self.fail("No dbport attribute in mambuconfig")
        try:
            mambuconfig.dbeng
        except AttributeError:
            self.fail("No dbeng attribute in mambuconfig")

    def test_default_configs(self):
        self.assertEqual(mambuconfig.default_configs.get("apiurl"), "domain.mambu.com")
        self.assertEqual(mambuconfig.default_configs.get("apiuser"), "mambu_api_user")
        self.assertEqual(mambuconfig.default_configs.get("apipwd"), "mambu_api_password")
        self.assertEqual(mambuconfig.default_configs.get("apipagination"), "50")
        self.assertEqual(mambuconfig.default_configs.get("dbname"), "mambu_db")
        self.assertEqual(mambuconfig.default_configs.get("dbuser"), "mambu_db_user")
        self.assertEqual(mambuconfig.default_configs.get("dbpwd"), "mambu_db_pwd")
        self.assertEqual(mambuconfig.default_configs.get("dbhost"), "localhost")
        self.assertEqual(mambuconfig.default_configs.get("dbport"), "3306")
        self.assertEqual(mambuconfig.default_configs.get("dbeng"), "mysql")

    def test_get_conf(self):
        self.config.read("/tmp/test.ini")
        mambuconfig.args = mock.Mock()
        mambuconfig.args.mambupy_test = None
        mambuconfig.args.mambupy_hello = None
        mambuconfig.args.mambupy_another = None
        self.assertEqual(mambuconfig.get_conf(self.config, "SECTION1", "Test"), "Value")
        self.assertEqual(mambuconfig.get_conf(self.config, "SECTION1", "Hello"), "World")
        self.assertEqual(
            mambuconfig.get_conf(self.config, "SECTION2", "Another"), "BrickInTheWall"
        )

    def test_defaults(self):
        mambuconfig.default_configs["AllInAll"] = "You'reJust"
        mambuconfig.args = mock.Mock()
        mambuconfig.args.mambupy_allinall = None
        self.assertEqual(
            mambuconfig.get_conf(self.config, "SECTION1", "AllInAll"), "You'reJust"
        )
        self.config.read("/tmp/test.ini")
        self.assertEqual(self.config.get("SECTION1", "AllInAll"), "You'reJust")
        self.assertEqual(self.config.get("SECTION2", "AllInAll"), "You'reJust")

    def test_environ(self):
        self.config.read("/tmp/test.ini")
        mambuconfig.args = mock.Mock()
        mambuconfig.args.mambupy_test = None
        self.assertEqual(mambuconfig.get_conf(self.config, "SECTION1", "Test"), "Value")
        os.environ["MAMBUPY_TEST"] = "OtherValue"
        self.assertEqual(
            mambuconfig.get_conf(self.config, "SECTION1", "Test"), "OtherValue"
        )
        del os.environ["MAMBUPY_TEST"]

    def test_args(self):
        self.config.read("/tmp/test.ini")
        mambuconfig.args = mock.Mock()
        mambuconfig.args.mambupy_test = "OtherValue"
        self.assertEqual(
            mambuconfig.get_conf(self.config, "SECTION1", "Test"), "OtherValue"
        )


if __name__ == "__main__":
    unittest.main()
