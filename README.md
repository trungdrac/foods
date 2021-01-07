## Django Web Application

## Installation

1. Install global packages: `python3 -m pip install virtualenv`
2. Create virtualenv for project: `virtualenv .venv`
3. Activate virtualenv: `source .venv/bin/activate`
4. Install required packages: `python -m pip install -r requirements.txt`
5. Rename file from '.env-example', and rename it to '.env'.: `cp .env-example .env`
6. Configure PostgreSQL:
    - Switch to `postgres` user: `sudo -i -u postgres`
    - Create PSQL user: `createuser --interactive --pwprompt` (skip if you already have it). Then fill answers for
      prompts, for example:
      |Prompt|Answer| |---|---| |Enter name of role to add:|hello| |Enter password for new role:|world123| |Enter it
      again:|world123| |Shall the new role be a superuser?|y|
    - Create database for Django: `createdb -O hello django`
7. Migrate databases: `python manage.py makemigrations && python manage.py migrate`
8. Run bash: `./reset_db.sh`
9. Run server: `python manage.py runserver`
10. Open browser with url: `http://localhost:8000` or `http://127.0.0.1:8000`


Sample accounts:
  |Type|Username|Password|
  |---|---|---|
  |admin|admin_1|1a2s3d4f|
  |user|user_1|1a2s3d4f|