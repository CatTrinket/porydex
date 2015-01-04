from sqlalchemy import Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Integer, Unicode

DBSession = sessionmaker()
TableBase = declarative_base()

def connect(uri):
    """Connect to the db and return a session."""

    engine = create_engine(uri)
    DBSession.configure(bind=engine)
    return DBSession()

class Pokemon(TableBase):
    """A species of Pokémon."""

    __tablename__ = 'pokemon'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, nullable=False)
