# backend/event-service/resources/ATM/schemas.py

from apiflask.fields import Float, String, Dict
from apiflask.validators import OneOf
from api.schemas import MetadataSchema

class MetadataSchemaATM(MetadataSchema):
    event_type = String(required=True)
    system = String(required=True)
    id_plane = String(required=True)