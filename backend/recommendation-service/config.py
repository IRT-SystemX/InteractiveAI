import os


class Config:
    pass


class DevConfig(Config):
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    if os.getenv("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    TESTING = False
    ROOT_PATH = "/my_app"


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    ROOT_PATH = "."


class ProdConfig(Config):
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    if os.getenv("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    TESTING = False
    ROOT_PATH = "/my_app"
