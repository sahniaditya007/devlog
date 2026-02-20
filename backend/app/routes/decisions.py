from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.decision import Decision, DecisionStatus
from app.models.project import Project
from app.schemas.decision import DecisionCreateSchema, DecisionUpdateSchema, StatusTransitionSchema
from app.schemas.decision_link import DecisionLinkCreateSchema
from app.services import decision_service

decisions_bp = Blueprint("decisions", __name__)

_create_schema = DecisionCreateSchema()
_update_schema = DecisionUpdateSchema()
_transition_schema = StatusTransitionSchema()
_link_create_schema = DecisionLinkCreateSchema()


def _get_decision_or_404(decision_id: int, user_id: int):
    """Return decision if it belongs to a project owned by user_id."""
    decision = db.session.get(Decision, decision_id)
    if not decision:
        return None, jsonify({"error": "Decision not found."}), 404
    project = db.session.get(Project, decision.project_id)
    if not project or project.owner_id != user_id:
        return None, jsonify({"error": "Access denied."}), 403
    return decision, None, None


@decisions_bp.get("/")
@jwt_required()
def list_decisions():
    user_id = int(get_jwt_identity())
    project_id = request.args.get("project_id", type=int)
    status_filter = request.args.get("status")
    tag_filter = request.args.get("tag")
    search = request.args.get("q", "").strip()

    query = (
        Decision.query
        .join(Project, Decision.project_id == Project.id)
        .filter(Project.owner_id == user_id)
    )

    if project_id:
        query = query.filter(Decision.project_id == project_id)
    if status_filter and status_filter in [s.value for s in DecisionStatus]:
        query = query.filter(Decision.status == DecisionStatus(status_filter))
    if search:
        like = f"%{search}%"
        query = query.filter(
            Decision.title.ilike(like) | Decision.context.ilike(like) | Decision.decision_text.ilike(like)
        )

    decisions = query.order_by(Decision.created_at.desc()).all()

    result = [decision_service.serialize_decision(d) for d in decisions]

    if tag_filter:
        result = [d for d in result if tag_filter.lower() in [t.lower() for t in d.get("tags", [])]]

    return jsonify(result), 200


@decisions_bp.post("/")
@jwt_required()
def create_decision():
    user_id = int(get_jwt_identity())
    try:
        data = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    project = db.session.get(Project, data["project_id"])
    if not project:
        return jsonify({"error": "Project not found."}), 404
    if project.owner_id != user_id:
        return jsonify({"error": "Access denied."}), 403

    decision = decision_service.create_decision(
        title=data["title"],
        context=data["context"],
        decision_text=data["decision_text"],
        consequences=data.get("consequences"),
        tags=data.get("tags", []),
        project_id=data["project_id"],
        author_id=user_id,
    )
    return jsonify(decision_service.serialize_decision(decision)), 201


@decisions_bp.get("/<int:decision_id>")
@jwt_required()
def get_decision(decision_id: int):
    user_id = int(get_jwt_identity())
    decision, err_response, err_code = _get_decision_or_404(decision_id, user_id)
    if err_response:
        return err_response, err_code
    return jsonify(decision_service.serialize_decision(decision)), 200


@decisions_bp.put("/<int:decision_id>")
@jwt_required()
def update_decision(decision_id: int):
    user_id = int(get_jwt_identity())
    decision, err_response, err_code = _get_decision_or_404(decision_id, user_id)
    if err_response:
        return err_response, err_code

    try:
        data = _update_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for field in ("title", "context", "decision_text", "consequences", "tags"):
        if field in data:
            setattr(decision, field, data[field])

    db.session.commit()
    return jsonify(decision_service.serialize_decision(decision)), 200


@decisions_bp.patch("/<int:decision_id>/status")
@jwt_required()
def transition_status(decision_id: int):
    user_id = int(get_jwt_identity())
    decision, err_response, err_code = _get_decision_or_404(decision_id, user_id)
    if err_response:
        return err_response, err_code

    try:
        data = _transition_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    try:
        decision = decision_service.transition_status(decision, data["status"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    return jsonify(decision_service.serialize_decision(decision)), 200


@decisions_bp.post("/<int:decision_id>/links")
@jwt_required()
def add_link(decision_id: int):
    user_id = int(get_jwt_identity())
    decision, err_response, err_code = _get_decision_or_404(decision_id, user_id)
    if err_response:
        return err_response, err_code

    try:
        data = _link_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    # Validate that target decision exists and belongs to the same user
    target_decision, target_err, target_code = _get_decision_or_404(data["target_id"], user_id)
    if target_err:
        return target_err, target_code

    try:
        decision_service.add_link(decision, data["target_id"], data["link_type"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    # Refresh the decision to include the new link in relationships
    db.session.refresh(decision)
    return jsonify(decision_service.serialize_decision(decision)), 201


@decisions_bp.delete("/<int:decision_id>")
@jwt_required()
def delete_decision(decision_id: int):
    user_id = int(get_jwt_identity())
    decision, err_response, err_code = _get_decision_or_404(decision_id, user_id)
    if err_response:
        return err_response, err_code

    db.session.delete(decision)
    db.session.commit()
    return jsonify({"message": "Decision deleted."}), 200
