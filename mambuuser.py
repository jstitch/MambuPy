from mambustruct import MambuStruct, MambuStructIterator
from podemos import PodemosError, getuserurl, DEBUG, ERROR_CODES
from datetime import datetime
from util import strip_consecutive_repeated_char

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

urlfunc = getuserurl

# Objeto con una lista de Usuarios Mambu
class MambuUsers(MambuStruct):
    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def __len__(self):
        return len(self.attrs)

    def convertDict2Attrs(self):
        for u in self.attrs:
            user = MambuUser(urlfunc=None, entid=None)
            user.init(u)
            u = user

class MambuUser(MambuStruct):
    # Preprocesamiento
    def preprocess(self):
        try:
            self.attrs['firstName'] = self.attrs['firstName'].strip()
        except Exception as e:
            self.attrs['firstName'] = ""
        try:
            self.attrs['lastName'] = self.attrs['lastName'].strip()
        except Exception as ex:
            self.attrs['lastName'] = ""

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:

            try:
                self.attrs['lastLoggedInDate'] = datetime.strptime(self.attrs['lastLoggedInDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['creationDate'] = datetime.strptime(self.attrs['creationDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['lastModifiedDate'] = datetime.strptime(self.attrs['lastModifiedDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
