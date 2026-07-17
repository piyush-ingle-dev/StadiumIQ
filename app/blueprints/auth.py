"""Authentication routes: register, login, logout."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.extensions import db, limiter
from app.models import User
from app.utils.security import clean_text

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    """Register a new fan/volunteer account."""
    if request.method == "POST":
        name = clean_text(request.form.get("name", ""), max_length=120)
        email = clean_text(request.form.get("email", ""), max_length=255).lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "fan")
        if role not in ("fan", "volunteer"):
            role = "fan"

        if not name or not email or len(password) < 8:
            flash("Please provide a name, valid email, and a password of at least 8 characters.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first() is not None:
            flash("An account with that email already exists.", "error")
            return render_template("auth/register.html")

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Welcome to StadiumIQ!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per hour")
def login():
    """Authenticate an existing user."""
    if request.method == "POST":
        email = clean_text(request.form.get("email", ""), max_length=255).lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    """Log the current user out."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
