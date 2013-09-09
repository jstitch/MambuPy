# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import gettransactionsurl
from podemos import PodemosError, ERROR_CODES
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


mod_urlfunc = gettransactionsurl

# Objeto con una lista de Transacciones Mambu
class MambuTransactions(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convertDict2Attrs(self, *args, **kwargs):
        for n,t in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            trans = MambuTransaction(urlfunc=None, entid=None, *args, **kwargs)
            trans.init(t, *args, **kwargs)
            self.attrs[n] = trans

# Objeto con una Transaccion de Mambu
class MambuTransaction(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__ + " - transactionid: %s" % self['transactionid']

        # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        try:
            MambuStruct.convertDict2Attrs(self, *args, **kwargs)
        except Exception as ex:
            raise ex
        # try:
        #     self['transactionId'] = self['transactionId']
        #     self['type'] = self['type']
        #     try:
        #         self['amount'] = float(self['amount'])
        #     except KeyError as kerr:
        #         pass
        #     try:
        #         self['comment'] = self['comment']
        #     except KeyError as kerr:
        #         pass
        #     try:
        #         self['balance'] = float(self['balance'])
        #     except KeyError as kerr:
        #         pass

        #     try:
        #         self['principalPaid'] = float(self['principalPaid'])
        #     except KeyError as kerr:
        #         pass
        #     try:
        #         self['interestPaid'] = float(self['interestPaid'])
        #     except KeyError as kerr:
        #         pass
        #     try:
        #         self['feesPaid'] = float(self['feesPaid'])
        #     except KeyError as kerr:
        #         pass
        #     try:
        #         self['penaltyPaid'] = float(self['penaltyPaid'])
        #     except KeyError as kerr:
        #         pass

        #     try:
        #         self['creationDate'] = self.util_dateFormat(self['creationDate'])
        #     except KeyError as kerr:
        #         pass
        #     try:
        #         self['entryDate'] = self.util_dateFormat(self['entryDate'])
        #     except KeyError as kerr:
        #         pass

        # except (TypeError, ValueError, KeyError) as err:
        #     raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
