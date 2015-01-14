from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Boolean, Integer, Unicode


DBSession = sessionmaker()
TableBase = declarative_base()

def connect(uri):
    """Connect to the db and return a session."""

    engine = create_engine(uri)
    DBSession.configure(bind=engine)
    return DBSession()


### Tables

class Ability(TableBase):
    """An ability (e.g. Overgrow, Blaze, Torrent)."""

    __tablename__ = 'abilities'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)

class Game(TableBase):
    """One of the main-series Pokémon games."""

    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    generation_id = Column(Integer, ForeignKey('generations.id'),
                           nullable=False)

class Generation(TableBase):
    """One iteration of the Pokémon series.

    For example, the original 151 Pokémon and the games Red, Blue, and Yellow
    all belong to Generation I.  The next 100 Pokémon and Gold, Silver, and
    Crystal belong to Generation II, and so on.
    """

    __tablename__ = 'generations'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)

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
    """A specific form of a Pokémon.

    Pokémon that don't have multiple forms still have a row in this table for
    their single form.
    """

    __tablename__ = 'pokemon_forms'

    pokemon_id = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    form_id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    is_default = Column(Boolean, nullable=False)
    order = Column(Integer, unique=True, nullable=False)

class Type(TableBase):
    """One of the eighteen elemental types (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
