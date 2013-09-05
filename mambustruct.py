# coding: utf-8

from podemos import PodemosError, MambuCommError, API_RETURN_CODES, DEBUG, ERROR_CODES
from urllib import urlopen
import json, copy
from datetime import datetime

# Singleton para contar requests
class RequestsCounter(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(RequestsCounter, cls).__new__(cls, *args, **kwargs)
            cls.requests = 0
        return cls.__instance

# Habilita iteracion sobre estructuras Mambu
class MambuStructIterator:
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.offset = 0

    def next(self):
        if self.offset >= len(self.wrapped):
            raise StopIteration
        else:
            item = self.wrapped[self.offset]
            self.offset += 1
            return item

# Clase padre de todas las estructuras Mambu. Dictionary-like
# Contienen un atributo, dict attrs
class MambuStruct(object):
    RETRIES = 5
    
    # Serializa data, y si es iterable serializa sus miembros
    # (y si es MambuStruct, serializa su diccionario attrs)
    def serializeFields(data):
        if isinstance(data, MambuStruct):
            return data.serializeStruct()
        try:
            it = iter(data)
        except TypeError as terr:
            return unicode(data)
        if type(it) == type(iter([])):
            l = []
            for e in it:
                l.append(MambuStruct.serializeFields(e))
            return l
        elif type(it) == type(iter({})):
            d = {}
            for k in it:
                d[k] = MambuStruct.serializeFields(data[k])
            return d
        # elif ... tuples? sets?
        return unicode(data)
    serializeFields = staticmethod(serializeFields)

    def __getitem__(self, key):
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __repr__(self):
        try:
            return self.__class__.__name__ + " - id: %s" % self.attrs['id']
        except TypeError:
            return self.__class__.__name__ + " - len: %s" % len(self.attrs)

    def __str__(self):
        return self.__class__.__name__ + " - " + str(self.attrs)

    # Initializa a partir de un diccionario con los elementos de la cuenta
    def init(self, attrs={}, *args, **kwargs):
        self.attrs = attrs
        self.preprocess()
        self.serial = copy.deepcopy(self.attrs)
        self.convertDict2Attrs(*args, **kwargs)
    
    # "Serializa" la informacion de cada campo en el diccionario
    # NO SERIALIZA LA CLASE, solo sus campos
    def serializeStruct(self):
        serial = MambuStruct.serializeFields(self.attrs)
        return serial

    # Inicializa a partir de un ID de cuenta, que se obtiene contactando a Mambu
    def __init__(self, urlfunc, entid='', *args, **kwargs):
        if urlfunc == None:
            return

        self.rc = RequestsCounter()
        self.__urlfunc = urlfunc
        try:
            self.__formatoFecha=kwargs['dateFormat']
        except KeyError:
            self.__formatoFecha="%Y-%m-%dT%H:%M:%S+0000"

        jsresp = {}

        retries = 0
        while retries < MambuStruct.RETRIES:
            try:
                resp = urlopen(self.__urlfunc(entid, *args, **kwargs))
                self.rc.requests += 1
                break
            except Exception as ex:
                retries += 1
                if DEBUG: print "commerror!%s" % (" retrying" if retries < MambuStruct.RETRIES else "",)
                # print repr(ex)
        else:
            raise MambuCommError(ERROR_CODES["MAMBU_COMM_ERROR"])

        try:
            # jsresp = json.load(resp,"latin-1")
            jsresp = json.load(resp)
            # if DEBUG:
            #     import pprint
            #     pprint.pprint(jsresp)
        except Exception as ex:
            raise PodemosError("JSON Error: %s" % repr(ex))
        try:
            if ((jsresp[u'returnCode'] == API_RETURN_CODES["INVALID_LOAN_ACCOUNT_ID"]) and
                (jsresp[u'returnStatus'] == u'INVALID_LOAN_ACCOUNT_ID')):

                raise PodemosError(ERROR_CODES["ACCOUNT_NOT_FOUND"])
                
            elif (jsresp[u'returnCode'] == API_RETURN_CODES["INVALID_ACCOUNT_STATE"]):
                  raise PodemosError("Invalid Account State!!")

        except (KeyError, TypeError) as err:
            pass

        self.init(attrs=jsresp, *args, **kwargs)

    # Cada implmentacion de MambuStruct puede masajear la informacion
    # salida de Mambu a un formato/estilo mas adecuado
    def preprocess(self):
        pass

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        pass

    # Convierte campo de fecha a formato especificado a partir de formato default de Mambu
    def util_dateFormat(self, field, formato=None):
        if not formato:
            try:
                formato = self.__formatoFecha
            except AttributeError:
                formato = "%Y-%m-%dT%H:%M:%S+0000"
        return datetime.strptime(datetime.strptime(field, "%Y-%m-%dT%H:%M:%S+0000").strftime(formato), formato)
