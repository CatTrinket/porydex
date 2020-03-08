import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy

from ..core import TableBase
from ..util import attr_ordereddict_collection


ENGLISH_ID = 3


class Language(TableBase):
    """A language that the Pokémon games are localized in.

    Some of these also represent a specific script (Japanese in kana vs kanji,
    traditional vs simplified Chinese); the IETF tag will reflect this.
    """

    __tablename__ = 'languages'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Text, unique=True, nullable=False)
    ietf_tag = sa.Column(sa.Text, unique=True, nullable=False)

class ByLanguage():
    """A mixin class to add name-related relationships to anything with a
    separate table of names in different languages.
    """

    #_by_language_class_name = None

    names = association_proxy('_names', 'name')

    @sa.ext.declarative.declared_attr
    def _names(self):
        """A relationship to this item's name in all languages."""

        # XXX The key should ideally be something nicer than just an id
        return sa.orm.relationship(
            self._by_language_class_name,
            collection_class=attr_ordereddict_collection('language_id'),
            order_by='{0}.language_id'.format(self._by_language_class_name),
            lazy='selectin'
        )

    @property
    def name(self):
        """This item's name in the default language (currently hardcoded as
        English).
        """

        # XXX This should be an actual relationship
        return self.names.get(ENGLISH_ID)
