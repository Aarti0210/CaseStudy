"""JWT helper utilities and wrappers.

Provides a drop-in replacement for ``get_jwt_identity`` that
transparently deserializes JSON-encoded identities so that callers can
continue to treat the value as a dict.  This allows the application to
store structured data in the token while satisfying PyJWT's requirement
that the ``sub`` (subject) claim be a string.

Other helper helpers could live here in the future (e.g. helpers for
additional claims).
"""

import json
from flask_jwt_extended import get_jwt_identity as _get_jwt_identity


def get_jwt_identity():
    """Return the current token identity, parsing JSON strings.

    The underlying Flask-JWT-Extended call stores whatever object is
    passed to ``create_access_token`` in the ``sub`` claim.  When the
    identity is a dictionary we ``json.dumps`` it before encoding the
    token so that PyJWT is happy (it insists ``sub`` be a string).  This
    helper reverses that transformation so that callers always receive a
    dict as they expect.

    Returns:
        The identity value from the token, typically a ``dict``.
    """
    identity = _get_jwt_identity()
    if isinstance(identity, str):
        try:
            return json.loads(identity)
        except ValueError:
            # not JSON, just return the raw string
            return identity
    return identity
