#!/usr/bin/env python

import os
import sys
from flask_alembic import Alembic

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


def _dispatch_alembic_cmd(alembic_config, cmd, *args, **kwargs):
    try:
        getattr(alembic_command, cmd)(alembic_config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(e)


def _get_head_path(script):
    if len(script.get_heads()) > 1:
        alembic_util.err('Timeline branches unable to generate timeline')
    head_path = os.path.join(script.versions, HEAD_FILENAME)
    return head_path


def _update_head_file(alembic_config):
    script = alembic_script.ScriptDirectory.from_config(alembic_config)
    with open(_get_head_path(script), 'w+') as f:
        f.write(script.get_current_head())


@migrate_cli.command(help="Generates a new database migration")
@click.pass_context
@click.option("-m", "--message", help="Message to store with the migration")
def revision(ctx, message):
    with flask_app.app_context():
        alembic_config = ctx.obj["alembic_config"]
        print(alembic_config.revision(message))


@migrate_cli.command(help="Upgrades the database to the specified version. "
                          "Pass 'head' as the revision to upgrade to the latest "
                          "version")
@click.pass_context
@click.argument("migration_revision")
def upgrade(ctx, migration_revision):
        alembic_config = ctx.obj["alembic_config"]
        migration_revision = migration_revision.lower()
        _dispatch_alembic_cmd(alembic_config, "upgrade", revision=migration_revision)


def main():
    alembic_config = Alembic()
    alembic_config.init_app(flask_app)
    migrate_cli(obj={"alembic_config": alembic_config})
