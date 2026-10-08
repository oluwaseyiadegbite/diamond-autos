# Diamond Autos Inventory Manager

A Django web app for a used-car business. It records cars, purchase prices, repair expenses and sales, calculates profit per vehicle, and shows available versus sold stock.

**Profit = sale price - purchase price - recorded expenses.**

## Features
- Secure login (Django authentication, CSRF protection, password validation)
- Add, edit and archive vehicle records (archiving hides a car without deleting its history)
- Multiple expenses per car
- Mark cars as sold, with profit calculated automatically
- Search and filter stock
- Dashboard with stock value and recorded profit
- Tests for calculations, validation and access permissions

## Permissions
- Any logged-in user can view stock, add cars and add expenses.
- Only staff users can edit, archive or sell cars.

## Built with
Python, Django, SQLite (PostgreSQL supported), HTML, CSS, JavaScript

## Run it
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations inventory
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000 and log in. Run the tests with `python manage.py test`.

## Use PostgreSQL instead of SQLite
Set `POSTGRES_DB` (and optionally `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`) before running the commands above.

## Before deploying
Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS`. Not production-ready yet: add login rate limiting (for example django-axes) and a production web server.

I added a "days in stock" column, with a model property and a test.
