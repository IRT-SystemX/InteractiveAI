import config
from api.views import api_bp
from apiflask import APIFlask
from api.utils import UseCaseFactory
from api.recommendation_manager.da_manager import DAManager
from api.recommendation_manager.rte_manager import RTEManager
from api.recommendation_manager.sncf_manager import SNCFManager

config_mapping = {
    'dev': config.DevConfig,
    'test': config.TestConfig,
    'prod': config.ProdConfig
}


def create_app(config_mode):
    app = APIFlask("recommendation-service")
    app.register_blueprint(api_bp)
    app.config.from_object(config_mapping.get(config_mode, config.DevConfig))
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
