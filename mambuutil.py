from mambuconfig import apiurl
from mambuconfig import apiuser
from mambuconfig import apipwd

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

class MambuError(Exception):
    pass

class MambuCommError(MambuError):
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
    groupidparam = "" if idgroup == "" else "/"+idgroup
    url = getmambuurl(*args,**kwargs) + "groups" + groupidparam + ( "" if len(getparams) == 0 else "?" + "&".join(getparams) )
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
        try:
            getparams.append("state=%s" % kwargs["state"])
        except Exception as ex:
            pass
        try:
            getparams.append("limit=%s" % kwargs["limit"])
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

# Retorna URL para api de Mambu, productos
def getproductsurl(idproduct, *args, **kwargs):
    productidparam = "" if idproduct == "" else "/"+idproduct
    url = getmambuurl(*args,**kwargs) + "loanproducts" + productidparam
    return url

# Retorna URL para api de Mambu, tasks
def gettasksurl(*args, **kwargs):
    url = getmambuurl() + "tasks"
    return url

from HTMLParser import HTMLParser
# Aux class for stripping HTML tags
class MLStripper(HTMLParser):
   def __init__(self):
      self.reset()
      self.fed = []
   def handle_data(self, d):
      self.fed.append(d)
   def get_data(self):
      return ''.join(self.fed)

# Stripts HTML tags from text
def strip_tags(html):
    s = MLStripper()
    s.feed(html.replace("&nbsp;"," "))
    return s.get_data()

# Strip characters in a string which are consecutively repeated
def strip_consecutive_repeated_char(s, ch, circ=True):
   sdest = ""
   for i,c in enumerate(s):
      if s[i] == ch and s[i] == s[i-1]:
         continue
      sdest += s[i]
   return sdest
