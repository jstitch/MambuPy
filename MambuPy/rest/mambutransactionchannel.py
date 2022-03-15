# coding: utf-8
"""Mambu Transaction Channel objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

MambuTansactionChannel holds a transaction channel.

MambuTansactionChannels holds a list of transaction channels.

Uses mambuutil.gettransactionchannelsurl as default urlfunc.
"""


from ..mambuutil import gettransactionchannelsurl
from .mambustruct import MambuStruct, MambuStructIterator

mod_urlfunc = gettransactionchannelsurl

# Objeto con una Cuenta desde Mambu
class MambuTransactionChannel(MambuStruct):
    """A Transaction Channel from Mambu.

    With the default urlfunc, entid argument must be the ID of the
    transaction channel you wish to retrieve.
    """

    def __init__(self, urlfunc=mod_urlfunc, entid="", *args, **kwargs):
        """Tasks done here:

        Just initializes the MambuStruct.
        """
        MambuStruct.__init__(
            self, urlfunc, entid, customFieldName="customFieldValues", *args, **kwargs
        )

    def preprocess(self):
        """Preprocessing.

        Each active custom field is given a 'name' key that holds the field
        name, and for each keyed name, the value of the custom field is
        assigned.
        """
        super(MambuTransactionChannel, self).preprocess()


class MambuTransactionChannels(MambuStruct):
    """A list of Transaction Channels from Mambu.

    With the default urlfunc, entid argument must be empty at
    instantiation time to retrieve all the transaction channels according to
    any other filter you send to the urlfunc.
    """

    def __init__(
        self,
        urlfunc=mod_urlfunc,
        entid="",
        itemclass=MambuTransactionChannel,
        *args,
        **kwargs
    ):
        """By default, entid argument is empty. That makes perfect
        sense: you want several groups, not just one.
        """
        self.itemclass = itemclass
        MambuStruct.__init__(self, urlfunc, entid, *args, **kwargs)

    def __iter__(self):
        return MambuStructIterator(self.attrs)

    def convertDict2Attrs(self, *args, **kwargs):
        """The trick for iterable Mambu Objects comes here:

        You iterate over each element of the responded List from Mambu,
        and create a TransactionChannel (or your own itemclass) object for each
        one, initializing them one at a time, and changing the attrs
        attribute (which just holds a list of plain dictionaries) with a
        TransactionChannel (or your own itemclass) just created.

        .. todo:: pass a valid (perhaps default) urlfunc, and its
          corresponding id to entid to each itemclass, telling MambuStruct
          not to connect() by default. It's desirable to connect at any
          other further moment to refresh some element in the list.
        """
        for n, l in enumerate(self.attrs):
            # ok ok, I'm modifying elements of a list while iterating it. BAD PRACTICE!
            try:
                params = self.params
            except AttributeError:
                params = {}
            kwargs.update(params)
            transaction_channel = self.itemclass(
                urlfunc=None, entid=None, *args, **kwargs
            )
            transaction_channel.init(l, *args, **kwargs)
            transaction_channel._MambuStruct__urlfunc = gettransactionchannelsurl
            self.attrs[n] = transaction_channel
