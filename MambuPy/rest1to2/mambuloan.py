from mambupy.rest.mambuloan import MambuLoan as MambuLoan1
from mambupy.rest1to2.mambustruct import MambuStruct, process_filters


class MambuLoan(MambuStruct, MambuLoan1):
    def __init__(self, *args, **kwargs):
        process_filters(
            ["accountState",
             "branchId", "centreId", "creditOfficerUsername"], kwargs)
        super().__init__(*args, **kwargs)
