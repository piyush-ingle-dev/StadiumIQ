"""Multilingual translation assistance routes."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import login_required

from app.services.ai_service import get_translation
from app.utils.security import clean_text, is_valid_language_code

bp = Blueprint("multilingual", __name__, url_prefix="/multilingual")


@bp.route("/")
@login_required
def index():
    """Render the multilingual assistance page."""
    return render_template(
        "multilingual.html", languages=current_app.config["SUPPORTED_LANGUAGES"]
    )


@bp.route("/api/translate", methods=["POST"])
@login_required
def translate():
    """Translate free text into one of the supported languages.

    Expects JSON body: {"text": str, "target_language": str}
    """
    data = request.get_json(silent=True) or {}
    text = clean_text(data.get("text", ""), max_length=1000)
    target_language = clean_text(data.get("target_language", ""), max_length=5)

    supported = current_app.config["SUPPORTED_LANGUAGES"]
    if not text:
        return jsonify({"error": "text is required."}), 400
    if not is_valid_language_code(target_language, supported):
        return jsonify({"error": f"target_language must be one of {supported}."}), 400

    translated = get_translation(text, target_language)
    return jsonify({"original": text, "target_language": target_language, "translated": translated})
