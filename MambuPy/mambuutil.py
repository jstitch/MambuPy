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
from .mambuconfig import (apipwd, apiurl, apiuser, dbeng, dbhost, dbname,
                          dbport, dbpwd, dbuser)

try:
    # python2
    unicode
except NameError:
    # python3
    unicode = str

import sys

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


OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 1000
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


# Connects to DB
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


def connectDb(
    engine=dbeng,
    user=dbuser,
    password=dbpwd,
    host=dbhost,
    port=dbport,
    database=dbname,
    params="?charset=utf8&use_unicode=1",
    echoopt=False,
):
    """Connect to database utility function.

    Uses SQLAlchemy ORM library.

    Useful when using schema modules in MambuPy
    """
    return create_engine(
        "%s://%s:%s@%s:%s/%s%s" % (engine, user, password, host, port, database, params),
        poolclass=NullPool,
        isolation_level="READ UNCOMMITTED",
        echo=echoopt,
    )


def getmambuurl(url=apiurl, *args, **kwargs):
    """Basic Mambu URL function. Builds the Mambu basic request string.

    Receives a user, password and url arguments to connect to Mambu.
    Defaults to what mambuconfig has, but you may override it by sending
    'user', 'pwd' and 'url' parameters at the Mambu object instantiation
    (for instance: MambuLoan(user=myuser, pwd=mypwd, url=myurl,
    entid='12345', ...)

    .. todo:: status API V2: compatible
    """
    mambuurl = "https://" + url + "/api/"
    return mambuurl


###*** Behold, the urlfuncs magic follows ***###
# This things are the gateways for implementing parameters on requests done to
# the Mambu REST API.


