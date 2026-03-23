# TODO App

Task management application built with Django.

## Features

- User registration and login
- Create, edit and delete tasks
- Soft delete with trash view
- Assign tasks to another user
- Task history / change tracking

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- Bootstrap

## Run locally

```bash
git clone https://github.com/Algiuxs-core/todo-app.git
cd todo-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver