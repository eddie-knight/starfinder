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


class HasGuid(object):
    """id mixin, add to subclasses that have a Globally Unique Identifier."""

    id = db_engine.Column(GUID,
                   primary_key=True,
                   default=db_utils.generate_guid)


class HasId(object):
    """id mixin, add to subclasses that have an incrementing id."""

    id = db_engine.Column(db_engine.Integer(), primary_key=True)


class User(db_engine.Model, ModelBase, HasGuid):
    username = db_engine.Column(db_engine.String(80), unique=True, nullable=False)

    characters = orm.relationship('Character', backref='user')

    def __repr__(self):
        return self.username


class Modifier(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    effected_stat = db_engine.Column(db_engine.String(64), nullable=False)
    modification = db_engine.Column(db_engine.Integer(), nullable=True)
    description = db_engine.Column(db_engine.String(64), nullable=True)

    themes = orm.relationship('ThemeModifier', backref='modifier')
    racial_traits = orm.relationship('RacialTraitModifier', backref='modifier')
    feats = orm.relationship('Feat', backref='modifier')
    class_modifiers = orm.relationship('ClassModifier', backref='modifier')


class Feat(db_engine.Model, ModelBase, HasId):
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=True)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    tagline = db_engine.Column(db_engine.String(64), nullable=False)
    prereq_text = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    benefit = db_engine.Column(db_engine.String(64), nullable=False)
    extra_text = db_engine.Column(db_engine.String(64), nullable=False)
    combat_feat = db_engine.Column(db_engine.Boolean(), nullable=False)

    character_feats = orm.relationship('CharacterFeat', backref='feat')
    race_associated = orm.relationship('RaceAssociatedFeat', backref='feat')
    class_proficiencies = orm.relationship('ClassProficiency', backref='feat')
    special_skills = orm.relationship('ClassSpecialSkill', backref='feat')
    mystic_skills = orm.relationship('MysticSkill', backref='feat')
    operative_skills = orm.relationship('OperativeSkill', backref='feat')
    feat_options = orm.relationship('FeatOption', backref='feat')


class Range(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)

    spells = orm.relationship('Spell', backref='range')


