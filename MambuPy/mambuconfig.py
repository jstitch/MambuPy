"""Mambu configuration file.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

IMPORTANT: be careful of who can read/import this file. It may contain
sensitive data to connect to your Mambu instance, or to your DB server.

Note for Mamby SysAdmins: please correctly configure your API user, with
right permissions that allow your users to access the data you wish to
make available but not to make any changes/access any information you
don't wish to be accessed. Please mind that this may restrict some of
the Mambu objects at the MambuPy package to don't be fully available to
python users of this library.

Note for DBAs: to increase security, configure your DB user to access
the Mambu DB backup so that it cannot access any other DB tables you
don't wish to be accessed by any other user

The api* configs are Mambu API configurations, you must have a valid API
user on your Mambu instance

The db* configs refer to Database configurations which hold a backup of
your Mambu Database on some server.

.. todo:: yep, perhaps this is the worst way to configure permissions.
          Looking for another more secure way to do it.
"""

# Mamby API configurations
apiurl  = "domain.mambu.com"
apiuser = "mambu_api_user"
apipwd  = "mambu_api_password"

# Mambu DB configurations
dbname  = "mambu_db"
dbuser  = "mambu_db_user"
dbpwd   = "mambu_db_pwd"
dbhost  = "localhost"
dbport  = "3306"
dbeng   = "mysql"
