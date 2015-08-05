"""Mambu utilites module.

Exceptions, some API return codes, utility functions, a lot of urlfuncs
(see MambuStruct.__init__ and .connect pydocs for more info on this)

Secutiry WARNING: Imports the configurations from mambuconfig. It surely
is a bad idea. Got to improve this!
"""

from mambuconfig import apiurl
from mambuconfig import apiuser
from mambuconfig import apipwd

from mambuconfig import dbname
from mambuconfig import dbuser
from mambuconfig import dbpwd
from mambuconfig import dbhost
from mambuconfig import dbport
from mambuconfig import dbeng


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
"""DEPRECATE this one, it's probably not useful. Besides,

MambuStruct.connect() method returns the code when an error occurs by
default.
"""


OUT_OF_BOUNDS_PAGINATION_LIMIT_VALUE = 500
"""Current maximum number of response elements Mambu returns"""


class MambuError(Exception):
    """Default exception"""
    pass

class MambuCommError(MambuError):
    """Thrown when communication issues with Mambu arise"""
    pass


# Connects to DB
def connectDb(engine   = dbeng,
              user     = dbuser,
              password = dbpwd,
              host     = dbhost,
              port     = dbport,
              database = dbname,
              echoopt  = False):
    """Connect to database utility function.

    Uses SQLAlchemy ORM library.

    Useful when using schema modules in MambuPy
    """
    from sqlalchemy import create_engine
    return create_engine('%s://%s:%s@%s:%s/%s' % (engine, user, password, host, port, database), echo=echoopt)


def getmambuurl(user=apiuser, pwd=apipwd, url=apiurl, *args, **kwargs):
    """Basic Mambu URL function. Builds the Mambu basic request string.

    Receives a user, password and url arguments to connect to Mambu.
    Defaults to what mambuconfig has, but you may override it by sending
    'user', 'pwd' and 'url' parameters at the Mambu object instantiation
    (for instance: MambuLoan(user=myuser, pwd=mypwd, url=myurl,
    entid='12345', ...)
    """
    mambuurl = "https://" + user + ":" + pwd + "@" + url + "/api/"
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
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception as ex:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            pass

    branchidparam = "" if idbranch == "" else "/"+idbranch
    url = getmambuurl(*args, **kwargs) + "branches" + branchidparam + ("" if len(getparams) == 0 else "?" + "&".join(getparams) )
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

    No current implemented filter parameters.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    url = getmambuurl(*args,**kwargs) + "loans/" + idcred + "/repayments"
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
    * creditOfficerUsername
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception as ex:
            pass
        try:
            getparams.append("accountState=%s" % kwargs["accountState"])
        except Exception as ex:
            pass
        try:
            getparams.append("branchId=%s" % kwargs["branchId"])
        except Exception as ex:
            pass
        try:
            getparams.append("creditOfficerUsername=%s" % kwargs["creditOfficerUsername"])
        except Exception as ex:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            pass

    idcredparam = "" if idcred == "" else "/"+idcred
    url = getmambuurl(*args,**kwargs) + "loans" + idcredparam + ("" if len(getparams) == 0 else "?" + "&".join(getparams) )
    return url

