import contextlib
import functools
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import orm, func
from sqlalchemy.ext import declarative
import sqlalchemy_utils

from starfinder import config, logging, flask_app
from starfinder.db import utils as db_utils

CONF = config.CONF
LOG = logging.get_logger(__name__)
TABLE_KWARGS = {"mysql_engine": "InnoDB",
                "mysql_charset": "utf8",
                "mysql_collate": "utf8_general_ci"}

flask_app.config['SQLALCHEMY_DATABASE_URI'] = CONF.get('db.engine.url')
db_engine = SQLAlchemy(flask_app)
Session = db_engine.session


class ModelBase(object):
    __table_args__ = TABLE_KWARGS

    @declarative.declared_attr
    def __tablename__(cls):
        """ Returns a snake_case form of the table name. """
        return db_utils.pluralize(db_utils.to_snake_case(cls.__name__))

    def __eq__(self, other):
        if not other:
            return False
        return self.id == other.id

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if hasattr(self, key):
            return setattr(self, key, value)
        raise AttributeError(key)

    def __contains__(self, key):
        return hasattr(self, key)

    def update(self, **fields):
        for attr, value in fields.items():
            if attr not in self:
                raise exception.ModelUnknownAttrbute(model=self, attr=attr)
            self[attr] = value
        return self

    @classmethod
    def get(cls, pk):
        return Session.query(cls).filter(cls.id == pk).first()

    @classmethod
    def _get_by_property(cls, prop):
        LOG.debug("Fetching '%s' by property '%s'", cls, prop)
        return Session.query(cls).filter(prop).first()

    @classmethod
    def _get_by(cls, field, value):
        LOG.debug("Fetching one '%s.%s' by value '%s'", cls, field, value)
        return Session.query(cls).filter(field == value).first()

    @classmethod
    def _get_all_by(cls, field, value):
        LOG.debug("Fetching all '%s.%s' with value '%s'", cls, field, value)
        return Session.query(cls).filter(field == value).all()

    def save(self):
        LOG.debug("Attempting to save '%s'", self)
        with transaction() as session:
            session.add(self)

    def delete(self):
        LOG.debug("Attempting to delete '%s'", self)
        with transaction() as session:
            session.delete(self)

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()
                if not callable(value) and not key.startswith('_')}


def save(model):
    Session.add(model)
    Session.commit()


class GUID(sqlalchemy_utils.UUIDType):
    """
    Overload of the sqlalchemy_utils UUID class. There are issues
    with it and alembic, acknowledged by the maintainer:
    https://github.com/kvesteri/sqlalchemy-utils/issues/129

    """
    def __init__(self, length=16, binary=True, native=True):
        # pylint: disable=unused-argument
        # NOTE(mdietz): Ignoring length, see:
        # https://github.com/kvesteri/sqlalchemy-utils/issues/129
        super(GUID, self).__init__(binary, native)


class HasId(object):
    """id mixin, add to subclasses that have an id."""

    id = db_engine.Column(GUID,
                   primary_key=True,
                   default=db_utils.generate_guid)


