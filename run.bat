@echo off
call .venv\Scripts\activate.bat
echo Activated .venv — running: python manage.py runserver
python manage.py runserver
