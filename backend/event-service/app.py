
from api.models import db
from api.views import api_bp
from apiflask import APIFlask
import config


def create_app(config_mode):
    app = APIFlask("event-service")

    app.register_blueprint(api_bp)
    app.config.from_object(config_mode)
    db.init_app(app)
    db.create_all(app=app)
    return app


if __name__ == "__main__":
    app = create_app(config.DevConfig)
