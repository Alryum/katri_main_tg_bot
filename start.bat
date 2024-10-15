@echo off
:: Активация виртуального окружения
call venv\Scripts\activate

:: Обновление репозитория через git
git pull

python manage.py
