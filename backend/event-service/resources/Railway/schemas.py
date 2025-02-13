# backend/event-service/resources/Railway/schemas.py

from apiflask.fields import Float, String, Dict, List, Integer
from apiflask.validators import OneOf
from api.schemas import MetadataSchema

class MetadataSchemaRailway(MetadataSchema):
    agent_id = String(allow_none=True, required=True)
    event_type = String(required=True)
    agent_position = List(
        Integer(allow_none=True), allow_none=True, default=None
    )
    delay = Integer(required=True)
    id_train = String(allow_none=True, required=True)
    malfunction_stop_position = List(Integer(allow_none=True), allow_none=True)
    num_rame = String(allow_none=True, default=None)
    tmp_rame = String(allow_none=True, default=None)
    travel_plan = List(Dict(), allow_none=True)
    longitude = Float(allow_none=True, default=None)
    latitude = Float(allow_none=True, default=None)
    simulation_name = String(allow_none=True, default=None)
