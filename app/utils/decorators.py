"""Role-based access control decorator.

Centralizes the "only these roles may access this route" pattern that
was previously duplicated as inline checks inside individual route
handlers (`app/blueprints/staff.py`, `app/blueprints/sustainability.py`).
Using one decorator means the access rule is defined once, is easy to
audit, and can't drift out of sync between routes.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from flask import abort
from flask_login import current_user


def role_required(*allowed_roles: str) -> Callable:
    """Restrict a view to users whose role is in `allowed_roles`.

    Must be combined with `@login_required` (or placed after it) so
    `current_user` is guaranteed to be authenticated before the role
    check runs.

    Args:
        *allowed_roles: One or more role strings that may access the
            decorated view, e.g. role_required("volunteer", "admin").

    Returns:
        A decorator that aborts with 403 for any other role.

    Example:
        @bp.route("/staff/api/tasks", methods=["POST"])
        @login_required
        @role_required("volunteer", "admin")
        def create_task():
            ...
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
