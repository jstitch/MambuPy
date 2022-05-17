"""Interfaces for Mambu Objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

from abc import ABC, abstractmethod


class MambuWritable(ABC):
    """An entity which allows basic write operations"""

    @abstractmethod
    def update(self):  # pragma: no cover
        """updates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        raise NotImplementedError

    @abstractmethod
    def create(self):  # pragma: no cover
        """creates a mambu entity

        Uses the current values of the _attrs to send to Mambu.
        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.
        """
        raise NotImplementedError

    @abstractmethod
    def patch(self, fields=None, autodetect_remove=False):  # pragma: no cover
        """patches a mambu entity

        Allows patching of parts of the entity up to Mambu.

        fields is a list of the values in the _attrs that will be sent to Mambu

        autodetect automatically searches for deleted fields and patches a
        remove in Mambu.

        Pre-requires that CustomFields are updated previously.
        Post-requires that CustomFields are extracted again.

        Args:
          fields (list of str): list of ids of fields to explicitly patch
          autodetect_remove (bool): False: if deleted fields, don't remove them
                                    True: if delete field, remove them

        Autodetect operation, for any field (every field if fields param is
        None):
          * ADD: in attrs, but not in resp
          * REPLACE: in attrs, and in resp
          * REMOVE: not in attrs, but in resp
          * MOVE: not yet implemented (how to autodetect? request needs 'from' element)

        Raises:
          `MambuPyError`: if field not in attrrs, and not in resp
        """
        raise NotImplementedError


class MambuAttachable(ABC):
    """An entity which can attach documents"""

    @abstractmethod
    def attach_document(self, filename, title="", notes=""):  # pragma: no cover
        """uploads an attachment to this entity

        Args:
          filename (str): path and filename of file to upload as attachment
          title (str): name to assign to the attached file in Mambu
          notes (str): notes to associate to the attached file in Mambu

        Returns:
          Mambu's response with metadata of the attached document
        """
        raise NotImplementedError


class MambuSearchable(ABC):
    """An entity which allows searching endpoint"""

    @classmethod
    @abstractmethod
    def search(
        cls,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
    ):  # pragma: no cover
        """search, several entities, filtering criteria allowed

        Args:
          filterCriteria (list of dicts): fields according to
                              LoanAccountFilterCriteria schema
          sortingCriteria (dict): fields according to
                            LoanAccountSortingCriteria
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not

        Returns:
          list of instances of an entity with data from Mambu
        """
        raise NotImplementedError


class MambuOwner(ABC):
    """"""


class MambuHolder(ABC):
    """"""
