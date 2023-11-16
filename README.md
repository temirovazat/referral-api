# Referral API

API service with phone number authentication and a simple referral system.

## Project Structure and Description

### Phone Number Authentication

Authentication in the service is based on the phone number format "+79608543017".

To start, obtain a 4-digit code by sending a POST request with the phone number to the `POST /api/v1/auth/send_code/` endpoint.

Once the code is received, submit it along with the phone number to the `POST /api/v1/auth/jwt/get_by_phone/` endpoint. Optionally, you can include an existing referral code from another user along with the phone number and 4-digit code.

If a user with the specified phone number does not exist, they are added to the database. After addition, the user is assigned a unique referral invite code.

Upon successful authentication, the response includes JWT access/refresh tokens (bearer auth). These tokens will be needed for accessing user endpoints and profile editing. Standard endpoints for token verification and refresh are also available: `POST /api/v1/auth/jwt/verify/`, `POST /api/v1/auth/jwt/refresh/`.

### Users

- `GET /api/v1/users/`: View the list of users. The `invite_code` field is the user's personal referral code, unique and assigned during user creation. The `invited_by_code` field is the referral code of another user who invited them to the service.

- `GET /api/v1/users/{id}/`: Retrieve information about a specific user.

- `GET /api/v1/users/current_user/`: Retrieve information about the current user.

On endpoints providing information about a specific/current user, there is an `invited` field with a list of user IDs and phone numbers who accepted the invitation from the viewed user.

- `PATCH /api/v1/users/current_user/`: Edit information about the current user. You can set the user's name, surname, email address, and the invite code through which they received the service invitation.

### **How to run the project:**

Clone the repository and navigate to the ```/infra ``` directory:

```bash
git clone https://github.com/temirovazat/referral-api.git
```
```
cd referral-api/infra/
```

Create a .env file and add project settings:

```bash
vi .env
```

```
# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=referral_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Django
SECRET_KEY=django-insecure-szpgqvuswh#lxmzs1#l@t_meqr#l-qceo#f+zm#u5a2@w@3v9#
DEBUG=False

# Authentication
AUTH_CODE_EXPIRES_MINUTES=30
REFRESH_TOKEN_LIFETIME_DAYS=14
ACCESS_TOKEN_LIFETIME_MINUTES=600
```

Deploy and run the project in containers:

```bash
docker compose up -d
```

Creating a superuser:

```bash
docker compose exec ref-web python manage.py createsuperuser
```
