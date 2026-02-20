"""Centralised error response helpers."""
from flask import jsonify


def error_response(message: str, status_code: int):
    return jsonify({"error": message}), status_code


def validation_error_response(errors: dict):
    return jsonify({"errors": errors}), 422
