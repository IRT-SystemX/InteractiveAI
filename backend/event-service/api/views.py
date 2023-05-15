

from apiflask import APIBlueprint
from cab_common_auth.decorators import get_use_cases, protected
from flask.views import MethodView


from .models import EventModel
from .schemas import EventIn, EventOut
from .utils import UseCaseFactory
from .event_manager.rte_event_manager import RTEEventManager
from .event_manager.da_event_manager import DAEventManager
from .event_manager.orange_event_manager import OrangeEventManager
from .event_manager.sncf_event_manager import SNCFEventManager


api_bp = APIBlueprint("event-api", __name__, url_prefix="/api/v1")
use_case_factory = UseCaseFactory()
use_case_factory.register_use_case('DA', DAEventManager())
use_case_factory.register_use_case('RTE', RTEEventManager())
use_case_factory.register_use_case('ORANGE', OrangeEventManager())
use_case_factory.register_use_case('SNCF', SNCFEventManager())


class HealthCheck(MethodView):

    def get(self):
        return


class Events(MethodView):

    @api_bp.output(EventOut(many=True))
    @protected
    def get(self):
        """Get all events"""
        use_cases = get_use_cases()
        return EventModel.query.filter(EventModel.use_case.in_(use_cases))

    @api_bp.input(EventIn)
    @api_bp.output(EventOut, status_code=201)
    @protected
    def post(self, data):
        """Add an event"""
        use_case = data["use_case"]
        event_manager = use_case_factory.get_event_manager(use_case)
        event = event_manager.create_event(data)
        return event


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/events", view_func=Events.as_view("events"))
