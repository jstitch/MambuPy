"""Connectors to Mambu.

Currently supports REST.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""
from abc import ABC, abstractmethod


class MambuConnector(ABC):
    """Interface for Connectors"""


class MambuConnectorReader(ABC):
    """Interface for Readers.

    A Reader supports the followint operations:

    - get (gets a single entity)
    - get_all (gets several entities, filtering allowed)
    - search (gets several entities, advanced filtering)
    - get_documents_metadata (gets the metadata of documents attached to some
                              entity)
    """

    @abstractmethod
    def mambu_get(self, entid, prefix, detailsLevel="BASIC"):
        """get, a single entity, identified by its entid.

        Args:
          entid (str): ID for the entity
          prefix (str): entity's URL prefix
          detailsLevel (str BASIC/FULL): ask for extra details or not
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_get_all(
        self,
        prefix,
        filters=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
        sortBy=None,
        **kwargs
    ):
        """get_all, several entities, filtering allowed

        Args:
          prefix (str): entity's URL prefix
          filters (dict): key-value filters (depends on each entity)
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
          detailsLevel (str BASIC/FULL): ask for extra details or not
          sortBy (str): ``field1:ASC,field2:DESC``, sorting criteria for
                        results
          kwargs (dict): extra parameters that a specific entity may receive in
                         its get_all method
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_search(
        self,
        prefix,
        filterCriteria=None,
        sortingCriteria=None,
        offset=None,
        limit=None,
        paginationDetails="OFF",
        detailsLevel="BASIC",
    ):
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
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_get_documents_metadata(
        self, entid, owner_type,
        offset=None, limit=None, paginationDetails="OFF",
    ):
        """Gets metadata for all the documents attached to an entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          owner_type (str): the type of the owner of the document
          offset (int): pagination, index to start searching
          limit (int): pagination, number of elements to retrieve
          paginationDetails (str ON/OFF): ask for details on pagination
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_loanaccount_getSchedule(self, loanid):
        """Retrieves the installments schedule

        Args:
          loanid (str): the id or encoded key of the loan account
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_get_customfield(self, customfieldid):
        """Retrieves a Custom Field.

        Args:
          customfieldid (str): the id or encoded key of the custom field
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_get_comments(self, owner_id, owner_type):
        """Retrieves the comments of entity with owner_id.

        Args:
          owner_id (str): the id or encoded key of the owner
          owner_type (str): the type of the entity owning the comments
        """
        raise NotImplementedError


class MambuConnectorWriter(ABC):
    """Interface for Writers.

    A Reader supports the followint operations:

    - update (updates an entity)
    - create (creates an entity)
    - patch (patches an entity)
    - upload_document (gets a single entity)
    - delete_document (gets several entities, filtering allowed)
    """

    @abstractmethod
    def mambu_update(self, entid, prefix, attrs):
        """updates a mambu entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          prefix (str): entity's URL prefix
          attrs (dict): entity to be updated, complying with Mambu's schemas
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_create(self, prefix, attrs):
        """creates a mambu entity

        Args:
          prefix (str): entity's URL prefix
          attrs (dict): entity to be created, complying with Mambu's schemas
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_patch(self, entid, prefix, fields):
        """patches certain parts of a mambu entity"""
        raise NotImplementedError

    @abstractmethod
    def mambu_upload_document(self, owner_type, entid, filename, name, notes):
        """uploads an attachment to this entity

        Args:
          owner_type (str): the type of the owner of the document
          entid (str): the id or encoded key of the entity owning the document
          filename (str): path and filename of file to upload as attachment
          name (str): name to assign to the attached file in Mambu
          notes (str): notes to associate to the attached file in Mambu
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_delete_document(self, documentId):
        """deletes an attachment by its documentId

        Args:
          documentId (str): the id or encodedkey of the document to be deleted
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_change_state(self, entid, prefix, action, notes):
        """change state of mambu entity

        Args:
          entid (str): the id or encoded key of the entity owning the document
          prefix (str): entity's URL prefix
          action (str): specify the action state
          notes (str): notes to associate to the change of status
        """
        raise NotImplementedError

    @abstractmethod
    def mambu_comment(self, owner_id, owner_type, text):
        """Comments an entity with owner_id.

        Args:
          owner_id (str): the id or encoded key of the owner
          owner_type (str): the type of the entity owning the comments
          text (str): the text of the comment
        """
        raise NotImplementedError
