# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getuserurl

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

class MambuUser(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        self.customFieldName = 'customFields'
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    # Preprocesamiento
    def preprocess(self):
        if self.has_key(self.customFieldName):
            for custom in self[self.customFieldName]:
                custom['name'] = custom['customField']['name']
                self[custom['name']] = custom['value']
        for k,v in self.items():
            try:
                self[k] = v.strip()
            except Exception:
                pass

        try:
            self['firstName'] = self['firstName'].strip()
        except Exception as e:
            self['firstName'] = ""
        try:
            self['lastName'] = self['lastName'].strip()
        except Exception as ex:
            self['lastName'] = ""

        self['name'] = self['firstName'] + " " + self['lastName']

# Objeto con una lista de Usuarios Mambu
class MambuUsers(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

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
