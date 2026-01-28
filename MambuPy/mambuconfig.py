"""Mambu configuration file.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

IMPORTANT: be careful of who can read/import this file. It may contain
sensitive data to connect to your Mambu instance, or to your DB server.

Supports ConfigParser to read a config file (in INI format) from
$HOME/.mambupy.rc, or /etc/mambupy.rc if the previous one not found. If you
send a --mambupy_rcfile it overrides this previous behavior using the RC file
wherever you say it is.

You may edit the default_configs dictionary to have some defaults defined
even if no RC file is found (NOT RECOMMENDED)

RC files must have the following format:

.. code-block:: ini

    [API]
    apiurl=url_to_mambu_domain
    apiuser=API_user
    apipwd=API_password
    apipagination=API_pagination_limit
    activate_request_session_objects=API_persistent_session
    [DB]
    dbname=Database_name
    dbuser=Database_user
    dbpwd=Database_password
    dbhost=Database_host
    dbport=Database_port
    dbeng=Database_engine
    [MAMBUPY]
    loggingconf=Logging_conf_path

You can use environment variables to override the previous behaviour for any
option. The variable must be named as follows::

    MAMBUPY_UPPERCASEOPTION

You can use command line arguments to override the previous behaviour for any
option. The command line argument must be named as follows::

    mambupy_lowercaseoption

IMPORTANT!!! if you use argparse anywhere on your own programs using MambuPy,
then you must parse using the parse_known_args() method from your parser.
Otherwise, your programs won't work by not recognizing MambuPy's own command
line arguments.

So, the configuration hierarchy goes like this::

    0) Command line arguments (overrides any config on the following)
      1) Environment variables (overrides any config on the following)
        2) RC file sent via --mambupy_rcfile command line argument
        3) RC file at $HOME/.mambupy.rc (if previous one not found)
        4) RC file at /etc/mambupy.rc (if previous one not found)
          5) values of default_configs dictionary, if any config is absent
             on any of the previous, this is used to default it

Note for Mambu SysAdmins: please correctly configure your API user, with
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

The activate_request_session_objects config enables or disables HTTP persistent sessions
for API requests. When enabled, it will reuse the same TCP connection for
multiple requests, improving performance. Default is False.
"""

default_configs = {
    # Mambu API configurations
    "apiurl": "domain.mambu.com",
    "apiuser": "mambu_api_user",
    "apipwd": "mambu_api_password",
    "apipagination": "50",
    "activate_request_session_objects": "False",
    # Mambu DB configurations
    "dbname": "mambu_db",
    "dbuser": "mambu_db_user",
    "dbpwd": "mambu_db_pwd",
    "dbhost": "localhost",
    "dbport": "3306",
    "dbeng": "mysql",
    # MambuPy configurations
    "loggingconf": "",  # empty string means default logging, path to a yaml for logging configuration
}
""" Defaults dictionary for the options configured here.

You may edit this to your own liking. But beware of pricking eyes!
"""

import os
import configparser
from configparser import NoSectionError

config = configparser.ConfigParser(defaults=default_configs)

# argparse for command line arguments overriding
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--mambupy_rcfile")
argparser.add_argument("--mambupy_apiurl")
argparser.add_argument("--mambupy_apiuser")
argparser.add_argument("--mambupy_apipwd")
argparser.add_argument("--mambupy_apipagination")
argparser.add_argument("--mambupy_activate_request_session_objects")
argparser.add_argument("--mambupy_dbname")
argparser.add_argument("--mambupy_dbuser")
argparser.add_argument("--mambupy_dbpwd")
argparser.add_argument("--mambupy_dbhost")
argparser.add_argument("--mambupy_dbport")
argparser.add_argument("--mambupy_dbeng")
argparser.add_argument("--mambupy_loggingconf")
args, unknown = argparser.parse_known_args()


def get_conf(conf, sect, opt):
    """Gets a config 'opt' from 'conf' file, under section 'sect'.

    If no 'opt' exists under 'sect', it looks for option on the default_configs
    dictionary

    If there exists an environmental variable named MAMBUPY_{upper_case_opt},
    it overrides whatever the conf files or default_configs dict says.

    But if you send a command line argument named mambupy_{lower_case_opt},
    it overrides anything else.

    Args:
     conf (ConfigParser): ConfigParser that reads from certain config file (INI
                          format)
     sect (string): section under the config file
     opt (string): option to read

    Returns:
     string: configuration option. If not found on conf, returns a value from
             default_configs dict. If environmental variable exists with name
             MAMBUPY_{upper_case_opt} it overrides anything else
    """
    argu = getattr(args, "mambupy_" + opt.lower())

    if not argu:
        envir = os.environ.get("MAMBUPY_" + opt.upper())
        if not envir:
            try:
                return conf.get(sect, opt)
            except NoSectionError:
                return default_configs[opt]
        return envir
    return argu


# Read config from --mambupy_rcfile, or $HOME/.mambupy.rc if not found, or
# /etc/mambupy.rc if not found
if not args.mambupy_rcfile or not config.read(args.mambupy_rcfile):
    if "HOME" not in os.environ or not config.read(os.environ["HOME"] + "/.mambupy.rc"):
        config.read("/etc/mambupy.rc")

# Read configs from config file
apiurl = get_conf(config, "API", "apiurl")
"""URL to access Mambu API"""
apiuser = get_conf(config, "API", "apiuser")
"""Username to access Mambu API"""
apipwd = get_conf(config, "API", "apipwd")
"""Password to access Mambu API"""
apipagination = get_conf(config, "API", "apipagination")
"""Pagination default limit for requests to Mambu API"""
activate_request_session_objects = get_conf(config, "API", "activate_request_session_objects")
"""Whether to use persistent HTTP sessions for API requests"""
dbname = get_conf(config, "DB", "dbname")
"""Name of the DB with a backup of Mambu's DB"""
dbuser = get_conf(config, "DB", "dbuser")
"""Username to connect to the Mambu's DB backup"""
dbpwd = get_conf(config, "DB", "dbpwd")
"""Password to connect to the Mambu's DB backup"""
dbhost = get_conf(config, "DB", "dbhost")
"""Host where the Mambu's DB backup lives"""
dbport = get_conf(config, "DB", "dbport")
"""Port to connect to the host of the Mambu's DB backup"""
dbeng = get_conf(config, "DB", "dbeng")
"""DB engine for the Mambu's DB backup"""
loggingconf = get_conf(config, "MAMBUPY", "loggingconf")
"""Directory where to store logs"""
