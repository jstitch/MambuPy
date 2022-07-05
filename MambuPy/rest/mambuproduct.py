# coding: utf-8
"""Mambu Products objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuProduct holds a product.

MambuProducts holds a list of products.

Uses mambugeturl.getproducturl as default urlfunc
"""


from ..mambugeturl import getproductsurl
from .mambustruct import MambuStruct, MambuStructIterator

mod_urlfunc = getproductsurl


class MambuProduct(MambuStruct):
    """A Product from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    product you wish to retrieve.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
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

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """By default, entid argument is empty. That makes perfect
        sense: you want several products, not just one
        """
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

                You iterate over each element of the responded List from Mambu,
                and create a Mambu Product object for each one, initializing them
                one at a time, and changing the attrs attribute (which just
                holds a list of plain dictionaries) with a MambuProduct just
                created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
                  corresponding id to entid to each MambuProduct, telling
                  MambuStruct not to connect() by default. It's desirable to
                  connect at any other further moment to refresh some element in
                  the list.
        """
        for n, r in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            try:
                self.mambuproductclass
            except AttributeError:
                self.mambuproductclass = MambuProduct

            product = self.mambuproductclass(urlfunc=None, entid=None, *args, **kwargs)
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

    .. todo:: is there a better way to implement cache directly on
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
            # cls.__instance = super(AllMambuProducts, cls).__new__(cls, *args, **kwargs)
            cls.__instance = super(AllMambuProducts, cls).__new__(cls)
        else:
            cls.__instance.noinit = True
        return cls.__instance

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """If you have already retrieved products, you don't contact
        Mambu. If you haven't, you do.
        """
        try:
            getattr(self, "noinit")
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
            if name in ["params", "noinit", "mambuproductclass"]:
                raise AttributeError
            return self[name]

    def convert_dict_to_attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

                You iterate over each element of the responded List from Mambu,
                and create a Mambu Product object for each one, initializing them
                one at a time, and changing the attrs attribute (which just
                holds a list of plain dictionaries) with a MambuProduct just
                created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
                  corresponding id to entid to each MambuProduct, telling
                  MambuStruct not to connect() by default. It's desirable to
                  connect at any other further moment to refresh some element in
                  the list.
        """
        for n, r in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            try:
                self.mambuproductclass
            except AttributeError:
                self.mambuproductclass = MambuProduct

            product = self.mambuproductclass(urlfunc=None, entid=None, *args, **kwargs)
            product.init(r, *args, **kwargs)
            product._MambuStruct__urlfunc = getproductsurl
            self.attrs[n] = product
