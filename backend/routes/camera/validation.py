"""Validation of camera source payloads sent by the frontend."""

from flask import jsonify


def validate_source(source):
    """Validate a camera source dict.

    Expected shapes:
        ``{"type": "local", "index": <non-negative int>, ...}``
        ``{"type": "remote", "url": "http(s)://...", ...}``

    Returns ``None`` when valid, otherwise a ``(response, 400)`` tuple that
    the route can return directly.
    """
    source_type = source.get("type")
    if not source_type:
        return jsonify({"error": "Source type is required"}), 400

    if source_type == "local":
        if "index" not in source:
            return jsonify({"error": "Camera index is required for local sources"}), 400
        if not isinstance(source["index"], int) or source["index"] < 0:
            return (
                jsonify({"error": "Camera index must be a non-negative integer"}),
                400,
            )
    elif source_type == "remote":
        if "url" not in source:
            return jsonify({"error": "URL is required for remote sources"}), 400
        if not source["url"].startswith(("http://", "https://")):
            return jsonify({"error": "URL must be a valid HTTP/HTTPS URL"}), 400
    else:
        return jsonify({"error": 'Source type must be either "local" or "remote"'}), 400

    return None
