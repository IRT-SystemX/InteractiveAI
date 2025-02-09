# backend/context-service/resources/Railway/schemas.py

from api.schemas import MetadataSchema
from apiflask.fields import Dict, String

class MetadataSchemaRailway(MetadataSchema):
    topology = String(allow_none=False)
    observation = Dict(allow_none=False)