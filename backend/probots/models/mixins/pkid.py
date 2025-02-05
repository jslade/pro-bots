from typing import Optional, Self

from ...db import DB


class PKId:
    """Models including this mixin must declare an `id` column"""

    id = DB.Column(DB.Integer, primary_key=True)

    @classmethod
    def with_id(cls, id: int) -> Optional[Self]:
        return cls.query.get(id)

    # This method should generate a unique key tuple for any PKId object
    def _key(self):
        return (f"{type(self).__module__}.{type(self).__name__}", self.id)

    # This method allows you to use PKId objects ask keys in dictionaries and
    # in sets safely.
    def __hash__(self):
        return hash(self._key())
