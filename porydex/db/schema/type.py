import sqlalchemy as sa

from ..core import TableBase
from .pokemon import pokemon_form_key, generation_pokemon_form_key


class Type(TableBase):
    """One of the eighteen elemental types (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

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
