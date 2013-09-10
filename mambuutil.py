from config import apiurl
from priv_data import apiuser
from priv_data import apipwd

class MambuError(Exception):
    pass

# Retorna URL para api de Mambu con datos de acceso
def getmambuurl(user=apiuser, pwd=apipwd, url=apiurl, *args, **kwargs):
    mambuurl = "https://" + user + ":" + pwd + "@" + url + "/api/"
    return mambuurl

# Retorna URL para api de Mambu, branches
def getbranchesurl(idbranch, *args, **kwargs):
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

# Retorna URL para api de Mambu, repayments
def getrepaymentsurl(idcred, *args, **kwargs):
    url = getmambuurl(*args,**kwargs) + "loans/" + idcred + "/repayments"
    return url

# Retorna URL para api de Mambu, loans
def getloansurl(idcred, *args, **kwargs):
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

# Retorna URL para api de Mambu, grupos
def getgroupurl(idgroup, *args, **kwargs):
    url = getmambuurl(*args,**kwargs) + "groups/" + idgroup + ("" if not kwargs or kwargs['fullDetails']==False else "?fullDetails=true")
    return url

# Retorna URL para api de Mambu, cuentas de un grupo
def getgrouploansurl(idgroup, *args, **kwargs):
    getparams = []
    if kwargs:
        try:
            getparams.append("accountState=%s" % kwargs["accountState"])
        except Exception as ex:
            pass
    groupidparam = "/" + idgroup
    url = getmambuurl(*args,**kwargs) + "groups" + groupidparam  + "/loans" + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
    return url

# Retorna URL para api de Mambu, transacciones
def gettransactionsurl(idcred, *args, **kwargs):
    getparams = []
    if kwargs:
        try:
            getparams.append("offset=%s" % kwargs["offset"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
        except Exception as ex:
            getparams.append("limit=499")
    url = getmambuurl(*args,**kwargs) + "loans/" + idcred + "/transactions" + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
    return url

# Retorna URL para api de Mambu, cliente
def getclienturl(idclient, *args, **kwargs):
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
    clientidparam = "" if idclient == "" else "/"+idclient
    url = getmambuurl(*args,**kwargs) + "clients" + clientidparam + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
    return url

# Retorna URL para api de Mambu, usuario
def getuserurl(iduser, *args, **kwargs):
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

# Retorna URL para api de Mambu, tasks
def gettasksurl(*args, **kwargs):
    url = getmambuurl() + "tasks"
    return url
