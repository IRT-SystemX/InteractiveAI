# backend/context-service/resources/ATM/schemas.py

from api.schemas import MetadataSchema
from apiflask.fields import Dict, String, Float, List, Integer
from apiflask import Schema, fields
from marshmallow import pre_load
class PlaneMetadataSchemaATM(MetadataSchema):
    id_plane = String()
    ApDest = Dict()
    Current_airspeed = Float()
    Latitude = Float()
    Longitude = Float()
    wpList = List(Dict())

class MetadataSchemaATM(MetadataSchema):
    airplanes = List(fields.Nested(PlaneMetadataSchemaATM), required=True)
    
    # Backward compatibility: optional fields for the single airplane case
    ApDest = Dict(required=False)
    Current_airspeed = Float(required=False)
    Latitude = Float(required=False)
    Longitude = Float(required=False)
    wpList = List(Dict(), required=False)

    @pre_load
    def handle_backward_compatibility(self, data, **kwargs):
        # If the new 'airplanes' field is not provided, assume the old format.
        if 'airplanes' not in data:
            airplane = {}
            for field in ['ApDest', 'Current_airspeed', 'Latitude', 'Longitude', 'wpList']:
                if field in data:
                    airplane[field] = data[field]
            # Provide a default id_plane if not present.
            airplane.setdefault('id_plane', "X")
            data['airplanes'] = [airplane]
        return data