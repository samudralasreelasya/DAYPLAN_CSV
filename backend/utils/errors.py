class AppError(Exception):
    """Base application error with an HTTP status code attached."""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self):
        body = dict(self.payload)
        body["error"] = self.message
        return body


class ValidationError(AppError):
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=422, payload=payload)


class UpstreamServiceError(AppError):
    """Raised when a free external API (OSRM, Overpass, etc.) fails or times out."""

    def __init__(self, service_name, detail="Service temporarily unavailable"):
        super().__init__(f"{service_name}: {detail}", status_code=502)


def register_error_handlers(app):
    from flask import jsonify

    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_405(err):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def handle_500(err):
        return jsonify({"error": "Internal server error"}), 500
