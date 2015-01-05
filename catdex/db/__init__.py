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
