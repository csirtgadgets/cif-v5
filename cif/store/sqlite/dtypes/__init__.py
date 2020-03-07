from sqlalchemy.types import UserDefinedType, BINARY


class IOCType(UserDefinedType):

    impl = BINARY(16)

    def bind_processor(self, dialect):

        DBAPIBinary = dialect.dbapi.Binary

        def process(value):
            if type(value) == str:
                value = value.encode('utf-8')
            return DBAPIBinary(value)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process

    @property
    def python_type(self):
        return self.impl.type.python_type