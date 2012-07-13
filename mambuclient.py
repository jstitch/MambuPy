from mambustruct import MambuStruct
from podemos import PodemosError, getclienturl, DEBUG, ERROR_CODES
from datetime import datetime

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


urlfunc = getclienturl

class MambuClient(MambuStruct):
    # Preprocesamiento
    def preprocess(self):
        try:
            for k,v in self.attrs['client'].items():
                self.attrs[k] = v
            del(self.attrs['client'])
        except Exception as e:
            pass

        self.attrs['firstName'] = self.attrs['firstName'].strip()
        self.attrs['middleName'] = self.attrs['middleName'].strip()
        self.attrs['lastName'] = self.attrs['lastName'].strip()

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:

            try:
                self.attrs['birthDate'] = datetime.strptime(self.attrs['birthDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass

            self.attrs['loanCycle'] = int(self.attrs['loanCycle'])
            self.attrs['groupLoanCycle'] = int(self.attrs['groupLoanCycle'])

            try:
                self.attrs['approvedDate'] = datetime.strptime(self.attrs['approvedDate'], "%Y-%m-%dT%H:%M:%S+0000")
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
            try:
                self.attrs['activationDate'] = datetime.strptime(self.attrs['activationDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
