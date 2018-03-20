#!/usr/bin/env python

import sys
import distutils.core

from pip.download import PipSession
from pip.req import parse_requirements

from starfinder import __version__

try:
    import setuptools
except ImportError:
    pass


def requires(path):
    return [str(r.req) for r in parse_requirements(path, session=PipSession())
            if r]


distutils.core.setup(
    name="starfinder",
    version=__version__,
    packages=["starfinder"],
    package_data={
        "starfinder": [],
        },
    author="Sacred Tenet",
    author_email="iv.eddieknight@gmail.com",
    url="https://github.com/sacred-tenet/starfinder",
    download_url="https://github.com/sacred-tenet/starfinder/releases",
    license="https://github.com/sacred-tenet/starfinder/LICENSE",
    description="",
    install_requires=requires("requirements.txt"),
    entry_points={
        "console_scripts": [
            "starfinder_shell = starfinder.shell:main",
            "starfinder_flask_server = starfinder.starfinder_app:run_server",
            "starfinder_gunicorn_server = starfinder.wsgi:run_server",
            "starfinder_db_manage = starfinder.db.migrations.cli:main",
        ]}
    )