# import os

# from api.models import db
from api.views import api_bp
from apiflask import APIFlask


def create_app():
    app = APIFlask("recommendation-service")

    app.register_blueprint(api_bp)
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db.init_app(app)
    # db.create_all(app=app)
    return app


if __name__ == "__main__":
    app = create_app()
