
class Config:
    pass


class DevConfig(Config):
    TESTING = False
    ROOT_PATH = "/my_app"


class TestConfig(Config):
    TESTING = True
    ROOT_PATH = "."


class ProdConfig(Config):
    TESTING = False
    ROOT_PATH = "/my_app"
