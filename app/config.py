import os


class Config:
    DATABASE_USER = os.environ.get('DATABASE_USER', 'ticket')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'devpassword')
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    DATABASE = os.environ.get('DATABASE', 'ticket')
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL', f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE}")
    TEST_ENVIRONMENT = os.getenv("TEST_ENVIRONMENT", "False") == "True"