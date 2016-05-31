from flask import Flask
from config import config
import redis

rdb = redis.StrictRedis()


def create_app(optional='default'):
    app = Flask(__name__)
    app.config.from_object(config[optional])
    config[optional].init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .scholat import scholat as scholat_blueprint
    app.register_blueprint(scholat_blueprint, url_prefix="/scholat")

    from .library import library as library_blueprint
    app.register_blueprint(library_blueprint, url_prefix='/library')

    from .jwc import jwc as jwc_blueprint
    app.register_blueprint(jwc_blueprint, url_prefix='/jwc')

    from .score import score as score_blueprint
    app.register_blueprint(score_blueprint, url_prefix='/score')

    return app
