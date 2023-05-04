from apiflask import Schema
from apiflask.fields import DateTime, Dict, Float, Integer, String, Boolean
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema


class Metadata(Schema):
    pass


class MetadataRTE(Metadata):
    event_type = String(required=True, validate=OneOf(
        ['KPI', 'anticipation', 'agent', 'consignation']))
    zone = String(validate=OneOf(['Est', 'Ouest', 'Centre']))
    line = String()
    flux = Float()


class MetadataSNCF(Metadata):
    pass


class MetadataOrange(Metadata):
    pass


class MetadataDA(Metadata):
    pass


class EventIn(Schema):
    use_case = String(required=True, validate=OneOf(
        ['RTE', 'SNCF', 'DA', 'ORANGE']))
    title = String(required=True, validate=Length(1, 255))
    description = String(required=True, validate=Length(1, 255))
    date = DateTime(format="iso")
    criticality = String(required=True, validate=OneOf(
        ['ND', 'HIGH', 'MEDIUM', 'LOW', 'ROUTINE']))
    data = Dict()
    is_active = Boolean()

    @property
    def _metadata_loaders(self):
        return {
            'RTE': MetadataRTE,
            'SNCF': MetadataSNCF,
            'ORANGE': MetadataOrange,
            'DA': MetadataDA,
        }

    @validates_schema
    def validate_metadata(self, data, **kwargs):
        use_case = data.get("use_case")
        metadata = data.get("data")
        if use_case in self._metadata_loaders:
            self._metadata_loaders[use_case]().load(metadata)
        else:
            raise ValidationError("Invalid use case")


class EventOut(Schema):
    id = Integer()
    id_event = String()
    use_case = String()
    description = String()
    date = DateTime(format="iso")
    criticality = String()
    data = Dict()
    is_active = Boolean()
