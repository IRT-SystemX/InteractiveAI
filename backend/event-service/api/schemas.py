from apiflask import Schema
from apiflask.fields import (
    DateTime,
    Dict,
    Float,
    Integer,
    String,
    Boolean,
    List,
)
from apiflask.validators import Length, OneOf
from marshmallow import ValidationError, validates_schema


class Metadata(Schema):
    pass


class MetadataRTE(Metadata):
    event_type = String(
        required=True,
        validate=OneOf(["KPI", "anticipation", "agent", "consignation"]),
    )
    zone = String(validate=OneOf(["Est", "Ouest", "Centre"]))
    line = String(required=True)
    flux = Float()


class MetadataSNCF(Metadata):
    agent_id = String(required=True)
    event_type = String(required=True)
    agent_position = List(Integer())
    delay = Integer(required=True)
    id_train = String(required=True)
    malfunction_stop_position = List(Integer())
    num_rame = String()
    tmp_rame = String()


class MetadataOrange(Metadata):
    event_type = String(required=True)
    id_app = String(required=True)
    bad_kpi = String(required=True)


class MetadataDA(Metadata):
    event_type = String(required=True)
    system = String(required=True)


class EventIn(Schema):
    use_case = String(
        required=True, validate=OneOf(["RTE", "SNCF", "DA", "ORANGE"])
    )
    title = String(required=True, validate=Length(1, 255))
    description = String(required=True, validate=Length(1, 255))
    start_date = DateTime(format="iso", allow_none=True)
    end_date = DateTime(format="iso", allow_none=True)
    criticality = String(
        required=True,
        validate=OneOf(["ND", "HIGH", "MEDIUM", "LOW", "ROUTINE"]),
    )
    data = Dict()
    is_active = Boolean()

    @property
    def _metadata_loaders(self):
        return {
            "RTE": MetadataRTE,
            "SNCF": MetadataSNCF,
            "ORANGE": MetadataOrange,
            "DA": MetadataDA,
        }

    @validates_schema
    def validate_metadata(self, data, **kwargs):
        use_case = data.get("use_case")
        metadata = data.get("data")
        if use_case in self._metadata_loaders:
            self._metadata_loaders[use_case]().load(metadata)
            return
        raise ValidationError("Invalid use case")


class EventOut(Schema):
    id = Integer()
    id_event = String()
    of_uid = String()
    use_case = String()
    title = String()
    description = String()
    start_date = DateTime(format="iso", allow_none=True)
    end_date = DateTime(format="iso", allow_none=True)
    criticality = String()
    data = Dict()
    is_active = Boolean()
