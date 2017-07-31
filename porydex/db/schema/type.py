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
    __table_args__ = (
        pokemon_form_key(),
        generation_pokemon_form_key(),
        sa.ForeignKeyConstraint(
            ['generation_id', 'type_id'],
            ['generation_types.generation_id', 'generation_types.type_id']
        )
    )

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

    pokemon = sa.orm.relationship('PokemonForm', secondary='pokemon_types',
                                  order_by='PokemonForm.order')
