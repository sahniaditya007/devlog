from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.decision import DecisionStatus


VALID_STATUSES = [s.value for s in DecisionStatus]
VALID_TAGS_MAX = 10


class DecisionCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    context = fields.Str(required=True, validate=validate.Length(min=1))
    decision_text = fields.Str(required=True, validate=validate.Length(min=1))
    consequences = fields.Str(load_default=None)
    tags = fields.List(fields.Str(validate=validate.Length(min=1, max=50)), load_default=list)
    project_id = fields.Int(required=True)

    @validates("tags")
    def validate_tags(self, value: list) -> None:
        if len(value) > VALID_TAGS_MAX:
            raise ValidationError(f"Maximum {VALID_TAGS_MAX} tags allowed.")


class DecisionUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    context = fields.Str(validate=validate.Length(min=1))
    decision_text = fields.Str(validate=validate.Length(min=1))
    consequences = fields.Str()
    tags = fields.List(fields.Str(validate=validate.Length(min=1, max=50)))

    @validates("tags")
    def validate_tags(self, value: list) -> None:
        if len(value) > VALID_TAGS_MAX:
            raise ValidationError(f"Maximum {VALID_TAGS_MAX} tags allowed.")


class StatusTransitionSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_STATUSES, error="Invalid status value."),
    )


class DecisionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    context = fields.Str(dump_only=True)
    decision_text = fields.Str(dump_only=True)
    consequences = fields.Str(dump_only=True)
    tags = fields.List(fields.Str(), dump_only=True)
    ai_summary = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    project_id = fields.Int(dump_only=True)
    author_id = fields.Int(dump_only=True)
    author_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    links = fields.List(fields.Dict(), dump_only=True)
