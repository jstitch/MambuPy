"""Helpers for the REST connector.

.. autosummary::
   :nosignatures:
   :toctree: _autosummary
"""

import datetime
import enum
import json
from decimal import Decimal

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class _MambuJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles Python types not natively serializable by json.dumps."""

    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _configure_retry_strategy(session, retries=5):
    """Configure retry strategy for a session.

    El HTTPAdapter se construye con pool_maxsize=50 para que los flujos
    que despachan multiples requests concurrentes contra Mambu (p.ej.
    fan-out de aprobaciones, cargar_datos paralelo) no queden encolados
    sobre el default de urllib3 de 10 conexiones por host.

    Args:
        session (requests.Session): The session to configure
        retries (int, optional): Number of retries. Defaults to 5.
    """
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1,
        allowed_methods=[
            "HEAD",
            "GET",
            "OPTIONS",
            "POST",
            "PUT",
            "DELETE",
            "TRACE",
            "PATCH",
        ],
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=50,
        pool_maxsize=50,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
