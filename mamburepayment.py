from mambustruct import MambuStruct
from podemos import PodemosError, getrepaymentsurl, DEBUG, ERROR_CODES
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

urlfunc = getrepaymentsurl

# Objeto con los repayments de una cuenta en Mambu
class MambuRepayment(MambuStruct):
    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def __getitem__(self, key):
        return self.attrs[key]

    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:
            for rp in self.attrs:
                rp['interestDue'] = float(rp['interestDue'])
                rp['principalDue'] = float(rp['principalDue'])
                rp['feesDue'] = float(rp['feesDue'])
                rp['penaltyDue'] = float(rp['penaltyDue'])

                rp['interestPaid'] = float(rp['interestPaid'])
                rp['principalPaid'] = float(rp['principalPaid'])
                rp['feesPaid'] = float(rp['feesPaid'])
                rp['penaltyPaid'] = float(rp['penaltyPaid'])

                rp['dueDate'] = datetime.strptime(rp['dueDate'], "%Y-%m-%dT%H:%M:%S+0000")
                try:
                    rp['lastPaidDate'] = datetime.strptime(rp['lastPaidDate'], "%Y-%m-%dT%H:%M:%S+0000")
                except KeyError as kerr:
                    pass
                try:
                    rp['lastPenaltyAppliedDate'] = datetime.strptime(rp['lastPenaltyAppliedDate'], "%Y-%m-%dT%H:%M:%S+0000")
                except KeyError as kerr:
                    pass
                try:
                    rp['repaidDate'] = datetime.strptime(rp['repaidDate'], "%Y-%m-%dT%H:%M:%S+0000")
                except KeyError as kerr:
                    pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
