import re
from utils.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_fields(data, fields):
    """Raise ValidationError if any required field is missing or empty."""
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def validate_email(email):
    if not EMAIL_RE.match(email or ""):
        raise ValidationError("Invalid email address")


def validate_password(password):
    if not password or len(password) < 6:
        raise ValidationError("Password must be at least 6 characters")


def parse_float(value, field_name, default=None, min_value=None):
    if value is None or value == "":
        if default is not None:
            return default
        raise ValidationError(f"{field_name} is required")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number")
    if min_value is not None and result < min_value:
        raise ValidationError(f"{field_name} must be >= {min_value}")
    return result


def parse_int(value, field_name, default=None, min_value=None):
    if value is None or value == "":
        if default is not None:
            return default
        raise ValidationError(f"{field_name} is required")
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be an integer")
    if min_value is not None and result < min_value:
        raise ValidationError(f"{field_name} must be >= {min_value}")
    return result
