# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getrepaymentsurl
from podemos import PodemosError, ERROR_CODES
from datetime import datetime

# {
# Propiedades
#  "state": "PAID",

# Saldos
#  "principalDue": "200",
#  "interestDue": "1.5",
#  "principalPaid": "200",
#  "interestPaid": "1.5",

# Fechas
#  "dueDate": "2012-06-17T00:00:00+0000",
#  "lastPaidDate": "2012-06-12T00:00:00+0000",
#  "repaidDate": "2012-06-12T00:00:00+0000",

# Relaciones
#  "parentAccountKey": "8af63f2837e19ef50137e1d755510016",
#  "assignedUserKey": "8a5c1e9f34bdd2b90134c49b6b950948",
#  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d"
#  "encodedKey": "8af63f2837e19ef50137e1d75563001c",
# }

mod_urlfunc = getrepaymentsurl

# Objeto con una lista de repayments de Mambu
class MambuRepayments(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convertDict2Attrs(self, *args, **kwargs):
        for n,r in enumerate(self.attrs):
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            repayment = MambuRepayment(urlfunc=None, entid=None, *args, **kwargs)
            repayment.init(r, *args, **kwargs)
            self.attrs[n] = repayment

# Objeto con un repayment de una cuenta en Mambu
class MambuRepayment(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__ + " - duedate: %s" % self['dueDate'].strftime("%Y-%m-%d")

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self, *args, **kwargs):
        try:
            self['interestDue'] = float(self['interestDue'])
            self['principalDue'] = float(self['principalDue'])
            self['feesDue'] = float(self['feesDue'])
            self['penaltyDue'] = float(self['penaltyDue'])

            self['interestPaid'] = float(self['interestPaid'])
            self['principalPaid'] = float(self['principalPaid'])
            self['feesPaid'] = float(self['feesPaid'])
            self['penaltyPaid'] = float(self['penaltyPaid'])

            try:
                self['dueDate'] = self.util_dateFormat(self['dueDate'])
            except KeyError as kerr:
                pass
            try:
                self['lastPaidDate'] = self.util_dateFormat(self['lastPaidDate'])
            except KeyError as kerr:
                pass
            try:
                self['lastPenaltyAppliedDate'] = self.util_dateFormat(self['lastPenaltyAppliedDate'])
            except KeyError as kerr:
                pass
            try:
                self['repaidDate'] = self.util_dateFormat(self['repaidDate'])
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
