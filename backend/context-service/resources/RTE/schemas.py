from api.schemas import MetadataSchema
from apiflask.fields import Dict, String


class MetadataSchemaRTE(MetadataSchema):
    topology = String(allow_none=False)
    observation = Dict(allow_none=False)
