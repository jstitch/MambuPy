from podemos import PodemosError, MambuCommError, API_RETURN_CODES, DEBUG, ERROR_CODES
from urllib import urlopen
import json, copy

class MambuStruct(object):
    # Initializa a partir de un diccionario con los elementos de la cuenta
    def __init__(self, attrs={}):
        self.attrs = attrs
        self.convertDict2Attrs()

    # Inicializa a partir de un ID de cuenta, que se obtiene contactando a Mambu
    def __init__(self, urlfunc, entid, *args, **kwargs):
        self.urlfunc = urlfunc
        jsresp = {}

        try:
            resp = urlopen(self.urlfunc(entid, *args, **kwargs))
        except Exception as ex:
            print repr(ex)
            raise MambuCommError(ERROR_CODES["MAMBU_COMM_ERROR"])
        else:
            try:
                jsresp = json.load(resp,"latin-1")
                # if DEBUG:
                #     import pprint
                #     pprint.pprint(jsresp)
            except Exception as ex:
                raise PodemosError("JSON Error: %s" % repr(ex))
            try:
                if ((jsresp[u'returnCode'] == API_RETURN_CODES["INVALID_LOAN_ACCOUNT_ID"]) and
                    (jsresp[u'returnStatus'] == u'INVALID_LOAN_ACCOUNT_ID')):

                    raise PodemosError(ERROR_CODES["ACCOUNT_NOT_FOUND"])
            except (KeyError, TypeError) as err:
                pass

        self.attrs = jsresp
        self.preprocess()
        self.serial = copy.deepcopy(self.attrs)
        self.convertDict2Attrs()

    def preprocess(self):
        pass

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        pass
