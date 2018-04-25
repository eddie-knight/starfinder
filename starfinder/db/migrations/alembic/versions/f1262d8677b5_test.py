"""test

Revision ID: f1262d8677b5
Revises: 785242bc6f1d
Create Date: 2018-04-23 16:00:29.858840

"""
from alembic import op
import sqlalchemy as sa

import starfinder.db.models


# revision identifiers, used by Alembic.
revision = 'f1262d8677b5'
down_revision = '785242bc6f1d'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    print("Downgrades not supported")
