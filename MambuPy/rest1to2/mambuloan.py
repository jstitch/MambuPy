from mambupy.rest.mambuloan import MambuLoan as MambuLoan1
from mambupy.rest1to2.mambustruct import MambuStruct


class MambuLoan(MambuStruct, MambuLoan1):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "connect" in kwargs:
            kwargs.pop("connect")
        if "fullDetails" in kwargs:
            kwargs.pop("fullDetails")
