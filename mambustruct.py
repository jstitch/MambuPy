# coding: utf-8

from mambuutil import API_RETURN_CODES, MambuCommError, MambuError

from urllib import urlopen, urlencode
import json, copy
from datetime import datetime
from time import sleep

import logging

def setup_logging(default_path='mambulogging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    import os, logging.config, yaml
    from codecs import open as copen
    path = default_path
    value = os.getenv(env_key,None)
    if value:
        path = value
    if os.path.exists(path):
        with copen(path, 'rt', 'utf-8') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    
logger = logging.getLogger(__name__)

# Singleton para contar requests
class RequestsCounter(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(RequestsCounter, cls).__new__(cls, *args, **kwargs)
            cls.requests = []
            cls.cnt = 0
        return cls.__instance
    def add(cls, temp):
        cls.requests.append(temp)
        cls.cnt += 1
    def reset(cls):
        cls.cnt = 0
        cls.requests = []


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
    setup_logging()
    RETRIES = 5
    
    # Serializa data, y si es iterable serializa sus miembros
    # (y si es MambuStruct, serializa su diccionario attrs)
    @staticmethod
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

    def __len__(self):
        return len(self.attrs)

    def __eq__(self, other):
        if isinstance(other, MambuStruct):
            try:
                if not other.attrs.has_key('encodedKey') or not self.attrs.has_key('encodedKey'):
                    return NotImplemented
            except AttributeError:
                return NotImplemented
            return other['encodedKey'] == self['encodedKey']

    # TODO: throw exception when not a dict
    def has_key(self, key):
        return self.attrs.has_key(key)

    # TODO: throw exception when not a dict
    def items(self):
        return self.attrs.items()

    # Initializa a partir de un diccionario con los elementos de la cuenta
    def init(self, attrs={}, *args, **kwargs):
        self.attrs = attrs
        self.preprocess()
        self.convertDict2Attrs(*args, **kwargs)
        self.postprocess()
    
    # "Serializa" la informacion de cada campo en el diccionario
    # NO SERIALIZA LA CLASE, solo sus campos
    # WARNING: puede caer en stackoverflow, verificar niveles de
    # recursion...
    def serializeStruct(self):
        serial = MambuStruct.serializeFields(self.attrs)
        return serial

    # Inicializa a partir de un ID de la entidad
    def __init__(self, urlfunc, entid='', *args, **kwargs):
        self.entid = entid
        self.rc = RequestsCounter()
        try:
            self.__debug=kwargs['debug']
        except KeyError:
            self.__debug=False
        try:
            self.__formatoFecha=kwargs['dateFormat']
        except KeyError:
            self.__formatoFecha="%Y-%m-%dT%H:%M:%S+0000"
        try:
            self.__data=kwargs['data']
        except KeyError:
            self.__data=None
            
        if urlfunc == None: # Only used when GET returns an array, meaning the MambuStruct must be a list of MambuStucts
            return          # and each element is init without further configs

        try:
            if kwargs.pop('connect'):
                connect = True
            else:
                connect = False
        except KeyError:
            connect = True

        self.__urlfunc = urlfunc

        if connect:
            self.connect(*args, **kwargs)

    # Conectarse con Mambu
    def connect(self, *args, **kwargs):
        jsresp = {}

        retries = 0
        while retries < MambuStruct.RETRIES:
            try:
                if self.__data:
                    resp = urlopen(self.__urlfunc(self.entid, *args, **kwargs), urlencode(self.__data))
                else:
                    resp = urlopen(self.__urlfunc(self.entid, *args, **kwargs))
                self.rc.add(datetime.now())
                try:
                    jsresp = json.load(resp)
                except ValueError as ex:
                    raise ex
                except Exception as ex:
                    raise MambuError("JSON Error: %s" % repr(ex))
                break
            except MambuError as merr:
                raise merr
            except Exception as ex:
                retries += 1
        else:
            raise MambuCommError("ERROR I can't communicate with Mambu")

        try:
            if jsresp.has_key(u'returnCode') and jsresp.has_key(u'returnStatus'):
                raise MambuError(jsresp[u'returnStatus'])
        except AttributeError:
            pass

        self.init(attrs=jsresp, *args, **kwargs)

    # Cada implementacion de MambuStruct puede masajear la informacion
    # salida de Mambu a un formato/estilo mas adecuado
    def preprocess(self):
        pass

    # Cada implementacion de MambuStruct puede masajear la informacion
    # convertida aqui, a un formato/estilo mas adecuado
    def postprocess(self):
        pass

    # De un diccionario de valores como cadenas, convierte los
    # pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        constantFields = ['id', 'homePhone', 'mobilePhone1', 'phoneNumber', 'postcode']
        def convierte(data):
            try:
                it = iter(data)
                if type(it) == type(iter({})):
                    d = {}
                    for k in it:
                        if k in constantFields:
                            d[k] = data[k]
                        else:
                            d[k] = convierte(data[k])
                    data = d
                if type(it) == type(iter([])):
                    l = []
                    for e in it:
                        l.append(convierte(e))
                    data = l
            except TypeError as terr:
                pass
            except Exception as ex:
                raise ex
            
            try:
                d = int(data)
                if str(d) != data: # por si la cadena tiene 0's al inicio, para no perderlos
                    return data
                return d
            except (TypeError, ValueError) as tverr:
                try:
                    return float(data)
                except (TypeError, ValueError) as tverr:
                    try:
                        return self.util_dateFormat(data)
                    except (TypeError, ValueError) as tverr:
                        return data
            
            return data

        self.attrs = convierte(self.attrs)

    # Convierte campo de fecha a formato especificado a partir de
    # formato default de Mambu
    def util_dateFormat(self, field, formato=None):
        if not formato:
            try:
                formato = self.__formatoFecha
            except AttributeError:
                formato = "%Y-%m-%dT%H:%M:%S+0000"
        return datetime.strptime(datetime.strptime(field, "%Y-%m-%dT%H:%M:%S+0000").strftime(formato), formato)
