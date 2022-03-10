"""Interfaces for Mambu Objects.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary

   MambuAttachable
   MambuSearchable
"""

from abc import ABC, abstractmethod


class MambuAttachable(ABC):
    """An entity which can attach documents"""

    @abstractmethod
    def attach_document(self, filename, title="", notes=""):
        """uploads an attachment to this entity

        Args:
          filename (str) - path and filename of file to upload as attachment
          title (str) - name to assign to the attached file in Mambu
          notes (str) - notes to associate to the attached file in Mambu

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
    ):
        """search, several entities, filtering criteria allowed

        Args:
          filterCriteria (list of dicts) - fields according to
                              LoanAccountFilterCriteria schema
          sortingCriteria (dict) - fields according to
                            LoanAccountSortingCriteria
          offset (int) - pagination, index to start searching
          limit (int) - pagination, number of elements to retrieve
          paginationDetails (str ON/OFF) - ask for details on pagination
          detailsLevel (str BASIC/FULL) - ask for extra details or not

        Returns:
          list of instances of an entity with data from Mambu
        """
        raise NotImplementedError
