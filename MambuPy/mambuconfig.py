"""Mambu configuration file.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

IMPORTANT: be careful of who can read/import this file. It may contain
sensitive data to connect to your Mambu instance, or to your DB server.

Supports ConfigParser to read a config file (in INI format) from
$HOME/.mambupy.rc, or /etc/mambupy.rc if the previous one not found.

You may edit the default_configs dictionary to have some defaults defined
even if no RC file is found (NOT RECOMMENDED)

RC files must have the following format::

    [API]
    apiurl=url_to_mambu_domain
    apiuser=API_user
    apipwd=API_password
    [DB]
    dbname=Database_name
    dbuser=Database_user
    dbpwd=Database_password
    dbhost=Database_host
    dbport=Database_port
    dbeng=Database_engine

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
"""

default_configs = {
    # Mamby API configurations
#    'API' : {
        'apiurl'  : "domain.mambu.com",
        'apiuser' : "mambu_api_user",
        'apipwd'  : "mambu_api_password",
#    },
    # Mambu DB configurations,
#    'DB' : {
        'dbname' : "mambu_db",
        'dbuser' : "mambu_db_user",
        'dbpwd'  : "mambu_db_pwd",
        'dbhost' : "localhost",
        'dbport' : "3306",
        'dbeng'  : "mysql",
#    },
}
""" Defaults dictionary for the options configured here.

You may edit this to your own liking. Beware of pricking eyes!
"""

# import ConfigParser depending on Python version
import sys, os
if sys.version_info.major < 3:
    import ConfigParser
    from ConfigParser import NoOptionError, NoSectionError
    config = ConfigParser.ConfigParser(defaults=default_configs)
else:
    import configparser
    from configparser import NoOptionError, NoSectionError
    config = configparser.ConfigParser(defaults=default_configs)

def get_conf(conf, sect, opt):
    """ Gets a config 'opt' from 'conf' file, under section 'sect'.

    If no 'opt' exists under 'sect', it looks for option on the default_configs
    dictionary

    Defaults to environmental variable named MAMBUPY_{upper_case_opt} if it
    exists, overriding whatever the conf files or default_configs dict says

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
    envir = os.environ.get(("mambupy_"+opt).upper())
    if not envir:
        try:
            return conf.get(sect,opt)
        except NoSectionError:
            return default_configs[opt]
    return envir

# Read config from $HOME/.mambupy.rc or /etc/mambupy.rc if not found
if 'HOME' not in os.environ or not config.read(os.environ['HOME']+"/.mambupy.rc"):
    config.read("/etc/mambupy.rc")

# Read configs from config file
apiurl  = get_conf(config, "API", "apiurl")
"""URL to access Mambu API"""
apiuser = get_conf(config, "API", "apiuser")
"""Username to access Mambu API"""
apipwd  = get_conf(config, "API", "apipwd")
"""Password to access Mambu API"""
dbname  = get_conf(config, "DB", "dbname")
"""Name of the DB with a backup of Mambu's DB"""
dbuser  = get_conf(config, "DB", "dbuser")
"""Username to connect to the Mambu's DB backup"""
dbpwd   = get_conf(config, "DB", "dbpwd")
"""Password to connect to the Mambu's DB backup"""
dbhost  = get_conf(config, "DB", "dbhost")
"""Host where the Mambu's DB backup lives"""
dbport  = get_conf(config, "DB", "dbport")
"""Port to connect to the host of the Mambu's DB backup"""
dbeng   = get_conf(config, "DB", "dbeng")
"""DB engine for the Mambu's DB backup"""
