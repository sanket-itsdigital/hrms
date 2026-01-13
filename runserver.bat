@echo off
REM Script to run Django development server on port 8001 (Windows)

cd /d "%~dp0"
call env\Scripts\activate
python manage.py runserver 8001
