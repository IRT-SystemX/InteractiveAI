from apiflask.fields import (
    Float,
    String
)
from apiflask.validators import OneOf
from api.schemas import MetadataSchema


class MetadataSchemaRTE(MetadataSchema):
    event_type = String(
        required=True,
        validate=OneOf(["KPI", "anticipation", "agent", "consignation"]),
    )
    zone = String(validate=OneOf(["Est", "Ouest", "Centre"]))
    line = String(required=True)
    flux = Float()
