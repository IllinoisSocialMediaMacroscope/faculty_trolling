#!/bin/bach

find . -path "*/migrations/*.pyc" -delete
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
rm db.sqlite3
python3 manage.py makemigrations 
python3 manage.py migrate
