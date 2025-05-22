# backend/context-service/resources/ATM/schemas.py

from api.schemas import MetadataSchema
from apiflask.fields import Dict, String

class MetadataSchemaATM(MetadataSchema):
    topology = String(allow_none=False)
    observation = Dict(allow_none=False)