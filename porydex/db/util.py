from collections import OrderedDict
from operator import attrgetter

import sqlalchemy as sa
import sqlalchemy.ext.hybrid
from sqlalchemy.orm.collections import MappedCollection


class ExistsByGeneration():
    """A mixin class for a table with a many-to-many relationship with
    generations.
    """

    _by_generation_class_name = None

    @sa.ext.declarative.declared_attr
    def _by_generation(self):
        """Add a relationship to the generation junction table class."""

        return sa.orm.relationship(
            self._by_generation_class_name,
            collection_class=attr_ordereddict_collection('generation_id'),
            order_by='{0}.generation_id'.format(self._by_generation_class_name)
        )

    @sa.ext.hybrid.hybrid_method
    def in_current_gen(self):
        """Determine whether this item exists in the session's currently-set
        generation.
        """

        session = sa.orm.object_session(self)
        gen_id = session.generation_id

        return gen_id is None or gen_id in self._by_generation

    @in_current_gen.expression
    def in_current_gen(class_):
        """Return the corresponding SQLA expression for in_current_gen."""

        gen_id = sa.bindparam('session_generation_id')

        return sa.or_(
            gen_id.is_(None),
            class_._by_generation.any(generation_id=gen_id)
        )

def attr_ordereddict_collection(attr_name):
    """Return a new mapped collection class using the given attribute as the
    key.
    """

    class _Collection(OrderedDict, MappedCollection):
        def __init__(self, *args, **kwargs):
            MappedCollection.__init__(self, keyfunc=attrgetter(attr_name))
            OrderedDict.__init__(self, *args, **kwargs)

    return _Collection
