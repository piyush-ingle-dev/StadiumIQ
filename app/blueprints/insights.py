"""Operational intelligence routes: real-time decision support.

Provides a control-room view combining crowd, staffing, and
sustainability data into one snapshot, an AI-generated briefing, and a
live server-sent-events stream so the dashboard updates without the
user refreshing the page.
"""

from __future__ import annotations

import json
import time

from flask import Blueprint, Response, jsonify, render_template, stream_with_context
from flask_login import login_required

from app.services import insights_service
from app.utils.decorators import role_required

bp = Blueprint("insights", __name__, url_prefix="/insights")

# How long a single SSE connection stays open before it closes and lets
# the browser's EventSource reconnect. Keeping this bounded avoids a
# single client holding a worker thread/process open indefinitely on
# a free-tier deployment.
_STREAM_DURATION_SECONDS = 60
_STREAM_INTERVAL_SECONDS = 5


@bp.route("/")
@login_required
@role_required("volunteer", "admin")
def index():
    """Render the operational intelligence control-room dashboard."""
    return render_template("insights.html")


@bp.route("/api/snapshot")
@login_required
@role_required("volunteer", "admin")
def snapshot():
    """Return the current cross-domain operations snapshot as JSON."""
    return jsonify(insights_service.build_snapshot())


@bp.route("/api/briefing")
@login_required
@role_required("volunteer", "admin")
def briefing():
    """Return an AI-generated (or rule-based fallback) operations briefing."""
    current_snapshot = insights_service.build_snapshot()
    text = insights_service.generate_briefing(current_snapshot)
    return jsonify({"snapshot": current_snapshot, "briefing": text})


@bp.route("/api/stream")
@login_required
@role_required("volunteer", "admin")
def stream():
    """Stream live operations snapshots as Server-Sent Events.

    The browser's EventSource API consumes this directly and
    reconnects automatically once the bounded stream below ends,
    giving continuous "real-time" updates without manual polling.
    """

    @stream_with_context
    def event_stream():
        elapsed = 0
        while elapsed < _STREAM_DURATION_SECONDS:
            current_snapshot = insights_service.build_snapshot()
            payload = json.dumps(current_snapshot)
            yield f"data: {payload}\n\n"
            time.sleep(_STREAM_INTERVAL_SECONDS)
            elapsed += _STREAM_INTERVAL_SECONDS

    return Response(event_stream(), mimetype="text/event-stream")
