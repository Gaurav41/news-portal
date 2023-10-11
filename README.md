# news-portal
Basic Django Application

# Setup
1. Clone the repo
2. cd to folder news-portal,run: cd news-portal
3. Create python virtual environment, run: python -m venv venv
4. Activate venv, run: venv\Scripts\activate
5. install requirements from requirements.txt, run: pip install -r requirements.txt
6. set env varibale,
   a. API_BASE_URL='https://newsapi.org/v2'
   b. API_KEY=(your API key)

# Steps to run application
1. make migrations , run: python manage.py makemigrations
2. migrate (Apply database changes), run: python manage.py migrate
3. create superuser or admin, run:python manage.py createsuperuser
4. run application, run: python manage.py runserver
5. visit: http://127.0.0.1:8000/


* run above mentioned in windows cmd.

# References
1. https://docs.djangoproject.com/en/4.2/
2. https://django-filter.readthedocs.io/en/stable/guide/usage.html#declaring-filters
3. https://newsapi.org/docs

# Approx time
Aprrox time take to build this project - 10 hrs.