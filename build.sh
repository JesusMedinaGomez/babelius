#!/usr/bin/env_bash
# exit on error
set -o errexit

# poetry install
# pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate