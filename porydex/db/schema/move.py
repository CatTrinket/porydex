import sqlalchemy as sa

from ..core import TableBase


class Move(TableBase):
    """A move (e.g. Tackle, Growl)."""

    __tablename__ = 'moves'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
