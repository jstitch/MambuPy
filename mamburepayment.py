# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getrepaymentsurl

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

# Objeto con un repayment de una cuenta en Mambu
class MambuRepayment(MambuStruct):
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__ + " - duedate: %s" % self['dueDate'].strftime("%Y-%m-%d")

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
