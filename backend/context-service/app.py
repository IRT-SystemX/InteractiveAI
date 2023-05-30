from api.context_manager.da_context_manager import DAContextManager
from api.context_manager.orange_context_manager import OrangeContextManager
from api.context_manager.rte_context_manager import RTEContextManager
from api.context_manager.sncf_context_manager import SNCFContextManager
from api.models import db
from api.utils import UseCaseFactory
from api.views import api_bp
from apiflask import APIFlask
from settings import logger

from config import DevConfig, ProdConfig, TestConfig

config_mapping = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}


def create_app(config_mode):
    logger.info(f"starting context-service in {config_mode} mode")
    app = APIFlask("context-service")
    app.register_blueprint(api_bp)
    app.config.from_object(config_mapping.get(config_mode, DevConfig))
    # Create the application context
    app_ctx = app.app_context()
    app_ctx.push()
    # add use_case_factory
    use_case_factory = UseCaseFactory()
    use_case_factory.register_use_case('DA', DAContextManager())
    use_case_factory.register_use_case('RTE', RTEContextManager())
    use_case_factory.register_use_case('ORANGE', OrangeContextManager())
    use_case_factory.register_use_case('SNCF', SNCFContextManager())
    app.use_case_factory = use_case_factory
    # intiate database
    db.init_app(app)
    db.create_all(app=app)
    return app


if __name__ == "__main__":
    app = create_app("dev")
    # Clean up the application context when you're done
    app_ctx = app.app_context()
    app_ctx.pop()