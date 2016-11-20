import sqlalchemy as sa
import sqlalchemy.orm

from ..core import TableBase
from ..util import attr_ordereddict_collection
from .pokemon import pokemon_form_key, generation_pokemon_form_key


class Type(TableBase):
    """One of the eighteen elemental types (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

    _by_generation = sa.orm.relationship(
        'GenerationType',
        collection_class=attr_ordereddict_collection('generation_id'),
        order_by='GenerationType.generation_id'
    )

class PokemonType(TableBase):
    """One of a Pokémon form's types in a particular generation."""

    __tablename__ = 'pokemon_types'
    __table_args__ = (pokemon_form_key(), generation_pokemon_form_key())

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    slot = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'))

class GenerationType(TableBase):
    """A generation that a type appears in."""

    __tablename__ = 'generation_types'

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    type_id = sa.Column(sa.Integer, sa.ForeignKey('types.id'),
                        primary_key=True)
