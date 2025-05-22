# backend/context-service/resources/Railway/schemas.py

from api.schemas import MetadataSchema
from apiflask.fields import Dict, String, List, Integer

class MetadataSchemaRailway(MetadataSchema):
    trains = List(Dict(), required=False)
    list_of_target = Dict(required=False)
    direction_agents = List(Integer(), required=False)
    position_agents = Dict(required=False)
