from mambustruct import MambuStruct
from podemos import PodemosError, getrepaymentsurl
from datetime import datetime

 # {
 #  "state": "PARTIALLY_PAID",
 #  "feesDue": "0",
 #  "interestDue": "1050",
 #  "penaltyDue": "0",
 #  "principalDue": "6250",
 #  "feesPaid": "0",
 #  "interestPaid": "1000",
 #  "penaltyPaid": "0",
 #  "principalPaid": "0",
 #  "dueDate": "2012-02-13T00:00:00+0000",
 #  "lastPaidDate": "2012-01-11T00:00:00+0000",
 #  "lastPenaltyAppliedDate": "2012-01-11T00:00:00+0000",
 #  "repaidDate": "2012-01-11T00:00:00+0000",
 #  "parentAccountKey": "8a4b860d349084d10134a1077022004a",
 #  "assignedUserKey": "8a70db342e6d595a012e6d8c47350f86",
 #  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d"
 #  "encodedKey": "8a4b860d349084d10134a10770280050",
 # }

urlfunc = getrepaymentsurl

# Objeto con los repayments de una cuenta en Mambu
class MambuRepayment(MambuStruct):
    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:
            for rp in self.attrs:
                rp['feesDue'] = float(rp['feesDue'])
                rp['interestDue'] = float(rp['interestDue'])
                rp['penaltyDue'] = float(rp['penaltyDue'])
                rp['principalDue'] = float(rp['principalDue'])

                rp['feesPaid'] = float(rp['feesPaid'])
                rp['interestPaid'] = float(rp['interestPaid'])
                rp['penaltyPaid'] = float(rp['penaltyPaid'])
                rp['principalPaid'] = float(rp['principalPaid'])

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