class Spell(db_engine.Model, ModelBase, HasId):
    school_id = db_engine.Column(db_engine.ForeignKey("magic_schools.id"),
                                 nullable=False)
    range_id = db_engine.Column(db_engine.ForeignKey("ranges.id"),
                                 nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    short_description = db_engine.Column(db_engine.String(64), nullable=True)
    long_description = db_engine.Column(db_engine.String(64), nullable=False)
    mystic_level = db_engine.Column(db_engine.Integer(), nullable=True)
    technomancer_level = db_engine.Column(db_engine.Integer(), nullable=True)
    casting_time = db_engine.Column(db_engine.String(64), nullable=False)
    area = db_engine.Column(db_engine.String(64), nullable=True)
    targets = db_engine.Column(db_engine.String(64), nullable=False)
    duration = db_engine.Column(db_engine.String(64), nullable=False)
    saving_throw = db_engine.Column(db_engine.String(64), nullable=True)
    spell_resistance = db_engine.Column(db_engine.Boolean(), 
                                        nullable=False, default=False)

    descriptor = orm.relationship('SpellDescriptor', backref='spell')
    character_spells = orm.relationship('CharacterSpell', backref='spell')


class FeatOption(db_engine.Model, ModelBase, HasId):
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)
    parent_id = db_engine.Column(db_engine.Integer(), nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class SpellDescriptor(db_engine.Model, ModelBase, HasId):
    spell_id = db_engine.Column(db_engine.ForeignKey("spells.id"),
                                     nullable=False)
    descriptor_id = db_engine.Column(db_engine.ForeignKey("descriptors.id"),
                                     nullable=False)


class Equipment(db_engine.Model, ModelBase, HasGuid):
    attributes = db_engine.Column(db_engine.JSON("equipments.attributes"),
                                     nullable=False)

    character_equipment = orm.relationship('CharacterEquipment', backref='equipment')


class Ammunition(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(832), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    charges_cartridge = db_engine.Column(db_engine.Integer(), nullable=False)
    bulk = db_engine.Column(db_engine.String(64), nullable=True)
    special = db_engine.Column(db_engine.String(64), nullable=True)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class Armor(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(832), nullable=False)
    type_armor = db_engine.Column(db_engine.Boolean(), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    eac = db_engine.Column(db_engine.Integer(), nullable=False)
    kac = db_engine.Column(db_engine.Integer(), nullable=False)
    max_dx = db_engine.Column(db_engine.Integer(), nullable=False)
    ac_penalty = db_engine.Column(db_engine.Integer(), nullable=False)
    speed_adjustment = db_engine.Column(db_engine.Integer(), nullable=False)
    upgrade_slots = db_engine.Column(db_engine.Integer(), nullable=False)
    bulk = db_engine.Column(db_engine.String(832), nullable=False)
    description = db_engine.Column(db_engine.String(832), nullable=False)


class ArmorUpgrade(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(832), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    slots = db_engine.Column(db_engine.Integer(), nullable=False)
    armor_type = db_engine.Column(db_engine.String(832), nullable=False)
    bulk = db_engine.Column(db_engine.String(832), nullable=True)
    description = db_engine.Column(db_engine.String(832), nullable=False)


class Augmentation(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(832), nullable=False)
    system = db_engine.Column(db_engine.String(832), nullable=False)
    model = db_engine.Column(db_engine.String(832), nullable=True)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=True)
    biotech = db_engine.Column(db_engine.Boolean(), nullable=False)


class Fusion(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class TechItem(db_engine.Model, ModelBase, HasId):
    item_type = db_engine.Column(db_engine.String(64), nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    hands = db_engine.Column(db_engine.Integer(), nullable=True)
    bulk = db_engine.Column(db_engine.Integer(), nullable=True)
    capacity = db_engine.Column(db_engine.Integer(), nullable=True)
    usage = db_engine.Column(db_engine.String(64), nullable=True)


class PersonalUpgrade(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    boost = db_engine.Column(db_engine.Integer(), nullable=False)


class Grenade(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    range_grenade = db_engine.Column(db_engine.String(64), nullable=False)
    capacity = db_engine.Column(db_engine.String(64), nullable=False)
    bulk = db_engine.Column(db_engine.String(64), nullable=False)
    special = db_engine.Column(db_engine.String(64), nullable=False)


class MeleeWeapon(db_engine.Model, ModelBase, HasId):
    category = db_engine.Column(db_engine.Integer(), nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=True)
    price = db_engine.Column(db_engine.Integer(), nullable=True)
    damage = db_engine.Column(db_engine.String(64), nullable=False)
    critical = db_engine.Column(db_engine.String(64), nullable=True)
    bulk = db_engine.Column(db_engine.String(64), nullable=True)
    special = db_engine.Column(db_engine.String(64), nullable=False)
    powered = db_engine.Column(db_engine.Binary(), nullable=False)
    operative = db_engine.Column(db_engine.Binary(), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    

class WeaponCategory(db_engine.Model, ModelBase, HasId):
    weapon_type = db_engine.Column(db_engine.String(64), nullable=False)
    hands = db_engine.Column(db_engine.Integer(), nullable=False)
    category = db_engine.Column(db_engine.String(64), nullable=False)


class SolarianCrystal(db_engine.Model, ModelBase, HasId):
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    damage = db_engine.Column(db_engine.String(64), nullable=False)
    critical = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class OtherEquipment(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    weapon_type = db_engine.Column(db_engine.String(64), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    bulk = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=True)


class RangedWeapon(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    category = db_engine.Column(db_engine.Integer(), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    price = db_engine.Column(db_engine.Integer(), nullable=False)
    damage = db_engine.Column(db_engine.String(64), nullable=False)
    attack_rangesss = db_engine.Column(db_engine.String(64), nullable=False)
    critical = db_engine.Column(db_engine.String(64), nullable=False)
    capacity = db_engine.Column(db_engine.String(64), nullable=False)
    usage = db_engine.Column(db_engine.Integer(), nullable=False)
    bulk = db_engine.Column(db_engine.String(64), nullable=False)
    special = db_engine.Column(db_engine.String(64), nullable=True)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class Class(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(832), nullable=False)
    hit_points = db_engine.Column(db_engine.Integer(), nullable=False)
    stamina_points = db_engine.Column(db_engine.Integer(), nullable=False)
    key_ability_score = db_engine.Column(db_engine.Integer(), nullable=False)
    key_ability_score_text = db_engine.Column(db_engine.String(64), nullable=False)
    skills_per_level = db_engine.Column(db_engine.Integer(), nullable=False)
    special_skill_name = db_engine.Column(db_engine.String(64), nullable=True)
    special_skill_description = db_engine.Column(db_engine.String(64), nullable=True)

    character = orm.relationship('Character', backref='class')
    special_skills = orm.relationship('ClassSpecialSkill', backref='class')
    class_proficiencies = orm.relationship('ClassProficiency', backref='class')
    class_feats = orm.relationship('ClassFeat', backref='class')
    operative_skills = orm.relationship('OperativeSkill', backref='class')


class Theme(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    level_1 = db_engine.Column(db_engine.String(64), nullable=False)
    level_6 = db_engine.Column(db_engine.String(64), nullable=False)
    level_12 = db_engine.Column(db_engine.String(64), nullable=False)
    level_18 = db_engine.Column(db_engine.String(64), nullable=False)

    character = orm.relationship('Character', backref='theme')
    theme_modifiers = orm.relationship('ThemeModifier', backref='theme')
    class_modifiers = orm.relationship('ClassModifier', backref='theme')


class ClassProficiency(db_engine.Model, ModelBase, HasId):
    class_id = db_engine.Column(db_engine.ForeignKey("classes.id"),
                                     nullable=False)
    feats_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)


class ClassSpecialSkill(db_engine.Model, ModelBase, HasId):
    class_id = db_engine.Column(db_engine.ForeignKey("classes.id"),
                                     nullable=False)
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=True)
    parent_id = db_engine.Column(db_engine.Integer(), nullable=True)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class ClassFeat(db_engine.Model, ModelBase, HasId):
    class_id = db_engine.Column(db_engine.ForeignKey("classes.id"),
                                     nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


class Skill(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    ability_id = db_engine.Column(db_engine.ForeignKey("abilities.id"),
                                     nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    trained_only = db_engine.Column(db_engine.Binary(), nullable=False)
    ac_penalty = db_engine.Column(db_engine.Integer(), nullable=False)

    mystic_skills = orm.relationship('MysticSkill', backref='skill')


class MysticSkill(db_engine.Model, ModelBase, HasId):
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)
    skill_id = db_engine.Column(db_engine.ForeignKey("skills.id"),
                                     nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)


class OperativeSkill(db_engine.Model, ModelBase, HasId):
    class_id = db_engine.Column(db_engine.ForeignKey("classes.id"),
                                     nullable=False)
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)
    parent_id = db_engine.Column(db_engine.Integer(), nullable=False)
    level = db_engine.Column(db_engine.Integer(), nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)


# ------------
# Info Classes
# ------------

class Ability(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    shorthand = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)

    skill = orm.relationship('Skill', backref='theme')


class Alignment(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    shorthand = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)

    deities = orm.relationship('Deity', backref='alignment')


class Size(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    height_or_length = db_engine.Column(db_engine.String(64), nullable=False)
    weight = db_engine.Column(db_engine.String(64), nullable=False)
    space = db_engine.Column(db_engine.String(64), nullable=False)
    natural_reach_tall = db_engine.Column(db_engine.String(64), nullable=False)
    natural_reach_long = db_engine.Column(db_engine.String(64), nullable=False)


class Deity(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    nickname = db_engine.Column(db_engine.String(64), nullable=False)
    alignment_id = db_engine.Column(db_engine.ForeignKey("alignments.id"),
                                     nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    gender = db_engine.Column(db_engine.String(64), nullable=False)
    represents = db_engine.Column(db_engine.String(64), nullable=False)
    symbol = db_engine.Column(db_engine.String(64), nullable=False)

    character = orm.relationship('Character', backref='deity')
    places_of_worship = orm.relationship('PlacesOfWorship', backref='deity')
    mystic_deities = orm.relationship('MysticDeity', backref='deity')


class MysticDeity(db_engine.Model, ModelBase, HasId):
    mystic_connection = db_engine.Column(db_engine.String(64), nullable=False)
    deity_id = db_engine.Column(db_engine.ForeignKey("deities.id"),
                                     nullable=False)


class World(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    nickname = db_engine.Column(db_engine.String(64), nullable=False)
    diameter = db_engine.Column(db_engine.String(64), nullable=False)
    mass = db_engine.Column(db_engine.String(64), nullable=False)
    gravity = db_engine.Column(db_engine.String(64), nullable=False)
    atmosphere = db_engine.Column(db_engine.String(64), nullable=False)
    day = db_engine.Column(db_engine.String(64), nullable=False)
    year = db_engine.Column(db_engine.String(64), nullable=False)
    location = db_engine.Column(db_engine.String(64), nullable=False)
    full_text = db_engine.Column(db_engine.String(64), nullable=False)

    character = orm.relationship('Character', backref='world')
    native_races = orm.relationship('NativeRace', backref='world')
    languages = orm.relationship('Language', backref='world')
    places_of_worship = orm.relationship('PlacesOfWorship', backref='world')


class PlacesOfWorship(db_engine.Model, ModelBase, HasId):
    deity_id = db_engine.Column(db_engine.ForeignKey("deities.id"),
                                     nullable=False)
    world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=False)


class Descriptor(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=True)

    spells = orm.relationship('SpellDescriptor', backref='descriptor')


class MagicSchool(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)

    spells = orm.relationship('Spell', backref='magic_school')


class Race(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    avg_height = db_engine.Column(db_engine.String(64), nullable=False)
    avg_weight = db_engine.Column(db_engine.Integer(), nullable=False)
    age_of_maturity = db_engine.Column(db_engine.Integer(), nullable=False)
    max_age = db_engine.Column(db_engine.Integer(), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=False)
    hit_points = db_engine.Column(db_engine.Integer(), nullable=False)
    race_type = db_engine.Column(db_engine.String(64), nullable=False)
    physical_description = db_engine.Column(db_engine.String(64), nullable=True)
    homeworld = db_engine.Column(db_engine.String(64), nullable=True)
    society_and_alignment = db_engine.Column(db_engine.String(64), nullable=True)
    relations = db_engine.Column(db_engine.String(64), nullable=True)
    adventurers = db_engine.Column(db_engine.String(64), nullable=True)
    names = db_engine.Column(db_engine.String(64), nullable=True)

    characters = orm.relationship('Character', backref='race')
    native_races = orm.relationship('NativeRace', backref='race')
    racial_traits = orm.relationship('RacialTrait', backref='race')
    languages = orm.relationship('Language', backref='race')


class RacialTrait(db_engine.Model, ModelBase, HasId):
    race_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=False)
    name = db_engine.Column(db_engine.String(64), nullable=False)
    description = db_engine.Column(db_engine.String(64), nullable=True)

    racial_trait_modifiers = orm.relationship('RacialTraitModifier', backref='racial_trait')
    associated_feat = orm.relationship('RaceAssociatedFeat', backref='racial_trait')


class NativeRace(db_engine.Model, ModelBase, HasId):
    world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=False)
    race_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=False)


class Language(db_engine.Model, ModelBase, HasId):
    name = db_engine.Column(db_engine.String(64), nullable=False)
    world_id = db_engine.Column(db_engine.ForeignKey("worlds.id"),
                                     nullable=True)
    race_id = db_engine.Column(db_engine.ForeignKey("races.id"),
                                     nullable=True)
    other = db_engine.Column(db_engine.String(64), nullable=True)


class RacialTraitModifier(db_engine.Model, ModelBase, HasId):
    trait_id = db_engine.Column(db_engine.ForeignKey("racial_traits.id"),
                                     nullable=False)
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=False)


class ClassModifier(db_engine.Model, ModelBase, HasId):
    theme_id = db_engine.Column(db_engine.ForeignKey("themes.id"),
                                     nullable=False)
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=False)


class ThemeModifier(db_engine.Model, ModelBase, HasId):
    theme_id = db_engine.Column(db_engine.ForeignKey("themes.id"),
                                     nullable=False)
    modifier_id = db_engine.Column(db_engine.ForeignKey("modifiers.id"),
                                     nullable=False)


class RaceAssociatedFeat(db_engine.Model, ModelBase, HasId):
    trait_id = db_engine.Column(db_engine.ForeignKey("racial_traits.id"),
                                     nullable=False)
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)


class Character(db_engine.Model, ModelBase, HasGuid):
    user_id = db_engine.Column(db_engine.ForeignKey("users.id"),
                                     nullable=True)
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
    strength = db_engine.Column(db_engine.Integer(), nullable=True)
    dexterity = db_engine.Column(db_engine.Integer(), nullable=True)
    constitution = db_engine.Column(db_engine.Integer(), nullable=True)
    intelligence = db_engine.Column(db_engine.Integer(), nullable=True)
    wisdom = db_engine.Column(db_engine.Integer(), nullable=True)
    charisma = db_engine.Column(db_engine.Integer(), nullable=True)

    character_skills = orm.relationship('CharacterSkill', backref='character')
    character_feats = orm.relationship('CharacterFeat', backref='character')
    character_equipment = orm.relationship('CharacterEquipment', backref='character')
    character_spells = orm.relationship('CharacterSpell', backref='character')

    @property
    def stamina(self):
        # stamina = constitution - con_mod - race.points
        return " "
    def hit_points(self):
        # hit_points = race.hit_points + (class.hit_points * class.level)
        return " "
    def str_mod(self):
        # str_mod = (strength / 2) - 5
        return " "
    def dex_mod(self):
        # dex_mod = (dexterity / 2) - 5
        return " "
    def con_mod(self):
        # con_mod = (constitution / 2) - 5
        return " "
    def int_mod(self):
        # int_mod = (intelligence / 2) - 5
        return " "
    def wis_mod(self):
        # wis_mod = (wisdom / 2) - 5
        return " "
    def char_mod (self):
        # char_mod = (charisma / 2) - 5
        return " "
    def misc_mod(self):
        # misc_mod = ?
        return " "
    def armor_bonus(self):
        # armor_bonus = ?
        return " "
    def eac(self):
        # eac = 10 + armor_bonus + dex_mod + misc_mod
        return " "
    def kac(self):
        # kac = 10 + armor_bonus + dex_mod + misc_mod
        return " "
    def ac_vs_combat(self):
        # ac_vs_combat = 8 + kac
        return " "
    def initiative(self):
        # initiative = dex_mod + misc_mod
        return " "
    def base_save(self):
        # base_save = ?
        return " "
    def fortitude_save(self):
        # fortitude_save = base_save + str_mod + misc_mod
        return " "
    def reflex_save(self):
        # reflex_save = base_save + dex_mod + misc_mod
        return " "
    def will_save(self):
        # will_save = base_save + wis_mod + misc_mod
        return " "
    def base_atk_bonus(self):
        # base_atk_bonus = ?
        return " "
    def melee_atk(self):
        # melee_atk = base_atk_bonus + str_mod + misc_mod
        return " "
    def ranged_atk(self):
        # ranged_atk = base_atk_bonus + dex_mod + misc_mod
        return " "
    def thrown_atk(self):
        # thrown_atk = base_atk_bonus + str_mod + misc_mod
        return " "
    def alignment(self):
        # alignment = ?
        return " "
    def user(self):
        return " "


    def __str__(self):
        return self.name


class CharacterEquipment(db_engine.Model, ModelBase, HasGuid):
    character_id = db_engine.Column(db_engine.ForeignKey("characters.id"),
                                     nullable=False)
    equipment_id = db_engine.Column(db_engine.ForeignKey("equipments.id"),
                                     nullable=False)
    in_bag = db_engine.Column(db_engine.Boolean(), nullable=False)


class CharacterFeat(db_engine.Model, ModelBase, HasGuid):
    character_id = db_engine.Column(db_engine.ForeignKey("characters.id"),
                                     nullable=False)
    feat_id = db_engine.Column(db_engine.ForeignKey("feats.id"),
                                     nullable=False)

class CharacterSpell(db_engine.Model, ModelBase, HasGuid):
    character_id = db_engine.Column(db_engine.ForeignKey("characters.id"),
                                     nullable=False)
    spell_id = db_engine.Column(db_engine.ForeignKey("spells.id"),
                                     nullable=False)


class CharacterSkill(db_engine.Model, ModelBase, HasGuid):
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