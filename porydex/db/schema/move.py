import enum

import sqlalchemy as sa
import sqlalchemy.orm

from .game import Game
from .language import ByLanguage
from .pokemon import (
    Pokemon, PokemonForm, game_pokemon_form_key, pokemon_form_key)
from ..core import TableBase
from ..util import ExistsByGeneration


class Move(TableBase, ExistsByGeneration, ByLanguage):
    """A move (e.g. Tackle, Growl)."""

    __tablename__ = 'moves'
    _by_generation_class_name = 'GenerationMove'
    _by_language_class_name = 'MoveName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)


class MoveName(TableBase):
    """A move's name in a particular language."""

    __tablename__ = 'move_names'

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    move_id = sa.Column(sa.Integer, sa.ForeignKey('moves.id'),
                        primary_key=True)
    name = sa.Column(sa.Text, nullable=False)


class GenerationMove(TableBase):
    """A generation that a move appears in."""

    __tablename__ = 'generation_moves'

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    move_id = sa.Column(sa.Integer, sa.ForeignKey('moves.id'),
                        primary_key=True)


class MoveMachineType(enum.Enum):
    """An enum for the three types of move-teaching machine (TM, HM, TR)."""

    tm = enum.auto()
    hm = enum.auto()
    tr = enum.auto()

    def __str__(self):
        return self.name


class MoveMachine(TableBase):
    """A move taught by a TM/HM/TR in a particular game."""

    __tablename__ = 'move_machines'

    game_id = sa.Column(sa.ForeignKey(Game.id), primary_key=True)
    move_id = sa.Column(sa.ForeignKey(Move.id), primary_key=True)
    machine_type = sa.Column(sa.Enum(MoveMachineType), nullable=False)
    number = sa.Column(sa.Integer, nullable=False)

    __table_args__ = (sa.UniqueConstraint(game_id, machine_type, number),)


class PokemonMoveList(TableBase):
    """A list of moves learned by one or more Pokémon.

    This list may be reused across multiple Pokémon, forms, and games; see
    PokemonMoveListMap.  This saves a ton of space at the cost of making the
    schema a bit more complex.
    """

    __tablename__ = 'pokemon_move_lists'

    id = sa.Column(sa.Integer, primary_key=True)


class PokemonMove(TableBase):
    """One move on a PokemonMoveList."""

    __tablename__ = 'pokemon_moves'

    id = sa.Column(
        sa.Integer, primary_key=True,
        doc="""An arbitrary ID for this row, as this table has no other
        candidate key (since level is nullable).
        """
    )
    pokemon_move_list_id = sa.Column(
        sa.ForeignKey(PokemonMoveList.id), nullable=False)
    move_id = sa.Column(sa.ForeignKey(Move.id), nullable=False)
    level = sa.Column(
        sa.Integer,
        doc="""The level at which this move is learned.  Null if this is not a
        level-up move.
        """
    )
    order_within_level = sa.Column(
        sa.Integer,
        doc="""The order in which this move is learned when multiple moves are
        learned at the same level.  Null if this is not a level-up move.

        The main reason this important is that Pokémon often have their last
        four level-up moves when initially encountered/received/etc., and that
        takes this order into account.
        """
    )
    base_move_id = sa.Column(
        sa.ForeignKey(Move.id),
        doc="""The ID of the move that gets replaced with this move under the
        right conditions.

        Used by the methods z_move and form_base_move.  Null otherwise.
        """
    )

    pokemon_move_list = sa.orm.relationship(
        PokemonMoveList,
        backref=sa.orm.backref('pokemon_moves', order_by=move_id)
    )
    move = sa.orm.relationship(Move, foreign_keys=[move_id])

    __table_args__ = (
        sa.Index(
            'pokemon_moves_unique_index',
            pokemon_move_list_id,
            move_id,
            sa.func.coalesce(level, 0),
            unique=True
        ),
        sa.UniqueConstraint(pokemon_move_list_id, level, order_within_level)
    )


class PokemonMoveMethod(enum.Enum):
    """An enum for the methods by which Pokémon can learn moves."""

    level = enum.auto()
    evolution = enum.auto()
    egg = enum.auto()
    egg_light_ball = enum.auto()
    tutor = enum.auto()
    stadium_surf = enum.auto()
    form_change = enum.auto()
    form_revert = enum.auto()
    form_base_move = enum.auto()
    z_move = enum.auto()  # Species-specific ones only
    partner_power = enum.auto()
    g_max_move = enum.auto()
    machine = enum.auto()

    def __str__(self):
        return self.name

class PokemonMoveListMap(TableBase):
    """A mapping to a move list for a particular Pokémon form, game, and
    method.
    """

    __tablename__ = 'pokemon_move_list_map'

    game_id = sa.Column(sa.ForeignKey(Game.id), primary_key=True)
    pokemon_id = sa.Column(sa.ForeignKey(Pokemon.id), primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    method = sa.Column(sa.Enum(PokemonMoveMethod), primary_key=True)
    pokemon_move_list_id = sa.Column(sa.ForeignKey(PokemonMoveList.id))

    pokemon_move_list = sa.orm.relationship(PokemonMoveList)
    game = sa.orm.relationship(Game)

    __table_args__ = (pokemon_form_key(), game_pokemon_form_key())
