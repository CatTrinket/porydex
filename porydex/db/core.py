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

class PorydexQuery(sa.orm.Query):
    """A query that automatically sets a session_generation_id parameter before
    executing.
    """

    def __iter__(self):
        if 'session_generation_id' not in self._params:
            q = self.params(
                session_generation_id=self.session.generation_id)
            return q.__iter__()
        else:
            return super().__iter__()

class PorydexSession(sa.orm.Session):
    """A session that can keep track of a generation id."""

    def __init__(self, *args, generation_id=None, query_cls=PorydexQuery,
                 **kwargs):
        super().__init__(*args, query_cls=query_cls, **kwargs)
        self.generation_id = generation_id

    @property
    def generation_id(self):
        return self._generation_id

    @generation_id.setter
    def generation_id(self, generation_id):
        """Set the generation id, fetch the corresponding generation, and
        expire all objects currently in the session so that their relationships
        will use the new generation id.
        """

        self.expire_all()

        if generation_id is None:
            generation = None
        else:
            generation_table = TableBase.metadata.tables['generations']
            query = self.query(generation_table).filter_by(id=generation_id)

            try:
                generation = query.one()
            except sa.orm.exc.NoResultFound:
                raise ValueError('Invalid generation id')

        self._generation_id = generation_id
        self.generation = generation


def connect(uri):
    """Connect to the db and return a session."""

    return PorydexSession(bind=sa.create_engine(uri))
