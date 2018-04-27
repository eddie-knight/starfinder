#!/usr/bin/env python

import os
import sys
from flask_alembic import Alembic
from alembic.config import Config
from alembic import command as alembic_command
import click
import sqlalchemy_utils

from starfinder import config, logging, flask_app
from starfinder.db import models

CONF = config.CONF
LOG = logging.get_logger(__name__)

SCRIPT_LOCATION = "starfinder.db.migrations:alembic"
MIGRATION_LOCATION = "starfinder.db.migrations:alembic_migrations"
ENGINE_URL = CONF.get("DB_ENGINE_URL")

@click.group()
def migrate_cli():
    pass


@migrate_cli.command(help="Creates the database. Must be run before any "
                          "migrations as 'upgrade' itself will not create "
                          "the database")
def create_database():
    models.db_engine.create_all()


@migrate_cli.command(help="Drops the database if it exists")
@click.option('--confirm', is_flag=True, expose_value=False,
              prompt='Are you sure you want to drop the database?')
def drop_database():
    models.db_engine.drop_all()


@migrate_cli.command(help="Generates a new database migration")
@click.pass_context
@click.option("-m", "--message", help="Message to store with the migration")
# From CLI: `starfinder_db_manage revision -m "revision title"`
# OPTION SET 2
# def revision(ctx, message): # succeeds
#     alembic_config = ctx.obj["alembic_config"]
#     alembic_command.revision(alembic_config, message)
    # Response: Generating /location/starfinder/db/migrations/alembic/versions/a3de23375e5e_revision_title.py ... done
    # Good
# OPTION SET 3
def revision(ctx, message):
    with flask_app.app_context():
        alembic_config = ctx.obj["alembic_config"]
        alembic_config.revision(message)
        # Response: AttributeError: 'NoneType' object has no attribute 'encoding'
        # Bad

# From CLI: `starfinder_db_manage upgrade`
@migrate_cli.command(help="Upgrades the database to the latest version.")
@click.pass_context
# OPTION SET 2
def upgrade(ctx):
        alembic_config = ctx.obj["alembic_config"]
        alembic_command.upgrade(alembic_config, "head")
        # Response: AttributeError: 'NoneType' object has no attribute 'encoding'
        # Bad

# OPTION SET 3
def main():
    alembic_config = Alembic()
    alembic_config.init_app(flask_app)
    migrate_cli(obj={"alembic_config": alembic_config})
# OPTION SET 2
# def main():
#     filepath = os.path.join(os.path.dirname(__file__),
#                             "alembic.ini")
#     alembic_config = Config(file_=filepath)
#     alembic_config.set_main_option("sqlalchemy.url",
#                                    ENGINE_URL)
#     alembic_config.set_main_option("script_location",
#                                    SCRIPT_LOCATION)
#     migrate_cli(obj={"alembic_config": alembic_config})