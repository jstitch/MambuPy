# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from podemos import PodemosError, getbranchesurl, DEBUG, ERROR_CODES
from util import strip_consecutive_repeated_char as strip_cons
from datetime import datetime
from products import products
import re

# [
#   {
#     "encodedKey": "8a70db342e6d595a012e6e7158670f9d",
#     "id": "1",
#     "creationDate": "2011-02-28T22:44:05+0000",
#     "lastModifiedDate": "2011-02-28T22:44:05+0000",
#     "name": "Nicolas Romero"
#     "phoneNumber": "12345678",
#     "emailAddress": "a@b.com"
#   }
# ]

urlfunc = getbranchesurl

# Objeto con una lista de Branches Mambu
class MambuBranches(MambuStruct):
    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def __len__(self):
        return len(self.attrs)

    def convertDict2Attrs(self):
        for b in self.attrs:
            branch = MambuBranch(urlfunc=None, entid=None)
            branch.init(b)
            b = branch

# Objeto con una Branch desde Mambu
class MambuBranch(MambuStruct):
    # Preprocesamiento
    def preprocess(self):
        pass

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:
            self.attrs['creationDate'] = datetime.strptime(self.attrs['creationDate'], "%Y-%m-%dT%H:%M:%S+0000")
            self.attrs['lastModifiedDate'] = datetime.strptime(self.attrs['lastModifiedDate'], "%Y-%m-%dT%H:%M:%S+0000")
        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
