# Garage Management System

A Django web application for managing a garage: customers, mechanics, services, job cards, customer bills and payments.

## Group Members

| No. | Name                  | Registration Number  |
|-----|-----------------------|----------------------|
| 1   | MAGATTO FAROUK        | 224-063012-29833     |
| 2   | GHASSANU BIN SULAIT   | 224-063012-29022     |
| 3   | LIBEGA UMAR           | 224-063012-31797     |

## Features

- Public pages: welcome page (`/`) and home page (`/home/`) listing the garage services
- Staff login and a dashboard with statistics, job status chart and latest payments
- Manage customers, mechanics and services (add, edit, delete, search)
- Job cards with multiple service items, status tracking and a status filter
- Customer bills generated from job cards, with discount, net cost and balance
- Payments with automatic receipt numbers (overpayment is blocked)
- Printable invoice, Django admin and a responsive design

## Database Entities

`Customer`, `Mechanic`, `Service`, `JobCard`, `JobCardItem`, `Bill`, `Payment`

## Requirements

- Python 3.10+
- Django 5.0+

## How to Run

```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# 2. install dependencies
pip install -r requirements.txt

# 3. create the database
python manage.py migrate

# 4. create an admin / staff account
python manage.py createsuperuser

# 5. (optional) load demo services and a mechanic
python manage.py seed_demo

# 6. start the server
python manage.py runserver
```

Then open:

- Public site: http://127.0.0.1:8000/
- Staff login: http://127.0.0.1:8000/accounts/login/
- Dashboard: http://127.0.0.1:8000/dashboard/
- Admin panel: http://127.0.0.1:8000/admin/

## Workflow

1. Add a customer
2. Create a job card (vehicle, problem, mechanic, service items)
3. Generate a bill from the job card (apply a discount if any)
4. Record payment(s) and issue a receipt

## Project Structure

```
garage_system/
├── manage.py
├── config/            # settings and root urls
├── garage/            # models, views, forms, urls, admin, templates
│   ├── templates/
│   ├── templatetags/
│   └── management/commands/seed_demo.py
├── static/css/style.css
└── requirements.txt
```

## Notes

- Currency (UGX) can be changed in `garage/templatetags/garage_extras.py` (`CURRENCY`).
- Before deploying, set `DEBUG = False` and change `SECRET_KEY` in `config/settings.py`.
