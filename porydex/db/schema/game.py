import sqlalchemy as sa

from ..core import TableBase


class Generation(TableBase):
    """One iteration of the Pokémon series.

    For example, the original 151 Pokémon and the games Red, Blue, and Yellow
    all belong to Generation I.  The next 100 Pokémon and Gold, Silver, and
    Crystal belong to Generation II, and so on.
    """

    __tablename__ = 'generations'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

class Game(TableBase):
    """One of the main-series Pokémon games."""

    __tablename__ = 'games'
    __table_args__ = (sa.UniqueConstraint('id', 'generation_id'),)

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              nullable=False)
