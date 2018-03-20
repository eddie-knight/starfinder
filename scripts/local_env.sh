#!/bin/bash

make db_localhost
set -a
source .env
set +a
make db_unset_localhost
