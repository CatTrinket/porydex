import enum

import sqlalchemy as sa

from .game import Game
from .language import ByLanguage
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
