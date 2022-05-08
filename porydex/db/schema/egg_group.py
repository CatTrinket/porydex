import sqlalchemy as sa

from porydex.db.schema.game import Game
from porydex.db.schema.language import ByLanguage, Language
from porydex.db.schema.pokemon import (
    Pokemon, pokemon_form_key, pokemon_instance_key)
from porydex.db.core import TableBase


class EggGroup(TableBase, ByLanguage):
    """A grouping of Pokémon that dictates which Pokémon can breed together."""

    __tablename__ = 'egg_groups'
    _by_language_class_name = 'EggGroupName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

class EggGroupName(TableBase):
    """An egg group's name in a particular language."""

    __tablename__ = 'egg_group_names'

    language_id = sa.Column(sa.ForeignKey(Language.id), primary_key=True)
    egg_group_id = sa.Column(sa.ForeignKey(EggGroup.id), primary_key=True)
    name = sa.Column(
        sa.Unicode, nullable=False,
        doc="""The egg group's name, as it appears in Pokédex 3D Pro.

        The only other game to include names for egg groups was Pokémon Stadium
        2; a handful of them were different, and porydex does not currently
        have those names.
        """
    )
    subtitle = sa.Column(
        sa.Unicode, nullable=True,
        doc="""An unofficial subtitle to better disambiguate Water 1-3."""
    )

class PokemonEggGroup(TableBase):
    """An egg group that a Pokémon form is in in a particular game.

    This is attached to individual forms because Cosplay Pikachu, Ash-Greninja,
    et al. are unable to breed, and are thus in Undiscovered rather than the
    main form's egg groups.

    On the other hand, many forms that only appear in battle, and thus cannot
    technically be bred, are still given the main form's egg groups.  They may
    be left out in the future.
    """

    __tablename__ = 'pokemon_egg_groups'
    __table_args__ = (pokemon_form_key(), pokemon_instance_key())

    game_id = sa.Column(sa.ForeignKey(Game.id), primary_key=True)
    pokemon_id = sa.Column(sa.ForeignKey(Pokemon.id), primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    egg_group_id = sa.Column(sa.ForeignKey(EggGroup.id), primary_key=True)
