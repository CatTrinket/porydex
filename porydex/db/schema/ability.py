import enum

import sqlalchemy as sa
import sqlalchemy.orm

from .game import Generation
from .language import ByLanguage
from .pokemon import (
    GenerationPokemonForm,
    Pokemon,
    generation_pokemon_form_key,
    pokemon_form_key
)
from ..core import TableBase
from ..util import ExistsByGeneration


class Ability(TableBase, ExistsByGeneration, ByLanguage):
    """An ability (e.g. Overgrow, Blaze, Torrent)."""

    __tablename__ = 'abilities'
    _by_generation_class_name = 'GenerationAbility'
    _by_language_class_name = 'AbilityName'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)

class AbilityName(TableBase):
    """An ability's name in a particular language."""

    __tablename__ = 'ability_names'

    language_id = sa.Column(sa.Integer, sa.ForeignKey('languages.id'),
                            primary_key=True)
    ability_id = sa.Column(sa.Integer, sa.ForeignKey('abilities.id'),
                           primary_key=True)
    name = sa.Column(sa.Text, nullable=False)

class GenerationAbility(TableBase):
    """A generation that an ability appears in."""

    __tablename__ = 'generation_abilities'

    generation_id = sa.Column(sa.Integer, sa.ForeignKey('generations.id'),
                              primary_key=True)
    ability_id = sa.Column(sa.Integer, sa.ForeignKey('abilities.id'),
                           primary_key=True)

class AbilitySlot(enum.IntEnum):
    """An enum for the slots in which a Pokémon may have a particular ability.

    `ability_1`, `ability_2`, and `hidden_ability` are self-explanatory;
    `unique_ability` is for cases like Greninja's Battle Bond or Zygarde's
    Power Construct.  (Both of these examples are implemented as separate forms
    in the games, but which we don't treat them as separate forms.)

    TODO: this shouldn't be an IntEnum; use auto() once we can drop Python 3.5
    and write a base class or something to add comparison.
    """

    ability_1 = 1
    ability_2 = 2
    hidden_ability = 3
    unique_ability = 4

    def __str__(self):
        return self.name

class PokemonAbility(TableBase):
    """An ability that a Pokémon has.

    There's no unique constraint involving `slot` because Gigantamax Toxtricity
    may have either Plus or Minus as its ability 2 (depending on which form
    transformed into it), and we simply list both in the same slot.
    """

    __tablename__ = 'pokemon_abilities'

    generation_id = sa.Column(sa.ForeignKey(Generation.id), primary_key=True)
    pokemon_id = sa.Column(sa.ForeignKey(Pokemon.id), primary_key=True)
    form_id = sa.Column(sa.Integer, primary_key=True)
    ability_id = sa.Column(sa.ForeignKey(Ability.id), primary_key=True)
    slot = sa.Column(sa.Enum(AbilitySlot))

    __table_args__ = (
        pokemon_form_key(),
        generation_pokemon_form_key(),
        sa.ForeignKeyConstraint(
            [generation_id, ability_id],
            [GenerationAbility.generation_id, GenerationAbility.ability_id]
        )
    )

    _generation_pokemon_form = sa.orm.relationship(
        GenerationPokemonForm,
        backref=sa.orm.backref(
            'pokemon_abilities', order_by=slot, lazy='selectin')
    )
    ability = sa.orm.relationship(Ability, lazy='joined')
