#!/bin/bash

set -euxo pipefail

# Code quality checks
all_files=(./*.py)

black --check "${all_files[@]}"
flake8 "${all_files[@]}"
ruff "${all_files[@]}"
isort --check "${all_files[@]}"
mypy "${all_files[@]}"

# TODO: pytest
# pytest -p no:cacheprovider test_*.python
