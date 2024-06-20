from apiflask.fields import (
    Float,
    String,
    Dict
)
from apiflask.validators import OneOf
from api.schemas import MetadataSchema


class MetadataSchemaRTE(MetadataSchema):
    event_type = String(
        required=True,
        validate=OneOf(["KPI", "anticipation", "agent", "consignation"]),
    )
    creation_date = String(required=True)
    zone = String(validate=OneOf(["Est", "Ouest", "Centre"]))
    line = String(required=True)
    flux = Float()
    kpis = Dict(required=True)
    event_context = String()
