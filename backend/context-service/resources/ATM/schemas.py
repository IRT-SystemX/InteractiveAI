# backend/context-service/resources/ATM/schemas.py

from api.schemas import MetadataSchema
from apiflask.fields import Dict, String, Float, List, Integer
class MetadataSchemaATM(MetadataSchema):
    ApDest = Dict()
    Current_airspeed = Float()
    Latitude = Float()
    Longitude = Float()
    wpList = List(Dict())
    id_plane = Integer()
