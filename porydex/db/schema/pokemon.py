import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.orm

from ..core import TableBase
from ..util import ExistsByGeneration, attr_ordereddict_collection


# Convenience functions for common foreign keys
def pokemon_form_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    pokemon_forms.
    """

    return sa.ForeignKeyConstraint(
        ['pokemon_id', 'form_id'],
        ['pokemon_forms.pokemon_id', 'pokemon_forms.form_id']
    )

def generation_pokemon_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    generation_pokemon.
    """

    return sa.ForeignKeyConstraint(
        ['generation_id', 'pokemon_id'],
        ['generation_pokemon.generation_id',
         'generation_pokemon.pokemon_id']
    )

def generation_pokemon_form_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    generation_pokemon_forms.
    """

    return sa.ForeignKeyConstraint(
        ['generation_id', 'pokemon_id', 'form_id'],
        ['generation_pokemon_forms.generation_id',
         'generation_pokemon_forms.pokemon_id',
         'generation_pokemon_forms.form_id']
    )


class Pokemon(TableBase, ExistsByGeneration):
    """One of the 721 (as of Generation VI) species of Pokémon."""

    __tablename__ = 'pokemon'

    _by_generation_class_name = 'GenerationPokemon'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    preevolution_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'))
    order = sa.Column(sa.Integer, unique=True, nullable=False)

class PokemonForm(TableBase, ExistsByGeneration):
    """A specific form of a Pokémon, e.g. Sky Shaymin.

    Pokémon that don't have multiple forms still have a row in this table for
    their single form.
    """

    __tablename__ = 'pokemon_forms'

    _by_generation_class_name = 'GenerationPokemonForm'

    pokemon_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'),
                           primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    is_default = sa.Column(sa.Boolean, nullable=False)
    order = sa.Column(sa.Integer, unique=True, nullable=False)

    _current_gpf = sa.orm.relationship(
        'GenerationPokemonForm',
        uselist=False,
        primaryjoin="""and_(
            PokemonForm.pokemon_id == GenerationPokemonForm.pokemon_id,
            PokemonForm.form_id == GenerationPokemonForm.form_id,
            PokemonForm._current_generation_id ==
                GenerationPokemonForm.generation_id
        )"""
    )

    types = association_proxy('_current_gpf', 'types')
    all_types = association_proxy('_by_generation', 'types')

    @hybrid_property
    def _current_generation_id(self):
        """The session's current generation id; or, if none, the latest
        generation this Pokémon form was in.
        """

        generation_id = sa.orm.session.object_session(self).generation_id

        if generation_id is not None:
            return generation_id
        else:
            return max(self._generation_pokemon_forms)

    @_current_generation_id.expression
    def _current_generation_id(class_):
        """The corresponding SQLA expression for _current_generation_id."""

        session_gen = sa.bindparam('session_generation_id')

        latest_gen = (
            sa.select([sa.func.max('generation_pokemon_forms.generation_id')])
            .where('generation_pokemon_forms.pokemon_id == '
                   'pokemon_forms.pokemon_id')
            .where('generation_pokemon_forms.form_id == pokemon_forms')
        )

        return sa.func.coalesce(session_gen, latest_gen.as_scalar())

class GenerationPokemon(TableBase):
    """A generation that a Pokémon appears in."""

    __tablename__ = 'generation_pokemon'

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    pokemon_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'),
                           primary_key=True)

class GenerationPokemonForm(TableBase):
    """A generation that a Pokémon form appears in."""

    __tablename__ = 'generation_pokemon_forms'
    __table_args__ = (pokemon_form_key(), generation_pokemon_key())

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)

    types = sa.orm.relationship('Type', secondary='pokemon_types',
                                order_by='PokemonType.slot')

class GamePokemonForm(TableBase):
    """A game that a Pokémon form appears in."""

    __tablename__ = 'game_pokemon_forms'
    __tableargs__ = (
        generation_pokemon_form_key(),
        sa.ForeignKeyConstraint(
            ['game_id', 'generation_id'],
            ['games.id', 'games.generation_id']
        )
    )

    game_id = sa.Column(sa.Integer, sa.ForeignKey('games.id'), primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              nullable=False)

    # Temporarily nullable
    ingame_internal_id = sa.Column(sa.Integer, nullable=True)
