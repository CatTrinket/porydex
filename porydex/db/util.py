from collections import OrderedDict
from operator import attrgetter

from sqlalchemy.orm.collections import MappedCollection


def attr_ordereddict_collection(attr_name):
    """Return a new mapped collection class using the given attribute as the
    key.
    """

    class _Collection(OrderedDict, MappedCollection):
        def __init__(self, *args, **kwargs):
            MappedCollection.__init__(self, keyfunc=attrgetter(attr_name))
            OrderedDict.__init__(self, *args, **kwargs)

    return _Collection
