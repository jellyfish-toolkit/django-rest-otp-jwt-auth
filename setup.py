from setuptools import setup

setup(
    name='django-rest-jwt-auth',
    install_requires=[
        'Django>=2.0',
        'django-smssender>=0.1',
        'psycopg2_binary>=2.8.6'
    ]
)
