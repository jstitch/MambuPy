# coding: utf-8

from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getproductsurl

# {
# Propiedades
#   "productName": "Credito Adicional",
#   "id": "2",
#   "productDescription": "Credito que se otorga a un grupo solidario para incrementar su liquidez.",
#   "activated": false,
#   "encodedKey": "8afae1dc2f3f6afa012f45bc7ed000d9",

# Atributos
#   "loanType": "PURE_GROUP",
#   "gracePeriodType": "NONE",
# interest
#   "daysInYear": "E30_360",
#   "defaultInterestRate": "4.2",
#   "minInterestRate": "4.2",
#   "maxInterestRate": "16.8",
#   "interestChargeFrequency": "EVERY_FOUR_WEEKS",
#   "interestCalculationMethod": "FLAT",
#   "interestApplicationMethod": "ON_DISBURSEMENT",
#   "interestRateSource": "FIXED_INTEREST_RATE",
#   "scheduleInterestDaysCountMethod": "USING_REPAYMENT_PERIODICITY",
# id gen
#   "idGeneratorType": "RANDOM_PATTERN",
#   "idPattern": "#####",
# cantidades
#   "defaultLoanAmount": "1000",
#   "minLoanAmount": "1000",
#   "maxLoanAmount": "100000",
# pagos
#   "defaultNumInstallments": 4,
#   "minNumInstallments": 4,
#   "maxNumInstallments": 16,
# repayments
#   "repaymentScheduleMethod": "FIXED",
#   "scheduleDueDatesMethod": "INTERVAL",
#   "defaultRepaymentPeriodCount": 1,
#   "repaymentPeriodUnit": "WEEKS",
#   "defaultPrincipalRepaymentInterval": 1,
#   "roundingRepaymentScheduleMethod": "NO_ROUNDING",
#   "repaymentCurrencyRounding": "NO_ROUNDING",
#   "paymentMethod": "HORIZONTAL",
#   "prepaymentAcceptance": "ACCEPT_PREPAYMENTS",
#   "futurePaymentsAcceptance": "NO_FUTURE_PAYMENTS",
#   "repaymentAllocationOrder": [
#     "PRINCIPAL",
#     "INTEREST",
#     "PENALTY",
#     "FEE"
#   ],
#   "repaymentScheduleEditOptions": [
#     "ADJUST_PAYMENT_DATES",
#     "ADJUST_PRINCIPAL_PAYMENT_SCHEDULE",
#     "ADJUST_INTEREST_PAYMENT_SCHEDULE",
#     "ADJUST_FEE_PAYMENT_SCHEDULE",
#     "ADJUST_PENALTY_PAYMENT_SCHEDULE"
#   ],
# }
# arrears and fees
#   "loanPenaltyCalculationMethod": "NONE",
#   "loanPenaltyGracePeriod": 0,
#   "arrearsDateCalculationMethod": "DATE_OF_LAST_LATE_REPAYMENT",
#   "arrearsTolerancePeriod": 0,
#   "loanFees": [
#         {
#           "encodedKey": "8a4a2142399b1bee01399cc72da55941",
#           "name": "Mora por pago atrasado",
#           "amount": "100",
#           "amountCalculationMethod": "FLAT",
#           "trigger": "LATE_REPAYMENT",
#           "active": true,
#           "creationDate": "2012-09-06T18:11:02+0000"
#         }
#       ],
#   "allowArbitraryFees": true,
#   "arrearsNonWorkingDaysMethod": "INCLUDED",
# accounting
#   "accountingMethod": "NONE",
#   "loanProductRules": [],
#   "accountLinkingEnabled": false,
#   "autoLinkAccounts": false,
#   "autoCreateLinkedAccounts": false,
#   "taxesOnInterestEnabled": false,
#   "taxesOnFeesEnabled": false,
#   "taxesOnPenaltyEnabled": false,
#   "allowGuarantors": false,
#   "allowCollateral": false,
#   "lendingMethodology": "FIXED"

# Fechas
#   "creationDate": "2011-04-11T18:04:31+0000",
#   "lastModifiedDate": "2012-11-30T18:56:42+0000",

mod_urlfunc = getproductsurl

# Objeto con un producto en Mambu
class MambuProduct(MambuStruct):
    # _instances = []
    # def __new__(cls, *args, **kwargs):
    #     try:
    #         inst = None
    #         if kwargs['entid'] and type(kwargs['entid'])==str and len(kwargs['entid']) > 0:
    #             if kwargs['entid'] not in [ ids['id'] for ids in cls._instances ]:
    #                 inst = super(MambuProduct, cls).__new__(cls, *args, **kwargs)
    #                 cls._instances.append(inst)
    #             else:
    #                 inst = [ ids for ids in cls._instances if ids['id']==kwargs['entid'] ][0]
    #                 inst.noinit = True
    #         else:
    #             inst = super(MambuProduct, cls).__new__(cls, *args, **kwargs)
    #     except KeyError:
    #         inst = super(MambuProduct, cls).__new__(cls, *args, **kwargs)
    #     return inst
    
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        # try:
        #     getattr(self,"noinit")
        # except AttributeError:
            MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

# Objeto con una lista de productos de Mambu
class MambuProducts(MambuStruct):
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
            product = MambuProduct(urlfunc=None, entid=None, *args, **kwargs)
            product.init(r, *args, **kwargs)
            self.attrs[n] = product
