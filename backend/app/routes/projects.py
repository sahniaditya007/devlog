from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.project import Project
from app.schemas.project import ProjectCreateSchema, ProjectSchema

projects_bp = Blueprint("projects", __name__)

_create_schema = ProjectCreateSchema()
_project_schema = ProjectSchema()


def _get_project_or_404(project_id: int, user_id: int):
    project = db.session.get(Project, project_id)
    if not project:
        return None, jsonify({"error": "Project not found."}), 404
    if project.owner_id != user_id:
        return None, jsonify({"error": "Access denied."}), 403
    return project, None, None


@projects_bp.get("/")
@jwt_required()
def list_projects():
    user_id = int(get_jwt_identity())
    projects = Project.query.filter_by(owner_id=user_id).order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        data = _project_schema.dump(p)
        data["decision_count"] = p.decisions.count()
        result.append(data)
    return jsonify(result), 200


@projects_bp.post("/")
@jwt_required()
def create_project():
    user_id = int(get_jwt_identity())
    try:
        data = _create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    project = Project(name=data["name"], description=data.get("description"), owner_id=user_id)
    db.session.add(project)
    db.session.commit()

    result = _project_schema.dump(project)
    result["decision_count"] = 0
    return jsonify(result), 201


@projects_bp.get("/<int:project_id>")
@jwt_required()
def get_project(project_id: int):
    user_id = int(get_jwt_identity())
    project, err_response, err_code = _get_project_or_404(project_id, user_id)
    if err_response:
        return err_response, err_code

    result = _project_schema.dump(project)
    result["decision_count"] = project.decisions.count()
    return jsonify(result), 200


@projects_bp.put("/<int:project_id>")
@jwt_required()
def update_project(project_id: int):
    user_id = int(get_jwt_identity())
    project, err_response, err_code = _get_project_or_404(project_id, user_id)
    if err_response:
        return err_response, err_code

    try:
        data = _create_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if "name" in data:
        project.name = data["name"]
    if "description" in data:
        project.description = data["description"]

    db.session.commit()
    result = _project_schema.dump(project)
    result["decision_count"] = project.decisions.count()
    return jsonify(result), 200


@projects_bp.delete("/<int:project_id>")
@jwt_required()
def delete_project(project_id: int):
    user_id = int(get_jwt_identity())
    project, err_response, err_code = _get_project_or_404(project_id, user_id)
    if err_response:
        return err_response, err_code

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted."}), 200
