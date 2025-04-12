import enum
import fractions

import sqlalchemy as sa
import sqlalchemy.orm

from ..core import TableBase
from .language import ByLanguage
from .pokemon import pokemon_form_key, pokemon_instance_key


class Type(TableBase, ByLanguage):
    """One of the eighteen elemental types (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    _by_language_class_name = 'TypeName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

    pokemon_instances = sa.orm.relationship(
        'PokemonInstance',
        secondary='pokemon_types',
        backref=sa.orm.backref('types', order_by='PokemonType.slot')
    )

class TypeName(TableBase):
    """A type's name in a particular language."""

    __tablename__ = 'type_names'

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'),
                        primary_key=True)
    name = sa.Column(sa.Text, nullable=False)

class PokemonType(TableBase):
    """One of a Pokémon form's types in a particular game."""

    __tablename__ = 'pokemon_types'

    game_id = sa.Column(
        sa.Integer, sa.ForeignKey('games.id'), primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    slot = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'))

    __table_args__ = (
        pokemon_form_key(),
        pokemon_instance_key(),
        sa.ForeignKeyConstraint(
            ['game_id', 'type_id'],
            ['type_instances.game_id', 'type_instances.type_id']
        )
    )

class TypeInstance(TableBase):
    """A type as it appears in a particular game."""

    __tablename__ = 'type_instances'

    game_id = sa.Column(sa.Integer, sa.ForeignKey('games.id'),
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
    single game.
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
