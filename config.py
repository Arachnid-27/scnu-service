class Config:
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = '3369'

    def __init__(self):
        pass

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
