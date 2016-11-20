import sqlalchemy as sa

from ..core import TableBase


class Ability(TableBase):
    """An ability (e.g. Overgrow, Blaze, Torrent)."""

    __tablename__ = 'abilities'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
