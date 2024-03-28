from api.models import db
from api.views import api_bp
from apiflask import APIFlask
from settings import logger

from config import DevConfig, ProdConfig, TestConfig

config_mapping = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}


def create_app(config_mode):
    logger.info(f"starting historic-service in {config_mode} mode")
    app = APIFlask("historic-service")
    app.register_blueprint(api_bp)
    app.config.from_object(config_mapping.get(config_mode, DevConfig))
    # Create the application context
    app_ctx = app.app_context()
    app_ctx.push()

    # intiate database
    db.init_app(app)
    db.create_all(app=app)

    return app


if __name__ == "__main__":
    app = create_app("dev")
    # Clean up the application context when you"re done
    app_ctx = app.app_context()
    app_ctx.pop()
