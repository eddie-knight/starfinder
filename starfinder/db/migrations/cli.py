#!/usr/bin/env python

import os
import sys

from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import script as alembic_script
from alembic import util as alembic_util
import click
import sqlalchemy_utils

from starfinder import config, logging
from starfinder.db import models

CONF = config.CONF
LOG = logging.get_logger(__name__)

HEAD_FILENAME = "head"
ALEMBIC_INI = "alembic.ini"
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
    if not sqlalchemy_utils.database_exists(ENGINE_URL):
        sqlalchemy_utils.create_database(ENGINE_URL)


def test_connection():
    if not models.can_connect():
        print("Couldn't connect to the database. Your engine URL is:")
        print(models.engine.url)
        sys.exit(1)
    print("Connected Successfully.")


def _dispatch_alembic_cmd(config, cmd, *args, **kwargs):
    try:
        getattr(alembic_command, cmd)(config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(e)


def _get_head_path(script):
    if len(script.get_heads()) > 1:
        alembic_util.err('Timeline branches unable to generate timeline')

    head_path = os.path.join(script.versions, HEAD_FILENAME)
    return head_path


def _update_head_file(config):
    script = alembic_script.ScriptDirectory.from_config(config)
    with open(_get_head_path(script), 'w+') as f:
        f.write(script.get_current_head())


@migrate_cli.command(help="Generates a new database migration")
@click.pass_context
@click.option("-m", "--message", help="Message to store with the migration")
def revision(ctx, message):
    test_connection()
    config = ctx.obj["alembic_config"]
    _dispatch_alembic_cmd(config, "revision", message=message)
    _update_head_file(config)


def main():
    config = alembic_config.Config(
        os.path.join(os.path.dirname(__file__), ALEMBIC_INI)
    )
    config.set_main_option("script_location",
                           SCRIPT_LOCATION)

    config.set_main_option("sqlalchemy.url",
                           ENGINE_URL)
    migrate_cli(obj={"alembic_config": config})
