from .mambuconfig import apiurl

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

def _get_parameters_url(dict_kwargs):
    """Get list with parameters for the url of getbranchesurl, getloansurl, getgroupurl, getclienturl,
    getactivitiesurl, getcentresurl, getrepaymentsurl, getsavingssurl, getsavingfundingrepaymentsurl,
    getsavingstransactionsurl, getsavingstransactionssearchurl, gettransactionchannelsurl, getgrouploansurl,
    gettransactionsurl, getclientloansurl, getuserurl, gettasksurl.
    """
    getparams_list = []

    for key in dict_kwargs.keys():
        if key == "fullDetails":
            if dict_kwargs[key] is True:
                getparams_list.append("fullDetails=true")
            else:
                getparams_list.append("fullDetails=false")
        elif key in ["user", "pwd"]:
            continue
        elif key in ["version"]:
            continue
        else:
            getparams_list.append(key + '=%s' % dict_kwargs[key])

    return getparams_list


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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

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
        getparams = _get_parameters_url(kwargs)

    groupIdparam = "" if idgroup == "" else "/" + idgroup

    url = (
        getmambuurl(*args, **kwargs)
        + "groups"
        + groupIdparam
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
        getparams = _get_parameters_url(kwargs)

    groupIdparam = "/" + idgroup
    url = (
        getmambuurl(*args, **kwargs)
        + "groups"
        + groupIdparam
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
    groupIdparam = "/" + idgroup
    url = (
        getmambuurl(*args, **kwargs)
        + "groups"
        + groupIdparam
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
        getparams = _get_parameters_url(kwargs)
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
        getparams = _get_parameters_url(kwargs)

    clientIdparam = "" if idclient == "" else "/" + idclient
    url = (
        getmambuurl(*args, **kwargs)
        + "clients"
        + clientIdparam
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
        getparams = _get_parameters_url(kwargs)

    clientIdparam = "/" + idclient
    url = (
        getmambuurl(*args, **kwargs)
        + "clients"
        + clientIdparam
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
    clientIdparam = "/" + idclient
    url = (
        getmambuurl(*args, **kwargs)
        + "clients"
        + clientIdparam
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
        getparams = _get_parameters_url(kwargs)

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
            getparams.append("status=%s" % kwargs["status"])
            del kwargs["status"]
        except Exception:
            getparams.append("status=OPEN")
        getparams.extend(_get_parameters_url(kwargs))

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
    * clientId
    * centreID
    * userID
    * loanAccountId
    * groupId
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
            del kwargs["fromDate"]
        except Exception:
            getparams.append("from=%s" % "1900-01-01")

        try:
            getparams.append("to=%s" % kwargs["toDate"])
            del kwargs["toDate"]
        except Exception:
            hoy = datetime.now().strftime("%Y-%m-%d")
            getparams.append("to=%s" % hoy)

        getparams.extend(_get_parameters_url(kwargs))

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
