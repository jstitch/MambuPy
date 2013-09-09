# coding: utf-8

from mambustruct import MambuStruct
from mambuutil import getclienturl
from podemos import PodemosError, ERROR_CODES
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
            for k,v in self.attrs['client'].items():
                self.attrs[k] = v
            del(self.attrs['client'])
        except Exception as e:
            pass

        if self.attrs.has_key('customInformation'):
            for custom in self.attrs['customInformation']:
                custom['name'] = custom['customField']['name']

        for k,v in self.attrs.items():
            try:
                self.attrs[k] = v.strip()
            except Exception:
                pass

        try:
            self.attrs['firstName'] = scrc(self.attrs['firstName'], " ")
        except Exception as e:
            self.attrs['firstName'] = ""
        try:
            self.attrs['middleName'] = scrc(self.attrs['middleName'], " ")
        except Exception as ex:
            self.attrs['middleName'] = ""
        self.attrs['lastName'] = scrc(self.attrs['lastName'], " ")
        self.attrs['firstLastName'] = " ".join(self.attrs['lastName'].split(" ")[:-1])
        self.attrs['secondLastName'] = " ".join(self.attrs['lastName'].split(" ")[-1:])

        self.attrs['name'] = "%s%s %s" % (self.attrs['firstName'],
                                          " " + self.attrs['middleName'] if self.attrs["middleName"] != "" else "",
                                          self.attrs['lastName'])

        self.attrs['address'] = {}
        try:
            for name,item in self.attrs['addresses'][0].items():
                try:
                    self.attrs['addresses'][0][name] = item
                    self.attrs['address'][name] = item
                except AttributeError:
                    pass
        except KeyError:
            pass

        try:
            for idDoc in self.attrs['idDocuments']:
                self.attrs[idDoc['documentType']] = idDoc['documentId']
        except KeyError:
            pass

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        try:

            try:
                formatoFecha=kwargs['dateFormat']
            except KeyError:
                formatoFecha="%Y-%m-%dT%H:%M:%S+0000"
            try:
                self.attrs['birthDate'] = self.util_dateFormat(self.attrs['birthDate'], formatoFecha)
            except KeyError as kerr:
                pass

            self.attrs['loanCycle'] = int(self.attrs['loanCycle'])
            self.attrs['groupLoanCycle'] = int(self.attrs['groupLoanCycle'])

            try:
                self.attrs['approvedDate'] = self.util_dateFormat(self.attrs['approvedDate'], formatoFecha)
            except KeyError as kerr:
                pass
            try:
                self.attrs['creationDate'] = self.util_dateFormat(self.attrs['creationDate'], formatoFecha)
            except KeyError as kerr:
                pass
            try:
                self.attrs['lastModifiedDate'] = self.util_dateFormat(self.attrs['lastModifiedDate'], formatoFecha)
            except KeyError as kerr:
                pass
            try:
                self.attrs['activationDate'] = self.util_dateFormat(self.attrs['activationDate'], formatoFecha)
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
