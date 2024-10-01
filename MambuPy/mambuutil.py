"""Mambu utilites module.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

Exceptions, some API return codes, utility functions, a lot of urlfuncs
(see MambuStruct.__init__ and .connect pydocs for more info on this)

.. warning::

   Secutiry WARNING: Imports the configurations from mambuconfig. It surely
   is a bad idea. Got to improve this!

.. todo:: status API V2: fullDetails are not compatible

.. todo:: status API V2: pagination managements needs review

.. todo:: status API V2: almost al GET operations seems
          compatible. PATCH/POST/DELETE operations needs review

.. todo:: status API V2: testing of EVERYTHING is required """

from .mambugeturl import getmambuurl
from .mambuconfig import apipwd, apiurl, apiuser, apipagination

try:
    # python2
    unicode
except NameError:
    # python3
    unicode = str

import json
import sys

from datetime import datetime, timezone

API_RETURN_CODES = {
    "SUCCESS": 0,
    "INVALID_PARAMETERS": 4,
    "INVALID_LOAN_ACCOUNT_ID": 100,
    "INVALID_ACCOUNT_STATE": 105,
    "EXCESS_REPAYMENT_ERROR": 110,
    "INVALID_REPAYMENT_DATE_ERROR": 111,
    "INVALID_STATE_TRANSITION": 116,
    "INVALID_ACCOUNT_STATE_FOR_REPAYMENTS": 128,
    "INCONSISTENT_SCHEDULE_PRINCIPAL_DUE_WITH_LOAN_AMOUNT": 132,
}
"""
.. deprecated:: 0.8
  It's probably not useful. Besides, :any:`mambustruct.MambuStruct.connect()`
  method returns the code when an error occurs by default.
"""


OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = int(apipagination)
"""Current maximum number of response elements Mambu returns"""


PAGINATIONDETAILS = ["ON", "OFF"]
"""paginationDetails options"""


DETAILSLEVEL = ["BASIC", "FULL"]
"""detailsLevel options"""

MAX_UPLOAD_SIZE = 52428800  # 50Mb
"""upload files maximum size"""

UPLOAD_FILENAME_INVALID_CHARS = "/><|:&?*[]#\*`"
"""invalid characters for an uploaded filename"""

ALLOWED_UPLOAD_MIMETYPES = [
    "JPEG",
    "PNG",
    "GIF",
    "BMP",
    "TIFF",
    "PDF",
    "XML",
    "DOC",
    "DOCX",
    "DOCM",
    "DOT",
    "DOTX",
    "DOTM",
    "XLS",
    "XLSX",
    "XLSB",
    "PPT",
    "PPTX",
    "ODT",
    "OTT",
    "FODT",
    "PDF",
    "XML",
    "TXT",
    "CSV",
    "PROPERTIES",
    "MSG",
    "TIF",
    "ZIP",
    "RTF",
    "XLSM",
    "ODS",
    "ODP",
    "EML",
    "EMLX",
    "HTML",
    "MHT",
    "MHTML",
    "XPS",
    "NUMBERS",
    "KEY",
    "PAGES",
    "YAML",
    "JSON",
    "JASPER",
    "JRXML",
]
"""allowed file types for uploads"""

SEARCH_OPERATORS = [
    "EQUALS",
    "EQUALS_CASE_SENSITIVE",
    "DIFFERENT_THAN",
    "MORE_THAN",
    "LESS_THAN",
    "BETWEEN",
    "ON",
    "AFTER",
    "BEFORE",
    "BEFORE_INCLUSIVE",
    "STARTS_WITH",
    "STARTS_WITH_CASE_SENSITIVE",
    "IN",
    "TODAY",
    "THIS_WEEK",
    "THIS_MONTH",
    "THIS_YEAR",
    "LAST_DAYS",
    "EMTPY",
    "NOT_EMPTY",
]
"""search operators"""


class MambuPyError(Exception):
    """Default exception"""


class MambuError(MambuPyError):
    """Default exception from Mambu"""


class MambuCommError(MambuError):
    """Thrown when communication issues with Mambu arise"""


### More utility functions follow ###
def date_format(field, formato=None, as_utc=False):
    """Converts a datetime field to a datetime using some specified format.

    What this really means is that, if specified format includes only for
    instance just year and month, day and further info gets ignored and the
    objects get a datetime with year and month, and day 1, hour 0, minute 0,
    etc.

    A useful format may be %Y%m%d, then the datetime objects effectively
    translates into date objects alone, with no relevant time information.

    When as_utc is True, the datetime object is converted to UTC timezone.

    PLEASE BE AWARE, that this may lose useful information for your datetimes
    from Mambu. Read this for why this may be a BAD idea:
    https://julien.danjou.info/blog/2015/python-and-timezones
    """
    from datetime import datetime

    if not formato:
        formato = "%Y-%m-%dT%H:%M:%S"
    if sys.version_info < (3, 0):
        return datetime.strptime(
            datetime.strptime(field, "%Y-%m-%dT%H:%M:%S+0000").strftime(formato),
            formato,
        )
    else:
        field_as_dt = datetime.strptime(
            datetime.fromisoformat(field).strftime(formato),
            formato,
        )
        if as_utc:
            field_as_dt = field_as_dt.astimezone(
                timezone.utc
            ).replace(tzinfo=None)
        return field_as_dt


