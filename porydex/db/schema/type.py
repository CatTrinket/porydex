import enum
import fractions

import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
import sqlalchemy.orm

from ..core import TableBase
from ..util import ExistsByGeneration
from .language import ByLanguage
from .pokemon import pokemon_form_key, generation_pokemon_form_key


class Type(TableBase, ExistsByGeneration, ByLanguage):
    """One of the eighteen elemental types (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    _by_generation_class_name = 'GenerationType'
    _by_language_class_name = 'TypeName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

    pokemon = association_proxy('_by_generation', 'pokemon')

class TypeName(TableBase):
    """A Pokémon's name in a particular language."""

    __tablename__ = 'type_names'

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'),
                        primary_key=True)
    name = sa.Column(sa.Text, nullable=False)

class PokemonType(TableBase):
    """One of a Pokémon form's types in a particular generation."""

    __tablename__ = 'pokemon_types'

    generation_id = sa.Column(
        sa.Integer, sa.ForeignKey('generations.id'), primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    slot = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'))

    pokemon = sa.orm.relationship('PokemonForm', lazy='joined')
    type = sa.orm.relationship('Type', lazy='joined')

    __table_args__ = (
        pokemon_form_key(),
        generation_pokemon_form_key(),
        sa.ForeignKeyConstraint(
            ['generation_id', 'type_id'],
            ['generation_types.generation_id', 'generation_types.type_id']
        )
    )

class GenerationType(TableBase):
    """A generation that a type appears in."""

    __tablename__ = 'generation_types'

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'),
                        primary_key=True)

    pokemon = sa.orm.relationship('PokemonForm', secondary='pokemon_types',
                                  order_by='PokemonForm.order')

class TypeChart(TableBase):
    """One iteration of the type chart, used in one or more generations.

    The Gen 1 type chart, the Gen 2-5 type chart, and the Gen 6+ type chart are
    each one row in this table.  The type_matchups table then lists all the
    matchups for each type chart, rather than listing all of them for every
    single generation.
    """

    __tablename__ = 'type_charts'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

class TypeMatchupResult(enum.Enum):
    """An enum containing the possible damage modifiers that can be the result
    of a type matchup.
    """

    no_effect = fractions.Fraction(0)
    not_very_effective = fractions.Fraction(1, 2)
    neutral = fractions.Fraction(1)
    super_effective = fractions.Fraction(2)

    def __init__(self, damage_multiplier):
        self.damage_multiplier = damage_multiplier

    def __str__(self):
        return self.name

class TypeMatchup(TableBase):
    """The resulting damage modifier when a particular type of move hits a
    particular type of Pokémon.
    """

    __tablename__ = 'type_matchups'

    type_chart_id = sa.Column(sa.ForeignKey(TypeChart.id), primary_key=True)
    attacking_type_id = sa.Column(sa.ForeignKey(Type.id), primary_key=True)
    defending_type_id = sa.Column(sa.ForeignKey(Type.id), primary_key=True)
    result = sa.Column(sa.Enum(TypeMatchupResult), nullable=False)

    attacking_type = sa.orm.relationship(Type, foreign_keys=[attacking_type_id])
    defending_type = sa.orm.relationship(Type, foreign_keys=[defending_type_id])
