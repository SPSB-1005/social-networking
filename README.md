# Prerequisites
- Python 3.x
- Pip (Python package manager)

# Installation steps

create and Activate a Virtual Environment
install Dependencies (pip install -r requirements.txt)
pip install django
pip install djangorestframework
django-admin startproject social_media
django-admin startapp friend_circle

Run Database Migrations (
    python manage.py makemigrations 
    python manage.py migrate
)
Start the Development Server: (python manage.py runserver)
