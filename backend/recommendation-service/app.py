from .config import DevConfig, TestConfig, ProdConfig
from api.views import api_bp
from apiflask import APIFlask
from api.utils import UseCaseFactory
from api.recommendation_manager.da_manager import DAManager
from api.recommendation_manager.rte_manager import RTEManager
from api.recommendation_manager.sncf_manager import SNCFManager
from .settings import logger
config_mapping = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}


def create_app(config_mode):
    logger.info(f"starting recommendation-service in {config_mode} mode")
    app = APIFlask("recommendation-service")
    app.register_blueprint(api_bp)
    app.config.from_object(config_mapping.get(config_mode, DevConfig))
    # Create the application context
    app_ctx = app.app_context()
    app_ctx.push()
    # add use_case_factory
    use_case_factory = UseCaseFactory()
    use_case_factory.register_use_case('DA', DAManager())
    use_case_factory.register_use_case('RTE', RTEManager())
    use_case_factory.register_use_case('SNCF', SNCFManager())
    app.use_case_factory = use_case_factory

    return app


if __name__ == "__main__":
    app = create_app("dev")
    # Clean up the application context when you're done
    app_ctx = app.app_context()
    app_ctx.pop()
