#!/usr/bin/env bash

current="$( dirname "$(readlink -f "$0")" )"
echo "[## RESET MIGRATIONS ##] current dir = $current"

project="$current/../../"
echo "[## RESET MIGRATIONS ##] project dir = $project"

echo "[## RESET MIGRATIONS ##] Deleting migrations files..."
find "$project" -path "*transiq/*/migrations/*.py" -not -name "__init__.py" -delete
find "$project" -path "*transiq/*/migrations/*.pyc"  -delete

echo "[## RESET MIGRATIONS ##] Deleting migration entries from db..."
echo "delete from django_migrations;" | python "$project"/transiq/manage.py dbshell

echo "[## RESET MIGRATIONS ##] Creating new migration files..."
python "$project"/transiq/manage.py makemigrations

echo "[## RESET MIGRATIONS ##] Creating fake migration entries..."
python "$project"/transiq/manage.py migrate --fake

echo "[## RESET MIGRATIONS ##] Done!"