import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.orm

from .game import Generation
from .language import ENGLISH_ID, ByLanguage
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

def game_pokemon_form_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    game_pokemon_forms.
    """

    return sa.ForeignKeyConstraint(
        ['game_id', 'pokemon_id', 'form_id'],
        ['game_pokemon_forms.game_id',
         'game_pokemon_forms.pokemon_id',
         'game_pokemon_forms.form_id']
    )



class Pokemon(TableBase, ExistsByGeneration, ByLanguage):
    """One of the 802 (as of Generation 7) species of Pokémon."""

    __tablename__ = 'pokemon'

    _by_generation_class_name = 'GenerationPokemon'
    _by_language_class_name = 'PokemonName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    preevolution_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'))
    order = sa.Column(sa.Integer, unique=True, nullable=False)

class PokemonName(TableBase):
    """A Pokémon's name in a particular language."""

    __tablename__ = 'pokemon_names'

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    pokemon_id = sa.Column(sa.Integer, sa.ForeignKey('pokemon.id'),
                           primary_key=True)
    name = sa.Column(sa.Text, nullable=False)

class PokemonForm(TableBase, ExistsByGeneration, ByLanguage):
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
    types = association_proxy('_current_gpf', 'types')
    all_types = association_proxy('_by_generation', 'types')
    pokemon_abilities = association_proxy('_current_gpf', 'pokemon_abilities')
    all_pokemon_abilities = association_proxy(
        '_by_generation', 'pokemon_abilities')
    stats = association_proxy('_current_gpf', 'stats')

    _current_gpf = sa.orm.relationship(
        'GenerationPokemonForm',
        uselist=False,
        primaryjoin="""and_(
            PokemonForm.pokemon_id == GenerationPokemonForm.pokemon_id,
            PokemonForm.form_id == GenerationPokemonForm.form_id,
            PokemonForm._current_generation_id ==
                GenerationPokemonForm.generation_id
        )""",
        lazy='joined'
    )

    @hybrid_property
    def _current_generation_id(self):
        """The session's current generation id; or, if none, the latest
        generation this Pokémon form was in.

        Let's Go never counts as the latest generation unless this Pokémon form
        has only appeared in Let's Go.
        """

        generation_id = sa.orm.session.object_session(self).generation_id

        if generation_id is not None:
            return generation_id
        else:
            generation = max(
                (gpf.generation for gpf in self._by_generation.values()),
                key=lambda gen: (gen.is_base_series, gen.release_order)
            )
            return generation.id

    @_current_generation_id.expression
    def _current_generation_id(class_):
        """The corresponding SQLA expression for _current_generation_id."""

        session_gen = sa.bindparam('session_generation_id')

        latest_gen = (
            sa.select([Generation.id])
            .select_from(sa.join(
                Generation,
                GenerationPokemonForm,
                Generation.id == GenerationPokemonForm.generation_id
            ))
            .where(GenerationPokemonForm.pokemon_id == class_.pokemon_id)
            .where(GenerationPokemonForm.form_id == class_.form_id)
            .order_by(
                Generation.is_base_series.desc(),
                Generation.release_order.desc()
            )
            .limit(1)
        )

        return sa.func.coalesce(session_gen, latest_gen.as_scalar())

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

    types = sa.orm.relationship(
        'Type', secondary='pokemon_types', order_by='PokemonType.slot',
        lazy='selectin')

class GamePokemonForm(TableBase):
    """A game that a Pokémon form appears in."""

    __tablename__ = 'game_pokemon_forms'
    __table_args__ = (
        generation_pokemon_form_key(),
        sa.ForeignKeyConstraint(
            ['game_id', 'generation_id'],
            ['games.id', 'games.generation_id']
        )
    )

    game_id = sa.Column(sa.Integer, sa.ForeignKey('games.id'),
                        primary_key=True)
    pokemon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    form_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              nullable=False)

    # Temporarily nullable
    ingame_internal_id = sa.Column(sa.Integer, nullable=True)
