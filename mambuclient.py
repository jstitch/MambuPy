# coding: utf-8

from mambustruct import MambuStruct
from mambuutil import getclienturl

from datetime import datetime
from util import strip_consecutive_repeated_char as scrc

# {
#  "idDocuments": [
#   {
#    "encodedKey": "8a101aa637fd34cc0137ffda2df40067",
#    "documentId": "VIMC730305MMCLDR08",
#    "documentType": "CURP",
#    "clientKey": "8a101aa637fd34cc0137ffda2df10066",
#    "issuingAuthority": "SEGOB",
#    "indexInList": 0
#   }
#  ],

#  "client": {
# Datos del cliente
#  "id": "PIT087",
#  "firstName": "MARIA DEL CARMEN",
#  "middleName": "",
#  "lastName": "VILLAFRANCA MADRIGAL",
#  "state": "ACTIVE",
#  "gender": "FEMALE",
#  "birthDate": "1973-03-05T00:00:00+0000",
# Datos de acceso
#  "homePhone": "58274975",
#  "mobilePhone1": "5538785979",
# Otros
#  "loanCycle": 0,
#  "groupLoanCycle": 1,
#  "clientLinesOfCredit": []
# Fechas
#  "approvedDate": "2012-06-18T13:48:37+0000",
#  "creationDate": "2012-06-18T13:48:37+0000",
#  "lastModifiedDate": "2012-07-09T16:54:48+0000",
#  "activationDate": "2012-06-18T14:08:32+0000",
# Relaciones
#  "encodedKey": "8a101aa637fd34cc0137ffda2df10066",
#  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
#  },

#  "addresses": [
#   {
#    "line2": "LA COLMENA",
#    "indexInList": 0,
#    "parentKey": "8a101aa637fd34cc0137ffda2df10066",
#    "encodedKey": "8a101aa637fd34cc0137ffda2df50068",
#    "city": "NICOLAS ROMERO",
#    "country": "MEXICO",
#    "region": "MEXICO",
#    "line1": "AV COLMENA S/N",
#    "postcode": "54467"
#   }
#  ],

#  "customInformation": [
#   {
#    "value": "testing1",
#    "indexInList": 0,
#    "parentKey": "8a101aa637fd34cc0137ffda2df10066",
#    "encodedKey": "8af4b276385d069301386caa2f7209ed",
#    "customField": {
#     "amounts": {
#      "testing2": "3",
#      "testing1": "1"
#     },
#     "type": "CLIENT_INFO",
#     "encodedKey": "8af4b276385d069301386ca9c0f609ec",
#     "isDefault": false,
#     "isRequired": false,
#     "name": "Test",
#     "dataType": "SELECTION",
#     "indexInList": 1,
#     "values": [
#      "testing2",
#      "testing1"
#     ],
#     "description": "pruebas"
#    },
#    "customFieldKey": "8af4b276385d069301386ca9c0f609ec",
#    "amount": "1"
#   }
#  ],

#  "groupKeys": [
#   "8a5e35f730dd26e4013132ec04b12a66"
#  ]
# }


mod_urlfunc = getclienturl

class MambuClient(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    # Preprocesamiento
    def preprocess(self):
        try:
            for k,v in self['client'].items():
                self[k] = v
            del(self.attrs['client'])
        except Exception as e:
            pass

        if self.has_key('customInformation'):
            for custom in self['customInformation']:
                custom['name'] = custom['customField']['name']

        for k,v in self.items():
            try:
                self[k] = v.strip()
            except Exception:
                pass

        try:
            self['firstName'] = scrc(self['firstName'], " ")
        except Exception as e:
            self['firstName'] = ""
        try:
            self['middleName'] = scrc(self['middleName'], " ")
        except Exception as ex:
            self['middleName'] = ""
        self['lastName'] = scrc(self['lastName'], " ")
        self['firstLastName'] = " ".join(self['lastName'].split(" ")[:-1])
        self['secondLastName'] = " ".join(self['lastName'].split(" ")[-1:])

        self['name'] = "%s%s %s" % (self['firstName'],
                                          " " + self['middleName'] if self["middleName"] != "" else "",
                                          self['lastName'])

        self['address'] = {}
        try:
            for name,item in self['addresses'][0].items():
                try:
                    self['addresses'][0][name] = item
                    self['address'][name] = item
                except AttributeError:
                    pass
        except KeyError:
            pass

        try:
            for idDoc in self['idDocuments']:
                self[idDoc['documentType']] = idDoc['documentId']
        except KeyError:
            pass

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        try:
            try:
                self['birthDate'] = self.util_dateFormat(self['birthDate'])
            except KeyError as kerr:
                pass

            self['loanCycle'] = int(self['loanCycle'])
            self['groupLoanCycle'] = int(self['groupLoanCycle'])

            try:
                self['approvedDate'] = self.util_dateFormat(self['approvedDate'])
            except KeyError as kerr:
                pass
            try:
                self['creationDate'] = self.util_dateFormat(self['creationDate'])
            except KeyError as kerr:
                pass
            try:
                self['lastModifiedDate'] = self.util_dateFormat(self['lastModifiedDate'])
            except KeyError as kerr:
                pass
            try:
                self['activationDate'] = self.util_dateFormat(self['activationDate'])
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
