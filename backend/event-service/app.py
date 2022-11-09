from apiflask import APIFlask

from .api.views import api_bp

app = APIFlask("event-service")

app.register_blueprint(api_bp)
