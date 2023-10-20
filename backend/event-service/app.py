
from api.event_manager.da_event_manager import DAEventManager
from api.event_manager.orange_event_manager import OrangeEventManager
from api.event_manager.rte_event_manager import RTEEventManager
from api.event_manager.sncf_event_manager import SNCFEventManager
from api.models import db
from api.utils import UseCaseFactory
from api.views import api_bp
from apiflask import APIFlask

from config import DevConfig, ProdConfig, TestConfig
from settings import logger

config_mapping = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}


def create_app(config_mode):
    logger.info(f"starting event-service in {config_mode} mode")
    app = APIFlask("event-service")
    app.register_blueprint(api_bp)
    app.config.from_object(config_mapping.get(config_mode, DevConfig))
    # Create the application context
    app_ctx = app.app_context()
    app_ctx.push()
    # add use_case_factory
    use_case_factory = UseCaseFactory()
    use_case_factory.register_use_case('DA', DAEventManager())
    use_case_factory.register_use_case('RTE', RTEEventManager())
    use_case_factory.register_use_case('SNCF', SNCFEventManager())
    use_case_factory.register_use_case('ORANGE', OrangeEventManager())
    app.use_case_factory = use_case_factory
    # intiate database
    db.init_app(app)
    db.create_all()
    return app


if __name__ == "__main__":
    app = create_app("dev")
    # Clean up the application context when you're done
    app_ctx = app.app_context()
    app_ctx.pop()
