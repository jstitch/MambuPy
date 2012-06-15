from mambustruct import MambuStruct
from podemos import PodemosError, getloansurl, DEBUG, ERROR_CODES
from datetime import datetime

# {
# Datos de la cuenta
#  "id": "38802",
#  "loanName": "Validation Credito Solidario",

# Propiedades de la cuenta
#  "accountState": "ACTIVE",
#  "repaymentPeriodUnit": "DAYS",
#  "repaymentInstallments": 5,
#  "interestRate": "4.2",
#  "interestChargeFrequency": "EVERY_FOUR_WEEKS",
#  "interestCalculationMethod": "FLAT_FIXED",
#  "interestRateSource": "FIXED_INTEREST_RATE",
#  "interestAdjustment": "0",
#  "accruedInterest": "0",
#  "principalRepaymentInterval": 1,
#  "loanAmount": "1000",

# Saldos
#  "principalDue": "200",
#  "interestDue": "1.5",
#  "feesDue": "0",
#  "penaltyDue": "0",
#  "principalPaid": "0",
#  "interestPaid": "0",
#  "feesPaid": "0",
#  "penaltyPaid": "0",
#  "principalBalance": "1000",
#  "interestBalance": "7.5",

# Mas propiedades
#  "gracePeriod": 0,
#  "gracePeriodType": "NONE",
#  "repaymentPeriodCount": 1,
#  "notes": "testing notes<br>",

# Fechas
#  "approvedDate": "2012-06-13T18:05:04+0000",
#  "expectedDisbursementDate": "2012-06-12T00:00:00+0000",
#  "disbursementDate": "2012-06-12T00:00:00+0000",
#  "lastInterestAppliedDate": "2012-06-12T00:00:00+0000"
#  "lastAccountAppraisalDate": "2012-06-13T18:05:35+0000",
#  "creationDate": "2012-06-13T18:04:49+0000",
#  "lastModifiedDate": "2012-06-13T18:05:35+0000",
#  "lastSetToArrearsDate": "2012-01-01T00:00:00+0000",
#  "closedDate": "2012-01-01T00:00:00+0000",

# Relaciones
#  "productTypeKey": "8afae1dc2f3f6afa012f45bae91500d7",
#  "accountHolderType": "GROUP",
#  "accountHolderKey": "8af20ea03755684801375d6b5f7f145b",
#  "assignedUserKey": "8a5c1e9f34bdd2b90134c49b6b950948",
#  "assignedBranchKey": "8a70db342e6d595a012e6e7158670f9d",
#  "encodedKey": "8af25b7337e52f8b0137e704ef71057b",
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

            self.attrs['principalDue'] = float(self.attrs['principalDue'])
            self.attrs['interestDue'] = float(self.attrs['interestDue'])
            self.attrs['feesDue'] = float(self.attrs['feesDue'])
            self.attrs['penaltyDue'] = float(self.attrs['penaltyDue'])

            self.attrs['principalPaid'] = float(self.attrs['principalPaid'])
            self.attrs['interestPaid'] = float(self.attrs['interestPaid'])
            self.attrs['feesPaid'] = float(self.attrs['feesPaid'])
            self.attrs['penaltyPaid'] = float(self.attrs['penaltyPaid'])

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
