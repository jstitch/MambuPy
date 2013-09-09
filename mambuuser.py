# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getuserurl
from podemos import PodemosError, ERROR_CODES
from datetime import datetime

# {
#   "id": 51,
#   "username": "i.martinez",
#   "email": "i.martinez@podemos.mx",
#   "userState": "ACTIVE",

#   "firstName": "Ilya ",
#   "lastName": "Martinez",
#   "title": "Coordinador de Emprendedoras",
#   "homePhone": "58288424",
#   "mobilePhone1": "(044)5559951342",
#   "notes": ""

#   "language": "SPANISH",
#   "twoFactorAuthentication": false,
#   "isAdministrator": false,
#   "isCreditOfficer": true,
#   "accessRights": [
#     "MAMBU",
#     "MOBILE"
#   ],

#   "lastLoggedInDate": "2012-12-19T20:31:07+0000",

#   "creationDate": "2011-08-25T19:23:54+0000",
#   "lastModifiedDate": "2012-12-19T20:31:07+0000",

#   "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
#   "encodedKey": "8ad807b031f6305b01320266094b4948",

# }

mod_urlfunc = getuserurl

# Objeto con una lista de Usuarios Mambu
class MambuUsers(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def __len__(self):
        return len(self.attrs)

    def convertDict2Attrs(self, *args, **kwargs):
        for n,u in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            user = MambuUser(urlfunc=None, entid=None, *args, **kwargs)
            user.init(u, *args, **kwargs)
            self.attrs[n] = user

class MambuUser(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    # Preprocesamiento
    def preprocess(self):
        if self.attrs.has_key('customFields'):
            for custom in self.attrs['customFields']:
                custom['name'] = custom['customField']['name']
        for k,v in self.attrs.items():
            try:
                self.attrs[k] = v.strip()
            except Exception:
                pass

        try:
            self.attrs['firstName'] = self.attrs['firstName'].strip()
        except Exception as e:
            self.attrs['firstName'] = ""
        try:
            self.attrs['lastName'] = self.attrs['lastName'].strip()
        except Exception as ex:
            self.attrs['lastName'] = ""

        self.attrs['name'] = self.attrs['firstName'] + " " + self.attrs['lastName']

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        try:
            try:
                self.attrs['lastLoggedInDate'] = self.util_dateFormat(self.attrs['lastLoggedInDate'])
            except KeyError as kerr:
                pass
            try:
                self.attrs['creationDate'] = self.util_dateFormat(self.attrs['creationDate'])
            except KeyError as kerr:
                pass
            try:
                self.attrs['lastModifiedDate'] = self.util_dateFormat(self.attrs['lastModifiedDate'])
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
