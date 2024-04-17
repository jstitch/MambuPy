"""MambuProduct entity: a MambuEntity struct for Products.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from .entities import (
    MambuEntity,
    MambuEntityWritable,
    MambuEntityAttachable,
    MambuEntityCommentable,
)


class MambuProduct(
    MambuEntity, MambuEntityWritable, MambuEntityAttachable, MambuEntityCommentable
):
    """MambuProduct entity"""

    _prefix = "loanproducts"
    """prefix constant for connections to Mambu"""

    _filter_keys = []
    """allowed filters for get_all filtering"""

    _sortBy_fields = [
        "creationDate",
        "lastModifiedDate",
        "id",
        "productName",
    ]
    """allowed fields for get_all sorting"""

    _ownerType = "LOAN_PRODUCT"
    """owner type of this entity"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._attachments = {}

    @classmethod
    def get(cls, entid, get_entities=False, **kwargs):
        """get, a single entity, identified by its entid.

        Args:
          entid (str): ID for the entity
          get_entities (bool): should MambuPy automatically instantiate other
                               MambuPy entities found inside the retrieved
                               entity?

        Returns:
          instance of an entity with data from Mambu
        """
        if "detailsLevel" in kwargs:
            kwargs.pop("detailsLevel")
        return super().get(
            entid, detailsLevel="FULL", get_entities=get_entities, **kwargs
        )

    def refresh(self):
        """get again this single entity, identified by its entid.

        Updates _attrs with responded data. Loses any change on _attrs that
        overlaps with anything from Mambu. Leaves alone any other properties
        that don't come in the response.
        """
        super().refresh(detailsLevel="FULL")

    @classmethod
    def get_all(
        cls, filters=None, offset=None, limit=None, paginationDetails="OFF", sortBy=None
    ):
        """get_all, several entities, filtering allowed

        Args:
          filters (dict): key-value filters, dependes on each entity
                          (keys must be one of the _filter_keys)
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          sortBy (str): ``field1:ASC,field2:DESC``, sorting criteria for
                        results (fields must be one of the _sortBy_fields)

        Returns:
          list of instances of an entity with data from Mambu
        """
        return super().get_all(
            filters, offset, limit, paginationDetails, detailsLevel="FULL", sortBy=sortBy
        )
