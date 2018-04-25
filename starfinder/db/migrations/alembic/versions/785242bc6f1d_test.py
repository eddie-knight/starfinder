"""test

Revision ID: 785242bc6f1d
Revises: 
Create Date: 2018-04-23 15:59:54.451878

"""
from alembic import op
import sqlalchemy as sa

import starfinder.db.models


# revision identifiers, used by Alembic.
revision = '785242bc6f1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    print("Downgrades not supported")
