# coding: utf-8
"""Mambu Products objects.

MambuProduct holds a product.

MambuProducts holds a list of products.

Uses mambuutil.getproducturl as default urlfunc

Example response from Mambu for products (please omit comment lines beginning with #):
{
# Propiedades
  "productName": "Credito Adicional",
  "id": "2",
  "productDescription": "Credito que se otorga a un grupo solidario para incrementar su liquidez.",
  "activated": false,
  "encodedKey": "8afae1dc2f3f6afa012f45bc7ed000d9",

# Atributos
  "loanType": "PURE_GROUP",
  "gracePeriodType": "NONE",
# interest
  "daysInYear": "E30_360",
  "defaultInterestRate": "4.2",
  "minInterestRate": "4.2",
  "maxInterestRate": "16.8",
  "interestChargeFrequency": "EVERY_FOUR_WEEKS",
  "interestCalculationMethod": "FLAT",
  "interestApplicationMethod": "ON_DISBURSEMENT",
  "interestRateSource": "FIXED_INTEREST_RATE",
  "scheduleInterestDaysCountMethod": "USING_REPAYMENT_PERIODICITY",
# id gen
  "idGeneratorType": "RANDOM_PATTERN",
  "idPattern": "#####",
# cantidades
  "defaultLoanAmount": "1000",
  "minLoanAmount": "1000",
  "maxLoanAmount": "100000",
# pagos
  "defaultNumInstallments": 4,
  "minNumInstallments": 4,
  "maxNumInstallments": 16,
# repayments
  "repaymentScheduleMethod": "FIXED",
  "scheduleDueDatesMethod": "INTERVAL",
  "defaultRepaymentPeriodCount": 1,
  "repaymentPeriodUnit": "WEEKS",
  "defaultPrincipalRepaymentInterval": 1,
  "roundingRepaymentScheduleMethod": "NO_ROUNDING",
  "repaymentCurrencyRounding": "NO_ROUNDING",
  "paymentMethod": "HORIZONTAL",
  "prepaymentAcceptance": "ACCEPT_PREPAYMENTS",
  "futurePaymentsAcceptance": "NO_FUTURE_PAYMENTS",
  "repaymentAllocationOrder": [
    "PRINCIPAL",
    "INTEREST",
    "PENALTY",
    "FEE"
  ],
  "repaymentScheduleEditOptions": [
    "ADJUST_PAYMENT_DATES",
    "ADJUST_PRINCIPAL_PAYMENT_SCHEDULE",
    "ADJUST_INTEREST_PAYMENT_SCHEDULE",
    "ADJUST_FEE_PAYMENT_SCHEDULE",
    "ADJUST_PENALTY_PAYMENT_SCHEDULE"
  ],
}
# arrears and fees
  "loanPenaltyCalculationMethod": "NONE",
  "loanPenaltyGracePeriod": 0,
  "arrearsDateCalculationMethod": "DATE_OF_LAST_LATE_REPAYMENT",
  "arrearsTolerancePeriod": 0,
  "loanFees": [
        {
          "encodedKey": "8a4a2142399b1bee01399cc72da55941",
          "name": "Mora por pago atrasado",
          "amount": "100",
          "amountCalculationMethod": "FLAT",
          "trigger": "LATE_REPAYMENT",
          "active": true,
          "creationDate": "2012-09-06T18:11:02+0000"
        }
      ],
  "allowArbitraryFees": true,
  "arrearsNonWorkingDaysMethod": "INCLUDED",
# accounting
  "accountingMethod": "NONE",
  "loanProductRules": [],
  "accountLinkingEnabled": false,
  "autoLinkAccounts": false,
  "autoCreateLinkedAccounts": false,
  "taxesOnInterestEnabled": false,
  "taxesOnFeesEnabled": false,
  "taxesOnPenaltyEnabled": false,
  "allowGuarantors": false,
  "allowCollateral": false,
  "lendingMethodology": "FIXED"

# Fechas
  "creationDate": "2011-04-11T18:04:31+0000",
  "lastModifiedDate": "2012-11-30T18:56:42+0000",

TODO: update this with later responses from Mambu, and perhaps certain
behaviours are obsolete here
"""


from mambustruct import MambuStruct, MambuStructIterator
from mambuutil import getproductsurl


mod_urlfunc = getproductsurl

class MambuProduct(MambuStruct):
    """A Product from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    product you wish to retrieve.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


class MambuProducts(MambuStruct):
    """A list of Products from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the products according to any
    other filter you send to the urlfunc.
    """
    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several products, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Product object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuProduct just
        created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each MambuProduct, telling
        MambuStruct not to connect() by default. It's desirable to
        connect at any other further moment to refresh some element in
        the list.
        """
        for n,r in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            product = MambuProduct(urlfunc=None, entid=None, *args, **kwargs)
            product.init(r, *args, **kwargs)
            self.attrs[n] = product


class AllMambuProducts(MambuStruct):
    """Singleton that holds ALL the Mambu products.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the products according to any
    other filter you send to the urlfunc.

    Caching singleton. You may not wish to retrieve from Mambu all the
    products every time you need to use them, so you can use this, which
    requests from Mambu one time only, and holds them here forever
    during your python session.

    To use it, instead of instantiating a MambuProducts() object when
    needing all the products from Mambu, instantiate an
    AllMambuProducts() object and the caching will be used by default.

    TODO: is there a better way to implement cache directly on
    MambuProducts()?

    Why have a cache? because Mambu products are not likely to change
    once you have them configured in Mambu. So it's better to prevent a
    lot of requests to get the same information over and over again.

    You are free to implement caches such as this on any other Mambu
    objects if you find it useful (perhaps groups or branches or any
    other Mambu entity do not change a lot on your own business?).
    Please try to be consistent on names and functionality.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(AllMambuProducts, cls).__new__(cls, *args, **kwargs)
        else:
            cls.__instance.noinit = True
        return cls.__instance


    def __init__(self, urlfunc=mod_urlfunc, entid='', *args, **kwargs):
        """If you have already retrieved products, you don't contact
        Mambu. If you haven't, you do.
        """
        try:
            getattr(self,"noinit")
        except AttributeError:
            MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)


    def __iter__(self):
        return MambuStructIterator(self.attrs)


    def __getattribute__(self, name):
        """Object-like get attribute"""
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # Iterable AllMambuProducts singleton also uses a special
            # noinit property that should raise AttributeError when
            # not set
            if name=='params' or name=='noinit':
                raise AttributeError
            return self[name]


    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a Mambu Product object for each one, initializing them
        one at a time, and changing the attrs attribute (which just
        holds a list of plain dictionaries) with a MambuProduct just
        created.

        TODO: pass a valid (perhaps default) urlfunc, and its
        corresponding id to entid to each MambuProduct, telling
        MambuStruct not to connect() by default. It's desirable to
        connect at any other further moment to refresh some element in
        the list.
        """
        for n,r in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError as aerr:
                params = {}
            kwargs.update(params)
            product = MambuProduct(urlfunc=None, entid=None, *args, **kwargs)
            product.init(r, *args, **kwargs)
            self.attrs[n] = product
