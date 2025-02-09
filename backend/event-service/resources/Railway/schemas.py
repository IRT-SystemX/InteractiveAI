# backend/event-service/resources/Railway/schemas.py

from apiflask.fields import Float, String, Dict
from apiflask.validators import OneOf
from api.schemas import MetadataSchema

class MetadataSchemaRailway(MetadataSchema):
    event_type = String(
        required=True,
        validate=OneOf(["KPI", "anticipation", "agent", "consignation"]),
    )
    creation_date = String()
    zone = String(validate=OneOf(["Est", "Ouest", "Centre"]))
    line = String(required=True)
    flux = Float()
    kpis = Dict(required=True)
    event_context = String()