class User(db_engine.Model, ModelBase, HasId):
    username = db_engine.Column(db_engine.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.username


# -----------------
# Equipment Classes
# -----------------

# class Equipment(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("equipments.attributes"),
#                                      nullable=False)


# class Ammunition(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("ammunitions.attributes"),
#                                      nullable=False)


# class Armor(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("armors.attributes"),
#                                      nullable=False)


# class ArmorUpgrade(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("armor_upgrades.attributes"),
#                                      nullable=False)


# class Augmentation(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("augmentations.attributes"),
#                                      nullable=False)


# class Computer(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("computers.attributes"),
#                                      nullable=False)


# class ComputerUpgrade(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("computer_upgrades.attributes"),
#                                      nullable=False)


# class Fusion(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("fusions.attributes"),
#                                      nullable=False)


# class Grenade(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("grenades.attributes"),
#                                      nullable=False)


# class MeleeWeapon(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("melee_weapons.attributes"),
#                                      nullable=False)


# class RangedWeapon(db_engine.Model, ModelBase, HasId):
#     attributes = db_engine.Column(db_engine.JSON("ranged_weapons.attributes"),
#                                      nullable=False)


# ------------
# Class Info Classes 
# ------------

class Class(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(832), nullable=False)
    hit_points = db_engine.Column(db_engine.Integer(), nullable=False)
    stamina_points = db_engine.Column(db_engine.Integer(), nullable=False)
    key_ability_score = db_engine.Column(db_engine.Integer(), nullable=False)
    key_ability_score_text = db_engine.Column(db_engine.String(64), nullable=False)
    skills_per_level = db_engine.Column(db_engine.Integer(), nullable=False)


class Theme(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    level_1 = db_engine.Column(db_engine.String(64), nullable=False)
    level_6 = db_engine.Column(db_engine.String(64), nullable=False)
    level_12 = db_engine.Column(db_engine.String(64), nullable=False)
    level_18 = db_engine.Column(db_engine.String(64), nullable=False)


class ClassSpecialSkill(db_engine.Model, ModelBase, HasId):
    class_id = db_engine.Column(db_engine.ForeignKey("classes.id"),
                                     nullable=False)
    class_name = db_engine.Column(db_engine.String(64), nullable=False)
    special_name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


# ------------
# Info Classes
# ------------

class Alignment(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class Size(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class Deity(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    alignment_id = db_engine.Column(db_engine.ForeignKey("alignments.id"),
                                     nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class World(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class PlacesOfWorship(db_engine.Model, ModelBase, HasId):
    world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=False)
    deity_id = db_engine.Column(db_engine.ForeignKey("deities.id"),
                                     nullable=False)


# ------------
# Race Classes
# ------------

class Race(db_engine.Model, ModelBase):
    id = db_engine.Column(db_engine.Integer(), primary_key=True)
    home_world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    avg_height = db_engine.Column(db_engine.String(64), nullable=False)
    avg_weight = db_engine.Column(db_engine.Integer(), nullable=False)
    age_of_maturity = db_engine.Column(db_engine.Integer(), nullable=False)
    max_age = db_engine.Column(db_engine.Integer(), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    hit_points = db_engine.Column(db_engine.Integer(), nullable=False)
    type_type = db_engine.Column(db_engine.String(64), nullable=False)
    physical_description = db_engine.Column(db_engine.String(64), nullable=False)
    society_and_alignment = db_engine.Column(db_engine.String(64), nullable=False)
    relations = db_engine.Column(db_engine.String(64), nullable=False)
    adventurers = db_engine.Column(db_engine.String(64), nullable=False)
    names = db_engine.Column(db_engine.String(64), nullable=False)


class RacialTrait(db_engine.Model, ModelBase, HasId):
    race_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class NativeRace(db_engine.Model, ModelBase, HasId):
    world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=False)
    race_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=False)


# --------------------
# Feat & Spell Classes
# --------------------

class Feat(db_engine.Model, ModelBase, HasId):
    modifier_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=False)
    prereq_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class Spell(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class RaceAssociatedFeat(db_engine.Model, ModelBase, HasId):
    trait_id = db_engine.Column(db_engine.ForeignKey("racial_traits.id"),
                                     nullable=False)
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)


# ----------------
# Modifier Classes
# ----------------

class Modifier(db_engine.Model, ModelBase, HasId):
    effected_stat = db_engine.Column(db_engine.String(64), nullable=False)
    modification = db_engine.Column(db_engine.Integer(), nullable=False)


class TraitModifier(db_engine.Model, ModelBase, HasId):
    trait_id = db_engine.Column(db_engine.ForeignKey("racial_traits.id"),
                                     nullable=False)
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=False)

class FeatModifier(db_engine.Model, ModelBase, HasId):
    trait_id = db_engine.Column(db_engine.ForeignKey("racial_traits.id"),
                                     nullable=False)
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=False)

class ThemeModifier(db_engine.Model, ModelBase, HasId):
    trait_id = db_engine.Column(db_engine.ForeignKey("racial_traits.id"),
                                     nullable=False)
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=False)


#-----------------
#Character Classes
#-----------------

class Character(db_engine.Model, ModelBase, HasId):
    alignment_id = db_engine.Column(db_engine.ForeignKey("alignments.id"),
                                     nullable=True)
    class_id = db_engine.Column(db_engine.ForeignKey("classes.id"),
                                     nullable=True)
    deity_id = db_engine.Column(db_engine.ForeignKey("deities.id"),
                                     nullable=True)
    home_world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=True)
    race_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=True)
    theme_id = db_engine.Column(db_engine.ForeignKey("themes.id"),
                                     nullable=True)
    name = db_engine.Column(db_engine.String(16), nullable=True)
    level = db_engine.Column(db_engine.Integer(), nullable=True)
    gender = db_engine.Column(db_engine.String(6), nullable=True)
    description = db_engine.Column(db_engine.String(160), nullable=True)

    def __str__(self):
        return self.name


class CharacterEquipment(db_engine.Model, ModelBase, HasId):
    character_id = db_engine.Column(db_engine.ForeignKey("characters.id"),
                                     nullable=False)
    attributes = db_engine.Column(db_engine.JSON("equipments.attributes"),
                                     nullable=False)


class CharacterFeat(db_engine.Model, ModelBase, HasId):
    character_id = db_engine.Column(db_engine.ForeignKey("characters.id"),
                                     nullable=False)
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)


class CharacterSkill(db_engine.Model, ModelBase, HasId):
    character_id = db_engine.Column(db_engine.ForeignKey("characters.id"),
                                     nullable=False)
    acrobatics = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    athletics = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    bluff = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    computers = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    culture = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    diplomacy = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    disguise = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    engineering = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    intimidate = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    life_science = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    medicine = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    mysticsm = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    perception = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    physical_science = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    piloting = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    profession = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    sense_motive = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    sleight_of_hand = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    stealth = db_engine.Column(db_engine.Integer(), nullable=False, default=False)
    survival = db_engine.Column(db_engine.Integer(), nullable=False, default=False)


# For maintenance and removal of database: db_engine.drop_all()
db_engine.create_all()
