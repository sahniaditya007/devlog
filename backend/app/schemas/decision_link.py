from marshmallow import Schema, fields, validate
from app.models.decision_link import DecisionLink


class DecisionLinkCreateSchema(Schema):
    target_id = fields.Int(required=True)
    link_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            list(DecisionLink.VALID_LINK_TYPES),
            error="link_type must be one of: supersedes, relates_to, blocked_by",
        ),
    )


class DecisionLinkSchema(Schema):
    id = fields.Int(dump_only=True)
    source_id = fields.Int(dump_only=True)
    target_id = fields.Int(dump_only=True)
    link_type = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    target_title = fields.Str(dump_only=True)
    source_title = fields.Str(dump_only=True)
