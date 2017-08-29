import sqlalchemy as sa

from .language import ByLanguage
from ..core import TableBase
from ..util import ExistsByGeneration


class Ability(TableBase, ExistsByGeneration, ByLanguage):
    """An ability (e.g. Overgrow, Blaze, Torrent)."""

    __tablename__ = 'abilities'
    _by_generation_class_name = 'GenerationAbility'
    _by_language_class_name = 'AbilityName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

class AbilityName(TableBase):
    """An ability's name in a particular language."""

    __tablename__ = 'ability_names'

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    ability_id = sa.Column(sa.Integer, sa.ForeignKey('abilities.id'),
                           primary_key=True)
    name = sa.Column(sa.Text, nullable=False)

class GenerationAbility(TableBase):
    """A generation that an ability appears in."""

    __tablename__ = 'generation_abilities'

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    ability_id = sa.Column(sa.Integer, sa.ForeignKey('abilities.id'),
                           primary_key=True)
