
class Config:
    pass


class DevConfig(Config):
    TESTING = False
    ROOT_PATH = "/code"


class TestConfig(Config):
    TESTING = True
    ROOT_PATH = "."


class ProdConfig(Config):
    TESTING = False
    ROOT_PATH = "/code"
