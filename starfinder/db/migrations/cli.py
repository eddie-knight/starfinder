#!/usr/bin/env python

import os
import sys

from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import util as alembic_util
import click

from starfinder.db import models

HEAD_FILENAME = "head"

ALEMBIC_INI = "alembic.ini"
SCRIPT_LOCATION = "starfinder.db.migrations:alembic"
MIGRATION_LOCATION = "starfinder.db.migrations:alembic_migrations"

@click.group()
def migrate_cli():
    pass


def test_connection():
    if not models.can_connect():
        print("Couldn't connect to the database. Your engine URL is:")
        print(models.engine.url)
        sys.exit(1)


def _dispatch_alembic_cmd(config, cmd, *args, **kwargs):
    try:
        getattr(alembic_command, cmd)(config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(e)


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
                           models.ENGINE_URL)
    migrate_cli(obj={"alembic_config": config})