def strip_tags(html):
    """Stripts HTML tags from text.

    Note fields on several Mambu entities come with additional HTML tags
    (they are rich text fields, I guess that's why). Sometimes they are
    useless, so stripping them is a good idea.
    """
    from html.parser import HTMLParser

    class MLStripper(HTMLParser):
        """Aux class for stripping HTML tags.

         fields on several Mambu entities come with additional HTML tags
        (they are rich text fields, I guess that's why). Sometimes they are
        useless, so stripping them is a good idea.
        """

        def __init__(self):
            try:
                super().__init__()  # required for python3
            except TypeError:  # pragma: no cover
                pass  # with python2 raises TypeError
            self.reset()
            self.fed = []

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return "".join(self.fed)

    s = MLStripper()
    s.feed(html.replace("&nbsp;", " "))
    return s.get_data()


def strip_consecutive_repeated_char(s, ch):
    """Strip characters in a string which are consecutively repeated.

    Useful when in notes or some other free text fields on Mambu, users
    capture anything and a lot of capture errors not always detected by
    Mambu get through. You want some cleaning? this may be useful.

    This is a string processing function.
    """
    sdest = ""
    for i, c in enumerate(s):
        if i != 0 and s[i] == ch and s[i] == s[i - 1]:
            continue
        sdest += s[i]
    return sdest


if sys.version_info >= (3, 0):
    # python3
    from future.moves.urllib import parse as urlparse
else:  # pragma: no cover
    # python2
    import urlparse


def iri_to_uri(iri):
    """Change an IRI (internationalized R) to an URI.

    Used at MambuStruct.connect() method for any requests done to Mambu.

    Perfect example of unicode getting in the way.

    Illustrative (I hope) example: I have Mambu usernames with special
    chars in them. When retrieving them and then trying to build a
    MambuUser object with them, I get a BIG problem because of the
    unicode chars there. Using this I solved the problem.
    """

    def url_encode_non_ascii(b):
        """Encode Non ASCII chars to URL-friendly chars.

        Sometimes unicode gets in the way. A shame, I know. And perhaps the
        biggest shame is not me correctly handling it.
        """
        import re

        return re.sub("[\x80-\xFF]", lambda c: "%%%02x" % ord(c.group(0)), b)

    parts = urlparse.urlparse(iri)
    if sys.version_info < (3, 0):  # pragma: no cover
        # python2
        partes = []
        for parti, part in enumerate(parts):
            try:
                if parti != 1:
                    partes.append(url_encode_non_ascii(part.encode("utf-8")))
                else:
                    partes.append(part.encode("idna"))
            except UnicodeDecodeError:
                partes.append(url_encode_non_ascii(part.decode("latin")))
            except Exception:
                raise Exception
        return urlparse.urlunparse(partes)
    else:
        # python3
        uri = [part.decode("utf8") for parti, part in enumerate(parts.encode("utf8"))]
        return urlparse.urlunparse(uri)


def encoded_dict(in_dict):
    """Encode every value of a dict to UTF-8.

    Useful for POSTing requests on the 'data' parameter of urlencode.
    """
    out_dict = {}
    for k, v in in_dict.items():
        if isinstance(v, unicode):
            if sys.version_info < (3, 0):  # pragma: no cover
                v = v.encode("utf8")
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            if sys.version_info < (3, 0):  # pragma: no cover
                v.decode("utf8")
        out_dict[k] = v
    return out_dict


from time import sleep

import requests


def _backup_db_previous_prep(callback, kwargs):
    list_ret = []
    try:
        verbose = kwargs["verbose"]
    except KeyError:
        verbose = False
    list_ret.append(verbose)
    try:
        retries = kwargs["retries"]
    except KeyError:
        retries = -1
    list_ret.append(retries)
    try:
        justbackup = kwargs["justbackup"]
    except KeyError:
        justbackup = False
    list_ret.append(justbackup)
    try:
        force_download_latest = bool(kwargs["force_download_latest"])
    except KeyError:
        force_download_latest = False
    list_ret.append(force_download_latest)
    try:
        headers = kwargs["headers"]
    except KeyError:
        headers = {
            "Accept": "application/vnd.mambu.v2+zip",
        }
    list_ret.append(headers)

    if verbose:
        log = open("/tmp/log_mambu_backup", "a")
        log.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - Mambu DB Backup\n")
        log.flush()
    else:
        log = None
    list_ret.append(log)

    user = kwargs.pop("user", apiuser)
    list_ret.append(user)

    pwd = kwargs.pop("pwd", apipwd)
    list_ret.append(pwd)

    data = {"callback": callback}
    list_ret.append(data)

    return list_ret