def getbranchesurl(idbranch, *args, **kwargs):
    """Request Branches URL.

    If idbranch is set, you'll get a response adequate for a MambuBranch object.
    If not set, you'll get a response adequate for a MambuBranches object.
    See mambubranch module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    branchidparam = "" if idbranch == "" else "/" + idbranch
    url = (
        getmambuurl(*args, **kwargs)
        + "branches"
        + branchidparam
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getcentresurl(idcentre, *args, **kwargs):
    """Request Centres URL.

    If idcentre is set, you'll get a response adequate for a MambuCentre object.
    If not set, you'll get a response adequate for a MambuCentres object.
    See mambucentre module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    centreidparam = "" if idcentre == "" else "/" + idcentre
    url = (
        getmambuurl(*args, **kwargs)
        + "centres"
        + centreidparam
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getrepaymentsurl(idcred, *args, **kwargs):
    """Request loan Repayments URL.

    If idcred is set, you'll get a response adequate for a
    MambuRepayments object. There's a MambuRepayment object too, but
    you'll get a list first and each element of it will be automatically
    converted to a MambuRepayment object that you may use.

    If not set, you'll get a Jar Jar Binks object, or something quite
    strange and useless as JarJar. A MambuError must likely since I
    haven't needed it for anything but for repayments of one and just
    one loan account.

    See mamburepayment module and pydoc for further information.

    Currently implemented GET filter parameters:
        * fullDetails
        * limit
        * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "loans/"
        + idcred
        + "/repayments"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getsavingssurl(idcred, *args, **kwargs):
    """Request loan savings URL.

    If idcred is set, you'll get a response adequate for a
    MambuSaving object.

    Currently implemented GET filter parameters:
        * fullDetails
        * limit
        * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible . Apparently changing
              'savings' to 'deposits' may work
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "savings/"
        + idcred
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getsavingfundingrepaymentsurl(idcred, loan_id, *args, **kwargs):
    """Request loan saving Repayments URL.

    If idcred is set, you'll get a response adequate for a
    MambuSaving object.

    Currently implemented GET filter parameters:
        * fullDetails
        * limit
        * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "savings/"
        + idcred
        + "/funding/"
        + loan_id
        + "/repayments"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getsavingstransactionsurl(idcred, *args, **kwargs):
    """Request saving transaction URL.

    If idcred is set, you'll get a response adequate for a
    MambuSavingTransaction object.

    Currently implemented GET filter parameters:
        * fullDetails
        * limit
        * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible . Apparently changing
              'savings' to 'deposits' may work
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "savings/"
        + idcred
        + "/transactions/"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getsavingstransactionssearchurl(idcred, *args, **kwargs):
    """Request saving transaction URL.

    idcred is not used - search is rather defined via POST filter parameter.

    Currently implemented GET filter parameters:
        * fullDetails
        * limit
        * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible . Apparently changing
              'savings' to 'deposits' may work
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "savings/transactions/search"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def gettransactionchannelsurl(idcred, *args, **kwargs):
    """Transaction channels URL.

    If idcred is set, you'll get a response adequate for a
    MambuTransactionChannel object.

    Currently implemented GET filter parameters:
        * fullDetails
        * limit
        * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible . Apparently changing
              URL to /organization/transactionchannels may work
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "transactionchannels/"
        + idcred
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getloansurl(idcred, *args, **kwargs):
    """Request Loans URL.

    If idcred is set, you'll get a response adequate for a MambuLoan object.
    If not set, you'll get a response adequate for a MambuLoans object.
    See mambuloan module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * accountState
    * branchId
    * centreId
    * creditOfficerUsername
    * fixedDaysOfMonth
    * startDate
    * endDate
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: GET compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("accountState=%s" % kwargs["accountState"])
        except Exception:
            pass
        try:
            getparams.append("branchId=%s" % kwargs["branchId"])
        except Exception:
            pass
        try:
            getparams.append("centreId=%s" % kwargs["centreId"])
        except Exception:
            pass
        try:
            getparams.append("creditOfficerUsername=%s" % kwargs["creditOfficerUsername"])
        except Exception:
            pass
        try:
            getparams.append("startDate=%s" % kwargs["startDate"])
        except Exception:
            pass
        try:
            getparams.append("endDate=%s" % kwargs["endDate"])
        except Exception:
            pass
        try:
            getparams.append("fixedDaysOfMonth=%s" % kwargs["fixedDaysOfMonth"])
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    idcredparam = "" if idcred == "" else "/" + idcred
    url = (
        getmambuurl(*args, **kwargs)
        + "loans"
        + idcredparam
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getloanscustominformationurl(idcred, customfield="", *args, **kwargs):
    """Request Loan Custom Information URL.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    loanidparam = "/" + idcred
    url = (
        getmambuurl(*args, **kwargs)
        + "loans"
        + loanidparam
        + "/custominformation"
        + (("/" + customfield) if customfield else "")
    )
    return url


def getusercustominformationurl(iduser, customfield="", *args, **kwargs):
    """Request User Custom Information URL.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    useridparam = "/" + iduser
    url = (
        getmambuurl(*args, **kwargs)
        + "users"
        + useridparam
        + "/custominformation"
        + (("/" + customfield) if customfield else "")
    )
    return url


def getgroupurl(idgroup, *args, **kwargs):
    """Request Groups URL.

    If idgroup is set, you'll get a response adequate for a MambuGroup object.
    If not set, you'll get a response adequate for a MambuGroups object.
    See mambugroup module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * creditOfficerUsername
    * branchId
    * centreId
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: GET compatible

    .. todo:: status API V2: other opers: needs test
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("creditOfficerUsername=%s" % kwargs["creditOfficerUsername"])
        except Exception:
            pass
        try:
            getparams.append("branchId=%s" % kwargs["branchId"])
        except Exception:
            pass
        try:
            getparams.append("centreId=%s" % kwargs["centreId"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
    groupidparam = "" if idgroup == "" else "/" + idgroup
    url = (
        getmambuurl(*args, **kwargs)
        + "groups"
        + groupidparam
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getgrouploansurl(idgroup, *args, **kwargs):
    """Request Group loans URL.

    How to use it? By default MambuLoan uses getloansurl as the urlfunc.
    Override that behaviour by sending getgrouploansurl (this function)
    as the urlfunc to the constructor of MambuLoans (note the final 's')
    and voila! you get the Loans just for a certain group.

    If idgroup is set, you'll get a response adequate for a
    MambuLoans object.

    If not set, you'll get a Jar Jar Binks object, or something quite
    strange and useless as JarJar. A MambuError must likely since I
    haven't needed it for anything but for loans of one and just
    one group.

    See mambugroup module and pydoc for further information.

    Currently implemented filter parameters:
    * accountState

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("accountState=%s" % kwargs["accountState"])
        except Exception:
            pass
    groupidparam = "/" + idgroup
    url = (
        getmambuurl(*args, **kwargs)
        + "groups"
        + groupidparam
        + "/loans"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getgroupcustominformationurl(idgroup, customfield="", *args, **kwargs):
    """Request Group Custom Information URL.

    See mambugroup module and pydoc for further information.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    groupidparam = "/" + idgroup
    url = (
        getmambuurl(*args, **kwargs)
        + "groups"
        + groupidparam
        + "/custominformation"
        + (("/" + customfield) if customfield else "")
    )
    return url


def gettransactionsurl(idcred, *args, **kwargs):
    """Request loan Transactions URL.

    If idcred is set, you'll get a response adequate for a
    MambuTransactions object. There's a MambuTransaction object too, but
    you'll get a list first and each element of it will be automatically
    converted to a MambuTransaction object that you may use.

    If not set, you'll get a Jar Jar Binks object, or something quite
    strange and useless as JarJar. A MambuError must likely since I
    haven't needed it for anything but for transactions of one and just
    one loan account.

    See mambutransaction module and pydoc for further information.

    Currently implemented filter parameters:
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible.
              Repayments/fees/adjustments/disbursements have their own
              endpoint each
    """
    getparams = []
    if kwargs:
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass
    url = (
        getmambuurl(*args, **kwargs)
        + "loans/"
        + idcred
        + "/transactions"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getclienturl(idclient, *args, **kwargs):
    """Request Clients URL.

    If idclient is set, you'll get a response adequate for a MambuClient object.
    If not set, you'll get a response adequate for a MambuClients object.
    See mambuclient module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * firstName
    * lastName
    * idDocument
    * birthdate
    * state
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: GET compatible

    .. todo:: status API V2: other opers: needs test
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("firstName=%s" % kwargs["firstName"])
        except Exception:
            pass
        try:
            getparams.append("lastName=%s" % kwargs["lastName"])
        except Exception:
            pass
        try:
            getparams.append("idDocument=%s" % kwargs["idDocument"])
        except Exception:
            pass
        try:
            getparams.append("birthdate=%s" % kwargs["birthdate"])
        except Exception:
            pass
        try:
            getparams.append("state=%s" % kwargs["state"])
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass
    clientidparam = "" if idclient == "" else "/" + idclient
    url = (
        getmambuurl(*args, **kwargs)
        + "clients"
        + clientidparam
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getclientloansurl(idclient, *args, **kwargs):
    """Request Client loans URL.

    How to use it? By default MambuLoan uses getloansurl as the urlfunc.
    Override that behaviour by sending getclientloansurl (this function)
    as the urlfunc to the constructor of MambuLoans (note the final 's')
    and voila! you get the Loans just for a certain client.

    If idclient is set, you'll get a response adequate for a
    MambuLoans object.

    If not set, you'll get a Jar Jar Binks object, or something quite
    strange and useless as JarJar. A MambuError must likely since I
    haven't needed it for anything but for loans of one and just
    one client.

    See mambuloan module and pydoc for further information.

    Currently implemented filter parameters:
    * accountState

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("accountState=%s" % kwargs["accountState"])
        except Exception:
            pass
    clientidparam = "/" + idclient
    url = (
        getmambuurl(*args, **kwargs)
        + "clients"
        + clientidparam
        + "/loans"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getclientcustominformationurl(idclient, customfield="", *args, **kwargs):
    """Request Client Custom Information URL.

    See mambugroup module and pydoc for further information.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible
    """
    clientidparam = "/" + idclient
    url = (
        getmambuurl(*args, **kwargs)
        + "clients"
        + clientidparam
        + "/custominformation"
        + (("/" + customfield) if customfield else "")
    )
    return url


def getuserurl(iduser, *args, **kwargs):
    """Request Users URL.

    If iduser is set, you'll get a response adequate for a MambuUser object.
    If not set, you'll get a response adequate for a MambuUsers object.
    See mambuuser module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * branchId
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: compatible
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception:
            pass
        try:
            getparams.append("branchId=%s" % kwargs["branchId"])
        except Exception:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass
    useridparam = "" if iduser == "" else "/" + iduser
    url = (
        getmambuurl(*args, **kwargs)
        + "users"
        + useridparam
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getproductsurl(idproduct, *args, **kwargs):
    """Request loan Products URL.

    If idproduct is set, you'll get a response adequate for a MambuProduct object.
    If not set, you'll get a response adequate for a MambuProducts object.
    See mambuproduct module and pydoc for further information.

    No current implemented filter parameters.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible. Current (2020-03) v2 only
              supports GETting a SINGLE product, not all of them
    """
    productidparam = "" if idproduct == "" else "/" + idproduct
    url = getmambuurl(*args, **kwargs) + "loanproducts" + productidparam
    return url


def gettasksurl(dummyId="", *args, **kwargs):
    """Request Tasks URL.

    dummyId is used because MambuStruct always requires an Id from an
    entity, but the Mambu API doesn't requires it for Tasks, because of
    that dummyId defaults to '', but in practice it is never used (if
    someone sends dummyId='someId' nothing happens). The fact of forcing
    to send an entid is a technical debt that should be payed.

    Currently implemented filter parameters:
    * username
    * clientId
    * groupId
    * status
    * limit
    * offset

    Mambu REST API defaults to open when status not provided. Here we
    are just making that explicit always defaulting status to 'OPEN'

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: GET compatible
    """
    getparams = []
    if kwargs:
        try:
            getparams.append("username=%s" % kwargs["username"])
        except Exception:
            pass

        try:
            getparams.append("clientid=%s" % kwargs["clientId"])
        except Exception:
            pass

        try:
            getparams.append("groupid=%s" % kwargs["groupId"])
        except Exception:
            pass

        try:
            getparams.append("status=%s" % kwargs["status"])
        except Exception:
            getparams.append("status=OPEN")

        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception:
            pass

        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "tasks"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getactivitiesurl(dummyId="", *args, **kwargs):
    """Request Activities URL.

    dummyId is used because MambuStruct always requires an Id from an
    entity, but the Mambu API doesn't requires it for Activities,
    because of that dummyId defaults to '', but in practice it is never
    used (if someone sends dummyId='someId' nothing happens). The fact
    of forcing to send an entid is a technical debt that should be
    payed.

    Currently implemented filter parameters:
    * from
    * to
    * branchID
    * clientID
    * centreID
    * userID
    * loanAccountID
    * groupID
    * limit

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.

    .. todo:: status API V2: NOT compatible. Apparently not yet implemented
    """
    from datetime import datetime

    getparams = []
    if kwargs:
        try:
            getparams.append("from=%s" % kwargs["fromDate"])
        except Exception:
            getparams.append("from=%s" % "1900-01-01")

        try:
            getparams.append("to=%s" % kwargs["toDate"])
        except Exception:
            hoy = datetime.now().strftime("%Y-%m-%d")
            getparams.append("to=%s" % hoy)

        try:
            getparams.append("branchID=%s" % kwargs["branchId"])
        except Exception:
            pass

        try:
            getparams.append("clientID=%s" % kwargs["clientId"])
        except Exception:
            pass

        try:
            getparams.append("centreID=%s" % kwargs["centreId"])
        except Exception:
            pass

        try:
            getparams.append("userID=%s" % kwargs["userId"])
        except Exception:
            pass

        try:
            getparams.append("loanAccountID=%s" % kwargs["loanAccountId"])
        except Exception:
            pass

        try:
            getparams.append("groupID=%s" % kwargs["groupId"])
        except Exception:
            pass

        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception:
            pass

    url = (
        getmambuurl(*args, **kwargs)
        + "activities"
        + ("" if len(getparams) == 0 else "?" + "&".join(getparams))
    )
    return url


def getrolesurl(idrole="", *args, **kwargs):
    """Request Roles URL.

    If idrole is set, you'll get a response adequate for a MambuRole
    object.  If not set, you'll get a response adequate for a MambuRoles
    object too.  See mamburoles module and pydoc for further
    information.

    See Mambu official developer documentation for further details.

    .. todo:: status API V2: NOT compatible. Apparently not yet implemented
    """
    url = getmambuurl(*args, **kwargs) + "userroles" + (("/" + idrole) if idrole else "")
    return url


def getpostdocumentsurl(identity="", *args, **kwargs):
    """Request to post documents URL.

    See Mambu official developer documentation for further details.
    https://support.mambu.com/docs/attachments-api

    """
    url = getmambuurl(*args, **kwargs) + "documents"
    return url


### No more urlfuncs from here ###

### More utility functions follow ###
def dateFormat(field, formato=None):
    """Converts a datetime field to a datetime using some specified format.

    What this really means is that, if specified format includes only for
    instance just year and month, day and further info gets ignored and the
    objects get a datetime with year and month, and day 1, hour 0, minute 0,
    etc.

    A useful format may be %Y%m%d, then the datetime objects effectively
    translates into date objects alone, with no relevant time information.

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
        return datetime.strptime(
            datetime.fromisoformat(field).strftime(formato),
            formato,
        )


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
            except TypeError:
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
else:
    # python2
    import urlparse


def iriToUri(iri):
    """Change an IRI (internationalized R) to an URI.

    Used at MambuStruct.connect() method for any requests done to Mambu.

    Perfect example of unicode getting in the way.

    Illustrative (I hope) example: I have Mambu usernames with special
    chars in them. When retrieving them and then trying to build a
    MambuUser object with them, I get a BIG problem because of the
    unicode chars there. Using this I solved the problem.
    """

    def urlEncodeNonAscii(b):
        """Encode Non ASCII chars to URL-friendly chars.

        Sometimes unicode gets in the way. A shame, I know. And perhaps the
        biggest shame is not me correctly handling it.
        """
        import re

        return re.sub("[\x80-\xFF]", lambda c: "%%%02x" % ord(c.group(0)), b)

    parts = urlparse.urlparse(iri)
    if sys.version_info < (3, 0):
        # python2
        partes = []
        for parti, part in enumerate(parts):
            try:
                if parti != 1:
                    partes.append(urlEncodeNonAscii(part.encode("utf-8")))
                else:
                    partes.append(part.encode("idna"))
            except UnicodeDecodeError:
                partes.append(urlEncodeNonAscii(part.decode("latin")))
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
            if sys.version_info < (3, 0):
                v = v.encode("utf8")
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            if sys.version_info < (3, 0):
                v.decode("utf8")
        out_dict[k] = v
    return out_dict


from time import sleep

import requests


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

    * force_download_latest boolean, True to force download even if no
      callback is called. False to throw error if callback isn't received
      after retries.

    * returns a dictionary with info about the download
        -latest     boolean flag, if the db downloaded was the latest or not

    .. todo:: status API V2: compatible
    """
    from datetime import datetime

    try:
        verbose = kwargs["verbose"]
    except KeyError:
        verbose = False
    try:
        retries = kwargs["retries"]
    except KeyError:
        retries = -1
    try:
        force_download_latest = bool(kwargs["force_download_latest"])
    except KeyError:
        force_download_latest = False
    try:
        headers = kwargs["headers"]
    except KeyError:
        headers = {
            "content-type": "application/json",
            "Accept": "application/vnd.mambu.v1+zip",
        }

    if verbose:
        log = open("/tmp/log_mambu_backup", "a")
        log.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - Mambu DB Backup\n")
        log.flush()

    user = kwargs.pop("user", apiuser)
    pwd = kwargs.pop("pwd", apipwd)
    data = {"callback": callback}
    try:
        posturl = iriToUri(getmambuurl(*args, **kwargs) + "database/backup")
        if verbose:
            log.write("open url: " + posturl + "\n")
            log.flush()
        resp = requests.post(
            posturl,
            data=data,
            headers={
                "content-type": "application/json",
                "Accept": "application/vnd.mambu.v1+json",
            },
            auth=(user, pwd),
        )
    except Exception as ex:
        mess = "Error requesting backup: %s" % repr(ex)
        if verbose:
            log.write(mess + "\n")
            log.close()
        raise MambuError(mess)

    if resp.status_code != 200:
        mess = "Error posting request for backup: %s" % resp.content
        if verbose:
            log.write(mess + "\n")
            log.close()
        raise MambuCommError(mess)

    data["latest"] = True
    while retries and not bool_func():
        if verbose:
            log.write("waiting...\n")
            log.flush()
        sleep(10)
        retries -= 1
        if retries < 0:
            retries = -1
    if not retries:
        mess = "Tired of waiting, giving up..."
        if verbose:
            log.write(mess + "\n")
            log.flush()
        if not force_download_latest:
            if verbose:
                log.close()
            raise MambuError(mess)
        else:
            data["latest"] = False
    sleep(30)

    geturl = iriToUri(getmambuurl(*args, **kwargs) + "database/backup/LATEST")
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

    if verbose:
        log.write("saving...\n")
        log.flush()
    with open(output_fname, "wb") as fw:
        fw.write(resp.content)

    if verbose:
        log.write("DONE!\n")
        log.close()

    return data
