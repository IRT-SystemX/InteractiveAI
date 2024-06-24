from api.models import db
from api.utils import UseCaseFactory, load_usecases_db
from api.views import api_bp
from apiflask import APIFlask
from settings import logger

from config import DevConfig, ProdConfig, TestConfig

config_mapping = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}


def create_app(config_mode):
    logger.info(f"starting recommendation-service in {config_mode} mode")
    app = APIFlask("recommendation-service")
    app.register_blueprint(api_bp)
    app.config.from_object(config_mapping.get(config_mode, DevConfig))

    # Create the application context
    app_ctx = app.app_context()
    app_ctx.push()

    # intiate database
    db.init_app(app)
    db.create_all()

    # add use_case_factory
    use_case_factory = UseCaseFactory()

    # Load use cases from the database
    load_usecases_db(use_case_factory)

    app.use_case_factory = use_case_factory

    return app


if __name__ == "__main__":
    app = create_app("dev")
    # Clean up the application context when you're done
    app_ctx = app.app_context()
    app_ctx.pop()
