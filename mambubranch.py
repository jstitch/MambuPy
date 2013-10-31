# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getbranchesurl

from util import strip_consecutive_repeated_char as strip_cons

# [
#  {
#   "id": "1",
#   "name": "Nicolas Romero",
#   "phoneNumber": "16605508",
#   "emailAddress": "d.jimenez@podemos.mx",
#   "branchHolidays": [],
#   "encodedKey": "8a70db342e6d595a012e6e7158670f9d",
#   "address": {
#     "line1": "Niños Heroes #15",
#     "line2": "Miguel Hidalgo",
#     "city": "Nicolas Romero",
#     "region": "Mexico",
#     "postcode": "54400",
#     "country": "Mexico",
#     "indexInList": -1
#     "encodedKey": "8a6a80593fc305e1013fc47ad052686b",
#     "parentKey": "8a70db342e6d595a012e6e7158670f9d",
#   },
#   "customFieldValues": []
#   "creationDate": "2011-02-28T22:44:05+0000",
#   "lastModifiedDate": "2013-07-09T17:36:27+0000",
#  },
# ]

mod_urlfunc = getbranchesurl

# Objeto con una Branch desde Mambu
class MambuBranch(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    # Preprocesamiento
    def preprocess(self):
        if self.has_key('customFieldValues'):
            for custom in self['customFieldValues']:
                custom['name'] = custom['customField']['name']
                self[custom['name']] = custom['value']

    # Anexa los usuarios activos de esa sucursal
    # Retorna numero de requests hechos
    def setUsers(self, *args, **kwargs):
        from mambuuser import MambuUsers
        usrs = [ us for us in MambuUsers(branchId=self['id'], *args, **kwargs) if us['userState'] == "ACTIVE" ]
        self['users'] = usrs

        return 1

# Objeto con una lista de Branches Mambu
class MambuBranches(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convertDict2Attrs(self, *args, **kwargs):
        for n,b in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            branch = MambuBranch(urlfunc=None, entid=None, *args, **kwargs)
            branch.init(b, *args, **kwargs)
            self.attrs[n] = branch
