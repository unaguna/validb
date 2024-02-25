#!/bin/bash -e

python -m pip install --upgrade build twine

python -m build
python -m twine upload --repository pypitest dist/*
