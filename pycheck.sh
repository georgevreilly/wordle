#!/bin/bash

set -euxo pipefail

DIR="$(dirname $0)"
ruff "$DIR"
isort --check "$DIR"
black "$DIR"
flake8 "$DIR"
mypy "$DIR"

# TODO: pytest
