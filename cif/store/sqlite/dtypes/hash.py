import sqlalchemy as sa
from sqlalchemy_utils.operators import CaseInsensitiveComparator


class HASHType(sa.types.TypeDecorator):
    impl = sa.Unicode
    comparator_factory = CaseInsensitiveComparator

    def get_col_spec(self, **kw):
        return "HASH"

    def __init__(self, length=256, *args, **kwargs):
        super(HASHType, self).__init__(length=length, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.lower()
        return value

    @property
    def python_type(self):
        return self.impl.type.python_type
