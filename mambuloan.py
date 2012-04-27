from mambustruct import MambuStruct
from podemos import PodemosError, getloansurl, DEBUG, ERROR_CODES
from datetime import datetime

# {
#  "id": "36530",
#  "loanName": "Credito Solidario",
#  "accountState": "ACTIVE",
#  "repaymentPeriodUnit": "WEEKS",
#  "repaymentInstallments": 16,
#  "interestRate": "4.2",
#  "interestChargeFrequency": "EVERY_FOUR_WEEKS",
#  "interestCalculationMethod": "FLAT",
#  "loanAmount": "100000",
#  "feesDue": "0",
#  "interestDue": "16800",
#  "penaltyDue": "0",
#  "principalDue": "100000",
#  "feesPaid": "0",
#  "interestPaid": "6250",
#  "penaltyPaid": "0",
#  "principalPaid": "31250",
#  "gracePeriod": 0,
#  "gracePeriodType": "NONE",
#  "repaymentPeriodCount": 1,
#  "notes": "Esta cuenta sera desembolsada y pagada poco a poco via la API<br>"
#  "approvedDate": "2012-01-03T00:54:10+0000",
#  "expectedDisbursementDate": "2012-01-02T00:00:00+0000",
#  "disbursementDate": "2012-01-01T00:00:00+0000",
#  "lastSetToArrearsDate": "2012-01-01T00:00:00+0000",
#  "closedDate": "2012-01-01T00:00:00+0000",
#  "creationDate": "2012-01-03T00:45:46+0000",
#  "lastModifiedDate": "2012-01-11T23:41:23+0000",
#  "productTypeKey": "8afae1dc2f3f6afa012f45bae91500d7",
#  "accountHolderType": "GROUP",
#  "accountHolderKey": "8a4b860d349084d10134a10077ef0048",
#  "assignedUserKey": "8a70db342e6d595a012e6d8c47350f86",
#  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
#  "encodedKey": "8a4b860d349084d10134a1077022004a",
# }

urlfunc = getloansurl

# Objeto con una Cuenta desde Mambu
class MambuLoan(MambuStruct):
    # De un diccionario de valores como cadenas, convierte los pertinentes a numeros/fechas
    def convertDict2Attrs(self):
        try:
            self.attrs['repaymentInstallments'] = int(self.attrs['repaymentInstallments'])
            self.attrs['interestRate'] = float(self.attrs['interestRate'])

            self.attrs['loanAmount'] = float(self.attrs['loanAmount'])

            self.attrs['feesDue'] = float(self.attrs['feesDue'])
            self.attrs['interestDue'] = float(self.attrs['interestDue'])
            self.attrs['penaltyDue'] = float(self.attrs['penaltyDue'])
            self.attrs['principalDue'] = float(self.attrs['principalDue'])

            self.attrs['feesPaid'] = float(self.attrs['feesPaid'])
            self.attrs['interestPaid'] = float(self.attrs['interestPaid'])
            self.attrs['penaltyPaid'] = float(self.attrs['penaltyPaid'])
            self.attrs['principalPaid'] = float(self.attrs['principalPaid'])

            self.attrs['creationDate'] = datetime.strptime(self.attrs['creationDate'], "%Y-%m-%dT%H:%M:%S+0000")
            self.attrs['lastModifiedDate'] = datetime.strptime(self.attrs['lastModifiedDate'], "%Y-%m-%dT%H:%M:%S+0000")

            try:
                self.attrs['approvedDate'] = datetime.strptime(self.attrs['approvedDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['expectedDisbursementDate'] = datetime.strptime(self.attrs['expectedDisbursementDate'],
                                                                           "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['disbursementDate'] = datetime.strptime(self.attrs['disbursementDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['lastSetToArrearsDate'] = datetime.strptime(self.attrs['lastSetToArrearsDate'],
                                                                       "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass
            try:
                self.attrs['closedDate'] = datetime.strptime(self.attrs['closedDate'], "%Y-%m-%dT%H:%M:%S+0000")
            except KeyError as kerr:
                pass

        except (TypeError, ValueError, KeyError) as err:
            raise PodemosError("%s (%s)" % (ERROR_CODES["INVALID_DATA"], repr(err)))