def _backup_db_request(justbackup, data, user, pwd, verbose=None, log=None):
    try:
        if not justbackup:
            posturl = iri_to_uri(getmambuurl() + "database/backup")
            if verbose:
                log.write("open url: " + posturl + "\n")
                log.write("data: " + str(data) + "\n")
                log.flush()
            resp = requests.post(
                posturl,
                data=json.dumps(data),
                headers={
                    "content-type": "application/json",
                    "Accept": "application/vnd.mambu.v2+json",
                },
                auth=(user, pwd),
            )
            if verbose:
                log.write(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    + " - "
                    + str(resp.content)
                    + "\n"
                )
                log.write(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    + " - "
                    + resp.request.url
                    + "\n"
                )
                log.write(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    + " - "
                    + resp.request.body
                    + "\n"
                )
                log.write(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    + " - "
                    + str(resp.request.headers)
                    + "\n"
                )
                log.flush()
    except Exception as ex:
        mess = "Error requesting backup: %s" % repr(ex)
        if verbose:
            log.write(mess + "\n")
            log.close()
        raise MambuError(mess)

    if not justbackup and resp.status_code != 202:
        mess = "Error posting request for backup: %s" % resp.content
        if verbose:
            log.write(mess + "\n")
            log.close()
        raise MambuCommError(mess)


def _backup_db_timeout_mechanism(
    justbackup, retries, bool_func, force_download_latest, verbose=None, log=None
):
    value_to_latest = True
    while not justbackup and retries and not bool_func():
        if verbose:
            log.write("waiting...\n")
            log.flush()
        sleep(10)
        retries -= 1
        if retries < 0:
            retries = -1
    if not justbackup and not retries:
        mess = "Tired of waiting, giving up..."
        if verbose:
            log.write(mess + "\n")
            log.flush()
        if not force_download_latest:
            if verbose:
                log.close()
            raise MambuError(mess)
        else:
            value_to_latest = False
    sleep(30)

    return value_to_latest


def _backup_db_request_download_backup(user, pwd, headers, verbose=None, log=None):
    geturl = iri_to_uri(getmambuurl() + "database/backup/LATEST")
    if verbose:
        log.write("open url: " + geturl + "\n")
        log.flush()
    resp = requests.get(geturl, auth=(user, pwd), headers=headers)

    if resp.status_code != 200:
        mess = "Error getting database backup: %s" % resp.content
        if verbose:
            log.write(mess + "\n")
            log.close()
        raise MambuCommError(mess)

    return resp


def _backup_db_post_processing(resp, output_fname, verbose=None, log=None):
    if verbose:
        log.write("saving...\n")
        log.flush()
    with open(output_fname, "wb") as fw:
        fw.write(resp.content)


def backup_db(callback, bool_func, output_fname, *args, **kwargs):
    """Backup Mambu Database via REST API.

    Makes two calls to Mambu API:

    - a POST to request a backup to be made

    - a GET, once the backup is ready, to download the latest backup

    * callback is a string to a callback URL Mambu will internally call
      when the backup is ready to download. You should have a webservice
      there to warn you when the backup is ready.

    * bool_func is a function you use against your own code to test if the
      said backup is ready. This function backup_db manages both the logic
      of the request of a backup and the downloading of it too, so
      bool_func allows you to have some way on your side to know when this
      function will download the backup.

      The thing is you have to build a webservice (for the callback)
      making some kind of flag turn that your bool_func will read and know
      when to say True, telling backup_db to begin the download of the
      backup.

    * output_fname the name of the file that will hold the downloaded
      backup. PLEASE MIND that Mambu sends a ZIP file here.

    * user, pwd and url allow you to change the Mambu permissions for
      the getmambuurl internally called here.

    * verbose is a boolean flag for verbosity.

    * retries number of retries for bool_func or -1 for keep waiting.

    * just_backup bool if True, skip asking for backup, just download LATEST

    * force_download_latest boolean, True to force download even if no
      callback is called. False to throw error if callback isn't received
      after retries.

    * returns a dictionary with info about the download
        -latest     boolean flag, if the db downloaded was the latest or not

    .. todo:: status API V2: compatible
    """

    # previous preparation
    (
        verbose,
        retries,
        justbackup,
        force_download_latest,
        headers,
        log,
        user,
        pwd,
        data,
    ) = _backup_db_previous_prep(callback, kwargs)

    # POST to request Mambu to prepare backup of its own DB
    _backup_db_request(justbackup, data, user, pwd, verbose, log)

    # wait & timeout mechanism
    data["latest"] = _backup_db_timeout_mechanism(
        justbackup, retries, bool_func, force_download_latest, verbose, log
    )

    # GET request to download LATEST Mambu's DB backup
    resp = _backup_db_request_download_backup(user, pwd, headers, verbose, log)

    # post-processing
    _backup_db_post_processing(resp, output_fname, verbose, log)

    # no refactor
    if verbose:
        log.write("DONE!\n")
        log.close()

    return data
