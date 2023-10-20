import os
import sys
import unittest

try:
    import mock
except ModuleNotFoundError:
    import unittest.mock as mock

sys.path.insert(0, os.path.abspath("."))

from MambuPy import mambuconfig

for k, v in mambuconfig.default_configs.items():
    setattr(mambuconfig, k, v)

from MambuPy.orm import schema_orm


class SchemaOrmTests(unittest.TestCase):
    @mock.patch("MambuPy.orm.schema_orm.create_engine")
    def test_connect_dB(self, mock_create_engine):
        mock_create_engine.return_value = "test_connect_dB"
        en = schema_orm.connect_db()
        self.assertEqual(en, "test_connect_dB")
        mock_create_engine.assert_called_once_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db?charset=utf8&use_unicode=1",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        schema_orm.connect_db(echoopt=True, params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=True,
        )
        schema_orm.connect_db(engine="myeng", params="")
        mock_create_engine.assert_called_with(
            "myeng://mambu_db_user:mambu_db_pwd@localhost:3306/mambu_db",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        schema_orm.connect_db(user="myuser", params="")
        mock_create_engine.assert_called_with(
            "mysql://myuser:mambu_db_pwd@localhost:3306/mambu_db",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        schema_orm.connect_db(password="mypass", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mypass@localhost:3306/mambu_db",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        schema_orm.connect_db(host="myhost", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@myhost:3306/mambu_db",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        schema_orm.connect_db(port="myport", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:myport/mambu_db",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )
        schema_orm.connect_db(database="mydb", params="")
        mock_create_engine.assert_called_with(
            "mysql://mambu_db_user:mambu_db_pwd@localhost:3306/mydb",
            poolclass=schema_orm.NullPool,
            isolation_level="READ UNCOMMITTED",
            echo=False,
        )


if __name__ == "__main__":
    unittest.main()
