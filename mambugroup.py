# coding: utf-8

from mambustruct import MambuStruct
from mambuutil import getgroupurl

from datetime import datetime

# {
#  "groupMembers": [
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2af0229",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "indexInList": 0,
#    "creationDate": "2012-07-04T22:35:03+0000",
#    "clientKey": "8a101aa637fd34cc013816274ec902d9"
#   },
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b1022a",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "indexInList": 1,
#    "creationDate": "2012-07-04T22:35:03+0000",
#    "clientKey": "8a43a79f3664edaa013733547d156af5"
#   },
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b1022b",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "indexInList": 2,
#    "creationDate": "2012-07-04T22:35:03+0000",
#    "clientKey": "8a101aa637fd34cc0137ffdc3692006b"
#   },
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b1022c",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "indexInList": 3,
#    "creationDate": "2012-07-04T22:35:03+0000",
#    "clientKey": "8a5c291d33563d0501335ad699960783"
#   },
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b1022d",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "indexInList": 4,
#    "creationDate": "2012-07-04T22:35:03+0000",
#    "clientKey": "8ad807b0316f84eb013191735a041b2b"
#   }
#  ],
#  "theGroup": {
#   "notes": "Las notas del grupo<br><br>son<br><br>estas<br>....<br>",
#   "id": "VQ611",
#   "groupLinesOfCredit": [],
#   "encodedKey": "8af4b2763852bc0201385421e2a70226",
#   "loanCycle": 0,
#   "creationDate": "2012-07-04T22:35:03+0000",
#   "lastModifiedDate": "2012-07-04T22:35:03+0000",
#   "groupName": "TestGroup",
#   "assignedUserKey": "8a5c1e9f34bdd2b90134c49b6b950948",
#   "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d"
#  },
#  "addresses": [
#   {
#    "line2": "Entre SnLuisPotosi y LopezMateos",
#    "indexInList": 0,
#    "parentKey": "8af4b2763852bc0201385421e2a70226",
#    "encodedKey": "8af4b2763852bc0201385421e2a90227",
#    "city": "Atizapan",
#    "country": "Mexico",
#    "region": "Mexico",
#    "line1": "Pedro Velasquez",
#    "postcode": "12345"
#   }
#  ],
#  "groupRoles": [
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b2022e",
#    "roleName": "President",
#    "groupRoleNameKey": "8a70db342e6d595a012e6d8391eb04be",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "clientKey": "8a101aa637fd34cc013816274ec902d9",
#    "indexInList": 0
#   },
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b5022f",
#    "roleName": "Secretary",
#    "groupRoleNameKey": "8a70db342e6d595a012e6d83925d04bf",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "clientKey": "8a43a79f3664edaa013733547d156af5",
#    "indexInList": 1
#   },
#   {
#    "encodedKey": "8af4b2763852bc0201385421e2b50230",
#    "roleName": "Treasurer",
#    "groupRoleNameKey": "8a70db342e6d595a012e6d83926504c0",
#    "groupKey": "8af4b2763852bc0201385421e2a70226",
#    "clientKey": "8a101aa637fd34cc0137ffdc3692006b",
#    "indexInList": 2
#   }
#  ],
#  "customInformation": [
#   {
#    "value": "ValorCustom",
#    "indexInList": 0,
#    "parentKey": "8af4b2763852bc0201385421e2a70226",
#    "encodedKey": "8af4b2763852bc0201385421e2aa0228",
#    "customField": {
#     "type": "GROUP_INFO",
#     "encodedKey": "8afae1dc2ecf2844012ee4a468f62773",
#     "isDefault": false,
#     "isRequired": false,
#     "name": "Referencia",
#     "dataType": "STRING",
#     "indexInList": -1
#    },
#    "customFieldKey": "8afae1dc2ecf2844012ee4a468f62773"
#   }
#  ]
# }

mod_urlfunc = getgroupurl

# Objeto con un grupo en Mambu
class MambuGroup(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    # Preprocesamiento
    def preprocess(self):
        try:
            for k,v in self['theGroup'].items():
                self[k] = v
            del(self.attrs['theGroup'])
        except Exception as e:
            pass

        if self.has_key('customInformation'):
            for custom in self['customInformation']:
                custom['name'] = custom['customField']['name']

        try:
            self['notes'] = self['notes'].replace("<div>", "").replace("</div>", "")
        except Exception as e:
            self['notes'] = ""

        self['name'] = self['groupName']

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        try:
            self.attrs['loanCycle'] = int(self.attrs['loanCycle'])
            self.attrs['creationDate'] = self.util_dateFormat(self.attrs['creationDate'])
            self.attrs['lastModifiedDate'] = self.util_dateFormat(self.attrs['lastModifiedDate'])

            if self.attrs.has_key('groupMembers'):
                for member in self.attrs['groupMembers']:
                    member['indexInList'] = int(member['indexInList'])
                    member['creationDate'] = self.util_dateFormat(member['creationDate'])

            if self.attrs.has_key('addresses'):
                for address in self.attrs['addresses']:
                    address['indexInList'] = int(address['indexInList'])

            if self.attrs.has_key('groupRoles'):
                for role in self.attrs['groupRoles']:
                    role['indexInList'] = int(role['indexInList'])

            if self.attrs.has_key('customInformation'):
                for custom in self.attrs['customInformation']:
                    custom['indexIntList'] = int(custom['indexInList'])
                    custom['customField']['indexInList'] = int(custom['customField']['indexInList'])

        self['clients'] = clients

            try:
                self.attrs['loanCycle'] = int(self.attrs['loanCycle'])
                self.attrs['creationDate'] = self.util_dateFormat('creationDate')
                self.attrs['lastModifiedDate'] = self.util_dateFormat('lastModifiedDate')
            except (TypeError, ValueError, KeyError) as err:
                raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
