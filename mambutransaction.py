from mambustruct import MambuStruct, MambuStructIterator
from podemos import PodemosError, DEBUG, ERROR_CODES
from datetime import datetime

# {
# Propiedades
#  "transactionId": 33080,
#  "type": "DISBURSMENT",
#  "amount": "1000",
#  "newState": "ACTIVE",
#  "comment": "Desembolsando cuenta",
#  "balance": "1000",

# Saldo
#  "principalPaid": "0",
#  "interestPaid": "0",
#  "feesPaid": "0",
#  "penaltyPaid": "0",

# Fechas
#  "creationDate": "2012-06-14T00:33:45+0000",
#  "entryDate": "2012-06-12T00:00:00+0000",

# Detalles
#  "details": {
#   "encodedKey": "8af62aae37e7dcef0137e8690251029a"
#  },

# Relaciones
#  "branchKey": "8a70db342e6d595a012e6e7158670f9d",
#  "userKey": "8a43a79f3664edaa0136a7ab14d4281c"
#  "parentAccountKey": "8af62aae37e7dcef0137e85e28e60282",
#  "encodedKey": "8af62aae37e7dcef0137e86902510299",
# }


# Objeto con una lista de Transacciones Mambu
class MambuTransactions(MambuStruct):
    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    def __len__(self):
        return len(self.attrs)

    def convertDict2Attrs(self):
        for t in self.attrs:
            trans = MambuTransaction(urlfunc=None, entid=None)
            trans.init(t)
            t = trans

# Objeto con una Transaccion de Mambu
class MambuTransaction(MambuStruct):
    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:
            self.attrs['transactionId'] = self.attrs['transactionId']
            self.attrs['type'] = self.attrs['type']
            try:
                self.attrs['amount'] = float(self.attrs['amount'])
            except KeyError as kerr:
                pass
            try:
                self.attrs['comment'] = self.attrs['comment']
            except KeyError as kerr:
                pass
            try:
                self.attrs['balance'] = float(self.attrs['balance'])
            except KeyError as kerr:
                pass

            try:
                self.attrs['principalPaid'] = float(self.attrs['principalPaid'])
            except KeyError as kerr:
                pass
            try:
                self.attrs['interestPaid'] = float(self.attrs['interestPaid'])
            except KeyError as kerr:
                pass
            try:
                self.attrs['feesPaid'] = float(self.attrs['feesPaid'])
            except KeyError as kerr:
                pass
            try:
                self.attrs['penaltyPaid'] = float(self.attrs['penaltyPaid'])
            except KeyError as kerr:
                pass

            try:
                self.attrs['creationDate'] = datetime.strptime(self.attrs['creationDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['entryDate'] = datetime.strptime(self.attrs['entryDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
