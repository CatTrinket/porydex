import sqlalchemy as sa

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
