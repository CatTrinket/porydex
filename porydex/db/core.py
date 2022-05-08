import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.declarative


class TableBase(sa.ext.declarative.declarative_base()):
    __abstract__ = True

    def __repr__(self):
        args = []

        for column in sa.orm.object_mapper(self).column_attrs:
            key = column.key
            val = getattr(self, key)

            args.append('{}={}'.format(key, repr(val)))

        return '{type}({args})'.format(
            type=type(self).__name__,
            args=', '.join(args)
        )


def connect(uri, echo=False):
    """Connect to the db and return a session."""

    return sa.orm.Session(bind=sa.create_engine(uri, echo=echo))
