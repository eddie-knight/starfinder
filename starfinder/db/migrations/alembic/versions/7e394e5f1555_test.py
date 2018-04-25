"""test

Revision ID: 7e394e5f1555
Revises: f1262d8677b5
Create Date: 2018-04-24 19:15:25.403700

"""
from alembic import op
import sqlalchemy as sa

import starfinder.db.models


# revision identifiers, used by Alembic.
revision = '7e394e5f1555'
down_revision = 'f1262d8677b5'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    print("Downgrades not supported")
