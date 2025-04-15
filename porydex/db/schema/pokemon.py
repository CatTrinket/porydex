import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
import sqlalchemy.orm

from .game import Generation
from .language import ENGLISH_ID, ByLanguage
from ..core import TableBase


# Convenience functions for common foreign keys
def pokemon_form_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    pokemon_forms.
    """

    return sa.ForeignKeyConstraint(
        ['pokemon_id', 'form_id'],
        ['pokemon_forms.pokemon_id', 'pokemon_forms.form_id']
    )

def pokemon_instance_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    pokemon_instances.
    """

    return sa.ForeignKeyConstraint(
        ['game_id', 'pokemon_id', 'form_id'],
        ['pokemon_instances.game_id',
         'pokemon_instances.pokemon_id',
         'pokemon_instances.form_id']
    )


class Pokemon(TableBase, ByLanguage):
    """One of the 802 (as of Generation 7) species of Pokémon."""

    __tablename__ = 'pokemon'

    _by_language_class_name = 'PokemonName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    preevolution_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'))
    order = sa.Column(sa.Integer, unique=True, nullable=False)

class PokemonName(TableBase):
    """A Pokémon's name in a particular language."""

    __tablename__ = 'pokemon_names'

    language_id = sa.Column(
        sa.Integer, sa.ForeignKey('languages.id'), primary_key=True)
    pokemon_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'),
                           primary_key=True)
    name = sa.Column(sa.Text, nullable=False)

class PokemonForm(TableBase, ByLanguage):
    """A specific form of a Pokémon, e.g. Sky Shaymin.

    Pokémon that don't have multiple forms still have a row in this table for
    their single form.
    """

    __tablename__ = 'pokemon_forms'

    _by_generation_class_name = 'GenerationPokemonForm'
    _by_language_class_name = 'PokemonFormName'

    pokemon_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'),
                           primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    is_default = sa.Column(sa.Boolean, nullable=False)
    order = sa.Column(sa.Integer, unique=True, nullable=False)
    height_m = sa.Column(sa.Numeric(4, 1), nullable=False)
    weight_kg = sa.Column(sa.Numeric(4, 1))

    pokemon = sa.orm.relationship('Pokemon', lazy='joined')
    full_names = association_proxy('_names', 'full_name')

    @property
    def full_name(self):
        """The Pokémon form's full name in the current language (currently
        hardcoded as English).
        """

        return self.full_names.get(ENGLISH_ID) or self.pokemon.name

class PokemonFormName(TableBase):
    """A Pokémon form's name in a particular language."""

    __tablename__ = 'pokemon_form_names'
    __table_args__ = (pokemon_form_key(),)

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('form_name', sa.Text, nullable=False)
    full_name = sa.Column(sa.Text, nullable=False)

class PokemonInstance(TableBase):
    """A Pokémon form as it appears in a particular game."""

    __tablename__ = 'pokemon_instances'
    __table_args__ = (pokemon_form_key(),)

    game_id = sa.Column(sa.Integer, sa.ForeignKey('games.id'),
                        primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    is_current = sa.Column(sa.Boolean, nullable=False)

    # Temporarily nullable
    ingame_internal_id = sa.Column(sa.Integer, nullable=True)

    game = sa.orm.relationship('Game')
    pokemon_form = sa.orm.relationship(PokemonForm)
