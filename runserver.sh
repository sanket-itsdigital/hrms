#!/bin/bash
# Script to run Django development server on port 8001

cd "$(dirname "$0")"
source env/bin/activate
python manage.py runserver 8001
