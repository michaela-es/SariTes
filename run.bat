@echo off
cd /d "%~dp0"
call sarites\.venv\Scripts\activate.bat
echo Activated .venv — running: python manage.py runserver
cd sarites
python manage.py runserver
