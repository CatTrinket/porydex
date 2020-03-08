import sqlalchemy as sa
import sqlalchemy.orm

from porydex.db.schema.game import Generation
from porydex.db.schema.language import ByLanguage, Language
from porydex.db.schema.pokemon import (
    GenerationPokemonForm, Pokemon, generation_pokemon_form_key,
    pokemon_form_key)
from porydex.db.core import TableBase


class Stat(TableBase, ByLanguage):
    """One of the stats that Pokémon have (HP, Attack, etc.)

    This includes the main six status, RBY's Special stat, Accuracy, and
    Evasion.
    """

    __tablename__ = 'stats'

    _by_language_class_name = 'StatName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    is_transient = sa.Column(
        sa.Boolean, nullable=False,
        doc="""True for Accuracy and Evasion, which only exist in battle and
        have no actual stat values."""
    )

class StatName(TableBase):
    """A stat's name in a particular language."""

    __tablename__ = 'stat_names'

    language_id = sa.Column(sa.ForeignKey(Language.id), primary_key=True)
    stat_id = sa.Column(sa.ForeignKey(Stat.id), primary_key=True)
    name = sa.Column(sa.Unicode, nullable=False)
    abbreviation = sa.Column(
        sa.Unicode, nullable=False,
        doc="""A three-letter (or less) abbreviation for this stat's name."""
    )

class PokemonStat(TableBase):
    __tablename__ = 'pokemon_stats'
    __table_args__ = (pokemon_form_key(), generation_pokemon_form_key())

    generation_id = sa.Column(sa.ForeignKey(Generation.id), primary_key=True)
    pokemon_id = sa.Column(sa.ForeignKey(Pokemon.id), primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    stat_id = sa.Column(sa.ForeignKey(Stat.id), primary_key=True)
    base_stat = sa.Column(
        sa.Integer, nullable=False,
        doc="""The base value plugged into the stat formula that determines the
        range this stat can have for all Pokémon of this species + form."""
    )
    effort_yield = sa.Column(
        sa.Integer,
        doc="""The number of effort points this Pokémon yields upon being
        knocked out.  Null for all stats in Gen 1-2, which use a different
        system.  Never null in Gen 3 and up; an actual 0 is used if applicable.
        (The only exception, for the time being, is Deoxys in Gen 3; all
        non-Normal Formes' effort yield is null until I figure out how that
        works.)"""
    )

    _generation_pokemon_form = sa.orm.relationship(
        GenerationPokemonForm,
        backref=sa.orm.backref('stats', order_by=stat_id, lazy='selectin')
    )
    stat = sa.orm.relationship(Stat, lazy='joined')
