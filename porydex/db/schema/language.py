import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import mapped_collection

from ..core import TableBase


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

    # XXX Why did I comment this out
    #_by_language_class_name = None

    names = association_proxy('_names', 'name')

    @sa.ext.declarative.declared_attr
    def _names(cls):
        """A relationship to this item's name in all languages."""

        # XXX The key should ideally be something nicer than just an id
        return sa.orm.relationship(
            cls._by_language_class_name,
            collection_class=mapped_collection(lambda row: row.language_id),
            order_by='{0}.language_id'.format(cls._by_language_class_name),
            lazy='selectin'
        )

    @property
    def name(self):
        """This item's name in the default language (currently hardcoded as
        English).
        """

        # XXX This should be an actual relationship
        return self.names.get(ENGLISH_ID)