def getgroupurl(idgroup, *args, **kwargs):
    """Request Groups URL.

    If idgroup is set, you'll get a response adequate for a MambuGroup object.
    If not set, you'll get a response adequate for a MambuGroups object.
    See mambugroup module and pydoc for further information.

    Currently implemented filter parameters:
    * fullDetails
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
    groupidparam = "" if idgroup == "" else "/"+idgroup
    url = getmambuurl(*args,**kwargs) + "groups" + groupidparam + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
    return url

def getgrouploansurl(idgroup, *args, **kwargs):
    """Request loan Repayments URL.

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

    See mambuloan module and pydoc for further information.

    Currently implemented filter parameters:
    * accountState

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    getparams = []
    if kwargs:
        try:
            getparams.append("accountState=%s" % kwargs["accountState"])
        except Exception as ex:
            pass
    groupidparam = "/" + idgroup
    url = getmambuurl(*args,**kwargs) + "groups" + groupidparam  + "/loans" + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
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
    """
    getparams = []
    if kwargs:
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            pass
    url = getmambuurl(*args,**kwargs) + "loans/" + idcred + "/transactions" + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
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
    * documentId
    * birthdate
    * state
    * limit
    * offset

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception as ex:
            pass
        try:
            getparams.append("firstName=%s" % kwargs["firstName"])
        except Exception as ex:
            pass
        try:
            getparams.append("lastName=%s" % kwargs["lastName"])
        except Exception as ex:
            pass
        try:
            getparams.append("documentId=%s" % kwargs["documentId"])
        except Exception as ex:
            pass
        try:
            getparams.append("birthdate=%s" % kwargs["birthdate"])
        except Exception as ex:
            pass
        try:
            getparams.append("state=%s" % kwargs["state"])
        except Exception as ex:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            pass
    clientidparam = "" if idclient == "" else "/"+idclient
    url = getmambuurl(*args,**kwargs) + "clients" + clientidparam + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
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
    """
    getparams = []
    if kwargs:
        try:
            if kwargs["fullDetails"] == True:
                getparams.append("fullDetails=true")
            else:
                getparams.append("fullDetails=false")
        except Exception as ex:
            pass
        try:
            getparams.append("branchId=%s" % kwargs["branchId"])
        except Exception as ex:
            pass
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            pass
    useridparam = "" if iduser == "" else "/"+iduser
    url = getmambuurl(*args,**kwargs) + "users" + useridparam + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
    return url

def getproductsurl(idproduct, *args, **kwargs):
    """Request loan Products URL.

    If idproduct is set, you'll get a response adequate for a MambuProduct object.
    If not set, you'll get a response adequate for a MambuProducts object.
    See mambuproduct module and pydoc for further information.

    No current implemented filter parameters.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    productidparam = "" if idproduct == "" else "/"+idproduct
    url = getmambuurl(*args,**kwargs) + "loanproducts" + productidparam
    return url

def gettasksurl(*args, **kwargs):
    """Request Tasks URL.

    TODO: a MambuTask object to implement this. Currently you'll need to
    implement a urllib.urlopen call to use something like this. Not good!

    No current implemented filter parameters.

    See Mambu official developer documentation for further details, and
    info on parameters that may be implemented here in the future.
    """
    url = getmambuurl(*args, **kwargs) + "tasks"
    return url

### No more urlfuncs from here ###

### More utility functions follow ###
from HTMLParser import HTMLParser
class MLStripper(HTMLParser):
    """Aux class for stripping HTML tags.

    Note fields on several Mambu entities come with additional HTML tags
    (they are rich text fields, I guess that's why). Sometimes they are
    useless, so stripping them is a good idea.
    """
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    """Stripts HTML tags from text.

    Note fields on several Mambu entities come with additional HTML tags
    (they are rich text fields, I guess that's why). Sometimes they are
    useless, so stripping them is a good idea.
    """
    s = MLStripper()
    s.feed(html.replace("&nbsp;"," "))
    return s.get_data()


def strip_consecutive_repeated_char(s, ch, circ=True):
    """Strip characters in a string which are consecutively repeated.

    Useful when in notes or some other free text fields on Mambu, users
    capture anything and a lot of capture errors not always detected by
    Mambu get through. You want some cleaning? this may be useful.

    This is a string processing function.
    """
    sdest = ""
    for i,c in enumerate(s):
        if s[i] == ch and s[i] == s[i-1]:
            continue
        sdest += s[i]
    return sdest


def urlEncodeNonAscii(b):
    """Encode Non ASCII chars to URL-friendly chars.

    Sometimes unicode gets in the way. A shame, I know. And perhaps the
    biggest shame is not me correctly handling it.
    """
    import re
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    """Change an IRI (internationalized R) to an URI.

    Used at MambuStruct.connect() method for any requests done to Mambu.

    Perfect example of unicode getting in the way.

    Illustrative (I hope) example: I have Mambu usernames with special
    chars in them. When retrieving them and then trying to build a
    MambuUser object with them, I get a BIG problem because of the
    unicode chars there. Using this I solved the problem.
    """
    import urlparse
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


def encoded_dict(in_dict):
    """Encode every value of a dict to UTF-8.

    Useful for POSTing requests on the 'data' parameter of urlencode.
    """
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict
