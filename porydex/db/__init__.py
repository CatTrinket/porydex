from collections import OrderedDict
from operator import attrgetter

from sqlalchemy import (
    Column, ForeignKey, ForeignKeyConstraint, UniqueConstraint, bindparam,
    create_engine, func, select)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm.collections import MappedCollection
from sqlalchemy.orm.query import Query
from sqlalchemy.types import Boolean, Integer, Unicode


TableBase = declarative_base()

class PorydexQuery(Query):
    """A query that automatically sets a session_generation_id parameter before
    executing.
    """

    def __iter__(self):
        if 'session_generation_id' not in self._params:
            q = self.params(
                session_generation_id=self.session.generation_id)
            return q.__iter__()
        else:
            return super().__iter__()


class PorydexSession(Session):
    """A session that can keep track of a generation id."""

    def __init__(self, *args, generation_id=None, query_cls=PorydexQuery,
                 **kwargs):
        super().__init__(*args, query_cls=query_cls, **kwargs)
        self.generation_id = generation_id

    @property
    def generation_id(self):
        return self._generation_id

    @generation_id.setter
    def generation_id(self, generation_id):
        """Set the generation id, fetch the corresponding generation, and
        expire all objects currently in the session so that their relationships
        will use the new generation id.
        """

        self.expire_all()

        if generation_id is None:
            generation = None
        else:
            generation = self.query(Generation).get(generation_id)

            if generation is None:
                raise ValueError('Invalid generation id')

        self._generation_id = generation_id
        self.generation = generation


def connect(uri):
    """Connect to the db and return a session."""

    return PorydexSession(bind=create_engine(uri))

def attr_ordereddict_collection(attr_name):
    """Return a new mapped collection class using the given attribute as the
    key.
    """

    class _Collection(OrderedDict, MappedCollection):
        def __init__(self, *args, **kwargs):
            MappedCollection.__init__(self, keyfunc=attrgetter(attr_name))
            OrderedDict.__init__(self, *args, **kwargs)

    return _Collection


### Convenience functions for common multi-column foreign keys

def pokemon_form_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    pokemon_forms.
    """

    return ForeignKeyConstraint(
        ['pokemon_id', 'form_id'],
        ['pokemon_forms.pokemon_id', 'pokemon_forms.form_id']
    )

def generation_pokemon_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    generation_pokemon.
    """

    return ForeignKeyConstraint(
        ['generation_id', 'pokemon_id'],
        ['generation_pokemon.generation_id',
         'generation_pokemon.pokemon_id']
    )

def generation_pokemon_form_key():
    """Return a new ForeignKeyConstraint describing a composite key to
    generation_pokemon_forms.
    """

    return ForeignKeyConstraint(
        ['generation_id', 'pokemon_id', 'form_id'],
        ['generation_pokemon_forms.generation_id',
         'generation_pokemon_forms.pokemon_id',
         'generation_pokemon_forms.form_id']
    )


### Tables

class Ability(TableBase):
    """An ability (e.g. Overgrow, Blaze, Torrent)."""

    __tablename__ = 'abilities'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)

class Game(TableBase):
    """One of the main-series Pokémon games."""

    __tablename__ = 'games'
    __tableargs__ = (UniqueConstraint('id', 'generation_id'),)

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    generation_id = Column(Integer, ForeignKey('generations.id'),
                           nullable=False)

class GamePokemonForm(TableBase):
    """A game that a Pokémon form appears in."""

    __tablename__ = 'game_pokemon_forms'
    __tableargs__ = (
        generation_pokemon_form_key(),
        ForeignKeyConstraint(
            ['game_id', 'generation_id'],
            ['games.id', 'games.generation_id']
        )
    )

    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    pokemon_id = Column(Integer, primary_key=True, autoincrement=False)
    form_id = Column(Integer, primary_key=True, autoincrement=False)
    generation_id = Column(Integer, ForeignKey('generations.id'),
                           nullable=False)
    ingame_internal_id = Column(Integer, nullable=True)  # Temporarily nullable

class Generation(TableBase):
    """One iteration of the Pokémon series.

    For example, the original 151 Pokémon and the games Red, Blue, and Yellow
    all belong to Generation I.  The next 100 Pokémon and Gold, Silver, and
    Crystal belong to Generation II, and so on.
    """

    __tablename__ = 'generations'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)

class GenerationPokemon(TableBase):
    """A generation that a Pokémon appears in."""

    __tablename__ = 'generation_pokemon'

    generation_id = Column(Integer, ForeignKey('generations.id'),
                           primary_key=True)
    pokemon_id = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)

class GenerationPokemonForm(TableBase):
    """A generation that a Pokémon form appears in."""

    __tablename__ = 'generation_pokemon_forms'
    __table_args__ = (pokemon_form_key(), generation_pokemon_key())

    generation_id = Column(Integer, ForeignKey('generations.id'),
                           primary_key=True)
    pokemon_id = Column(Integer, primary_key=True, autoincrement=False)
    form_id = Column(Integer, primary_key=True, autoincrement=False)

    types = relationship('Type', secondary='pokemon_types',
                         order_by='PokemonType.slot')

class Move(TableBase):
    """A move (e.g. Tackle, Growl)."""

    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)

class Pokemon(TableBase):
    """One of the 721 (as of Generation VI) species of Pokémon."""

    __tablename__ = 'pokemon'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    preevolution_id = Column(Integer, ForeignKey('pokemon.id'))
    order = Column(Integer, unique=True, nullable=False)

class PokemonForm(TableBase):
    """A specific form of a Pokémon, e.g. Sky Shaymin.

    Pokémon that don't have multiple forms still have a row in this table for
    their single form.
    """

    __tablename__ = 'pokemon_forms'

    pokemon_id = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    form_id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    is_default = Column(Boolean, nullable=False)
    order = Column(Integer, unique=True, nullable=False)

    _generation_pokemon_forms = relationship(
        'GenerationPokemonForm',
        collection_class=attr_ordereddict_collection('generation_id'),
        order_by='GenerationPokemonForm.generation_id'
    )

    _current_gpf = relationship(
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
    all_types = association_proxy('_generation_pokemon_forms', 'types')

    @hybrid_property
    def _current_generation_id(self):
        """The session's current generation id; or, if none, the latest
        generation this Pokémon form was in.
        """

        generation_id = object_session(self).generation_id

        if generation_id is not None:
            return generation_id
        else:
            return max(self._generation_pokemon_forms)

    @_current_generation_id.expression
    def _current_generation_id(class_):
        """The corresponding SQLA expression for _current_generation_id."""

        session_gen = bindparam('session_generation_id')

        latest_gen = (
            select([func.max(GenerationPokemonForm.generation_id)])
            .where(GenerationPokemonForm.pokemon_id == class_.pokemon_id)
            .where(GenerationPokemonForm.form_id == class_.form_id)
        )

        return func.coalesce(session_gen, latest_gen.as_scalar());

class PokemonType(TableBase):
    """One of a Pokémon form's types in a particular generation."""

    __tablename__ = 'pokemon_types'
    __table_args__ = (pokemon_form_key(), generation_pokemon_form_key())

    generation_id = Column(Integer, ForeignKey('generations.id'),
                           primary_key=True)
    pokemon_id = Column(Integer, primary_key=True, autoincrement=False)
    form_id = Column(Integer, primary_key=True, autoincrement=False)
    slot = Column(Integer, primary_key=True, autoincrement=False)
    type_id = Column(Integer, ForeignKey('types.id'))

class Type(TableBase):
    """One of the eighteen elemental types (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
