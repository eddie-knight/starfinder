"""Initial Migration

Revision ID: a318fae4abe3
Revises: 
Create Date: 2018-03-24 11:03:07.078498

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Binary

from starfinder.db import models, utils


# revision identifiers, used by Alembic.
revision = 'a318fae4abe3'
down_revision = None
branch_labels = None
depends_on = None

users = table(
    'users',
    column('id', Binary),
    column('username', String),
    column('hashed_password', String))

alignments = table(
    'alignments',
    column('description', String))

deities = table(
    'deities',
    column('name', String),
    column('represents', String),
    column('alignment_id', String))

creature_sizes = table(
    'creature_sizes',
    column('size_category', String),
    column('height_or_length', String),
    column('weight', String),
    column('space', String),
    column('natural_reach_tall', String),
    column('natural_reach_long', String))

def upgrade():
    op.create_table('users',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', models.GUID(length=16), nullable=False),
    sa.Column('username', sa.String(length=16), nullable=False),
    sa.Column('hashed_password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('characters',
    sa.Column('id', models.GUID(length=16), nullable=False),
    sa.Column('name', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('classes',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('character_id', models.GUID(length=16), nullable=False),
    sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),    
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('races',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('character_id', models.GUID(length=16), nullable=False),
    sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),    
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('themes',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('character_id', models.GUID(length=16), nullable=False),
    sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),    
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('home_worlds',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('home_world', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('creature_sizes',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('size_category', sa.String(length=16), nullable=False),
    sa.Column('height_or_length', sa.String(length=16), nullable=False),
    sa.Column('weight', sa.String(length=20), nullable=False),
    sa.Column('space', sa.String(length=16), nullable=False),
    sa.Column('natural_reach_tall', sa.String(length=16), nullable=False),
    sa.Column('natural_reach_long', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('alignments',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('description', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('deities',
    sa.Column('id', sa.Integer(), primary_key=True, ),
    sa.Column('name', sa.String(length=16), nullable=False),
    sa.Column('represents', sa.String(length=60), nullable=False),
    sa.Column('alignment_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['alignment_id'], ['alignments.id'], ),    
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('character_details',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', models.GUID(length=16), nullable=False),
    sa.Column('class_id', sa.Integer(), nullable=False),
    sa.Column('race_id', sa.Integer(), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=False),
    sa.Column('home_world_id', sa.Integer(), nullable=False),
    sa.Column('deity_id', sa.Integer(), nullable=False),
    sa.Column('size',sa.Integer(), nullable=False),
    sa.Column('alignment', sa.Integer(), nullable=False),
    sa.Column('gender', sa.String(length=16), nullable=False),
    sa.Column('description', sa.String(length=160), nullable=False),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ),    
    sa.ForeignKeyConstraint(['race_id'], ['races.id'], ),    
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ),    
    sa.ForeignKeyConstraint(['home_world_id'], ['home_worlds.id'], ),    
    sa.ForeignKeyConstraint(['deity_id'], ['deities.id'], ),    
    sa.ForeignKeyConstraint(['size'], ['creature_sizes.id'], ),    
    sa.ForeignKeyConstraint(['alignment'], ['alignments.id'], ),    
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.bulk_insert(alignments,
                   [
                       {'description': 'Good'},
                       {'description': 'Lawful Good'},
                       {'description': 'Chaotic Good'},
                       {'description': 'Neutral'},
                       {'description': 'Lawful Neutral'},
                       {'description': 'Chaotic Neutral'},
                       {'description': 'Evil'},
                       {'description': 'Lawful Evil'},
                       {'description': 'Chaotic Evil'}
                    ])
    op.bulk_insert(creature_sizes,
                   [
                       {'size_category': 'Fine',
                           'height_or_length': "6 in. or less",
                           'weight': "1/8 lb. or less",
                           'space': "1/2 ft.",
                           'natural_reach_tall': "0 ft.",
                           'natural_reach_long': "0 ft."},
                       {'size_category': 'Dimunitive',
                           'height_or_length': "6 in. - 1 ft.",
                           'weight': "1/8 lb. - 1 lb.",
                           'space': "1 ft.",
                           'natural_reach_tall': "0 ft.",
                           'natural_reach_long': "0 ft."},
                       {'size_category': 'Tiny',
                           'height_or_length': "1 - 2 ft.",
                           'weight': "1 - 8 lbs.",
                           'space': "2-1/2 ft.",
                           'natural_reach_tall': "0 ft.",
                           'natural_reach_long': "0 ft."},
                       {'size_category': 'Small',
                           'height_or_length': "2 - 4 ft.",
                           'weight': "8 - 60 lbs.",
                           'space': "5 ft.",
                           'natural_reach_tall': "5 ft.",
                           'natural_reach_long': "5 ft."},
                       {'size_category': 'Medium',
                           'height_or_length': "4 - 8 ft.",
                           'weight': "60 - 500 lbs.",
                           'space': "5 ft.",
                           'natural_reach_tall': "5 ft.",
                           'natural_reach_long': "5 ft."},
                       {'size_category': 'Large',
                           'height_or_length': "8 - 16 ft.",
                           'weight': "500 lbs. - 2 tons",
                           'space': "10 ft.",
                           'natural_reach_tall': "10 ft.",
                           'natural_reach_long': "5 ft."},
                       {'size_category': 'Huge',
                           'height_or_length': "16 - 32 ft.",
                           'weight': "2 - 16 tons",
                           'space': "15 ft.",
                           'natural_reach_tall': "15 ft.",
                           'natural_reach_long': "10 ft."},
                       {'size_category': 'Gargantuan',
                           'height_or_length': "32 - 64 ft.",
                           'weight': "16 - 125 tons",
                           'space': "20",
                           'natural_reach_tall': "20 ft.",
                           'natural_reach_long': "15 ft."},
                       {'size_category': 'Colossal',
                           'height_or_length': "64 ft. or more",
                           'weight': "125 tons or more",
                           'space': "30 ft.",
                           'natural_reach_tall': "30 ft.",
                           'natural_reach_long': "20 ft."}
                    ])
    op.bulk_insert(deities,
                   [
                       {'name': 'Abadar',
                           'represents': "Civilization, commerce, law, and wealth",
                           'alignment_id': "5"},
                       {'name': 'Besmara',
                           'represents': "Piracy, space monsters, and strife",
                           'alignment_id': "6"},
                       {'name': 'Desna',
                           'represents': "Dreams, luck, stars, and travelers",
                           'alignment_id': "3"},
                       {'name': 'Urgathoa',
                           'represents': "Goddess of disease, gluttony, and undeath",
                           'alignment_id': "7"},
                       {'name': 'Nyarlathotep',
                           'represents': "Conspiracies, dangerous secrets, and forbidden magic",
                           'alignment_id': "9"},
                       {'name': 'Damoritosh',
                           'represents': "Conquest, duty, and war",
                           'alignment_id': "8"},
                       {'name': 'Ibra',
                           'represents': "Celestial bodies, the cosmos, and mysteries of the universe",
                           'alignment_id': "4"},
                       {'name': 'Iomedae',
                           'represents': "Honorable battle, humanity, justice, and valor",
                           'alignment_id': "2"},
                       {'name': 'Lao Shu Po',
                           'represents': "Assassins, rats, spies, and thieves",
                           'alignment_id': "7"},
                       {'name': 'Pharasma',
                           'represents': "Birth, death, fate, and prohecy",
                           'alignment_id': "4"},
                       {'name': 'Sarenrae',
                           'represents': "Healing, redemption, and the sun",
                           'alignment_id': "1"},
                       {'name': 'Zon-Kuthon',
                           'represents': "Darkness, envy, loss, and pain",
                           'alignment_id': "8"},
                       {'name': 'The Devourerer',
                           'represents': "Black holes, destruction, and supernovas",
                           'alignment_id': "9"},
                       {'name': 'Triune',
                           'represents': "Artificial intelligence, computers, and the Drift",
                           'alignment_id': "4"},
                       {'name': 'Eloritu',
                           'represents': "History, magic, and secrets",
                           'alignment_id': "4"},
                    ])



def downgrade():
    print("Downgrades not supported")
