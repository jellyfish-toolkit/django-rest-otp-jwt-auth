django-rest-opt-auth
====================

1. Add app to your INSTALLED_APPS setting like this::

```python
INSTALLED_APPS = [
    ...
    'django_rest_opt_auth',
]
```
Make migration for app
```python
python manage.py makemigrations django_rest_opt_auth
```

2. Include the polls URLconf in your project urls.py like this::

```python
path('<path>/', include('django_rest_opt_auth.urls'))
```

Paths are:

`/sending`
`/checking`

3. In settings.py:

*For JWT*
```python
JWT_SECRET = 'super-secret-key'
JWT_ALGORITHM = 'HS256'
JWT_ROLE = DATABASES['default']['USER']
JWT_EXP = <amount in minutes>
```

*For smssender*
```python
    'See smssender readme'
```

*For sms code*
```python
SMS_CODE_LEN = <int>
SMS_CODE_LOWER = <bool>
SMS_CODE_UPPER = <bool>
SMS_CODE_DIGITS = <bool>
```

*For sms content*
```python
APP_NAME = '...'
OTP_MESSAGE = "Hi, you're trying to login into {APP_NAME}," \
              " please input this code {CODE} into input"
```

*For sms driver*
```python
SMS_DRIVER = '<import string for needed driver>'
```

```python
Set up User model
AUTH_USER_MODEL = '<app>.<User model name>'
```

4. Request examples
Sending:

url - `/sending`

```js
{
    "phone": ".."
}
```

Checking:

url - `/checking`

```js
{
    "code": "..."
}
```

5. Response examples

`/sending`

```js
{
    "message": {
        "from": "..",
        "to": "..",
        "status": ".."
    }, 
    "status": 200
}
```

`/checking`

```js
{
    "token": "...."
    "status": 200
}
```

6. Error example

```js
{
    "status": <your error HTTP code>,
    "error": {
        "message": "Error explanation"
    }
}
```
