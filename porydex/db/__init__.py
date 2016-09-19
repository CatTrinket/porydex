from collections import OrderedDict
from operator import attrgetter

from sqlalchemy import (
    Column, ForeignKey, ForeignKeyConstraint, UniqueConstraint, create_engine)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.collections import MappedCollection
from sqlalchemy.types import Boolean, Integer, Unicode


DBSession = sessionmaker()
TableBase = declarative_base()

def connect(uri):
    """Connect to the db and return a session."""

    engine = create_engine(uri)
    DBSession.configure(bind=engine)
    return DBSession()

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
        collection_class=attr_ordereddict_collection('generation_id')
    )

    types = association_proxy('_generation_pokemon_forms', 'types')

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
