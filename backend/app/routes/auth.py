from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.user import User
from app.schemas.user import RegisterSchema, LoginSchema, UserSchema

auth_bp = Blueprint("auth", __name__)

_register_schema = RegisterSchema()
_login_schema = LoginSchema()
_user_schema = UserSchema()


@auth_bp.post("/register")
def register():
    try:
        data = _register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"errors": {"email": ["Email already registered."]}}), 409

    user = User(email=data["email"], name=data["name"])
    try:
        user.set_password(data["password"])
    except ValueError as exc:
        return jsonify({"errors": {"password": [str(exc)]}}), 422

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": _user_schema.dump(user)}), 201


@auth_bp.post("/login")
def login():
    try:
        data = _login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"errors": {"credentials": ["Invalid email or password."]}}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": _user_schema.dump(user)}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(_user_schema.dump(user)), 200
