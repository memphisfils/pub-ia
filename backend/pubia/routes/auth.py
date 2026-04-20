from __future__ import annotations

from typing import Any

from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from authlib.integrations.flask_client import OAuth

auth = Blueprint("auth", __name__, url_prefix="/auth")

oauth = OAuth()


def _get_google_auth() -> OAuth:
    """Initialize Google OAuth."""
    config = current_app.config
    oauth.register(
        name="google",
        client_id=config.get("GOOGLE_CLIENT_ID"),
        client_secret=config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth


@auth.route("/google")
def google_login() -> Any:
    """Redirect to Google OAuth2."""
    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI")
    return oauth.create_client("google").authorize_redirect(redirect_uri)


@auth.route("/google/callback")
def google_callback() -> Any:
    """Handle Google OAuth2 callback."""
    token = oauth.create_client("google").authorize_access_token()
    user_info = token.get("userinfo")
    if not user_info:
        return jsonify({"error": "Failed to get user info from Google"}), 400

    from sqlalchemy.orm import Session
    from sqlalchemy import select
    from pubia.models import User
    from pubia.services import DatabaseClient

    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    session = Session(bind=db_client.engine)
    try:
        # Find or create user
        stmt = select(User).where(User.google_id == user_info.get("sub"))
        user = session.execute(stmt).scalars().first()

        if not user:
            stmt = select(User).where(User.email == user_info.get("email"))
            user = session.execute(stmt).scalars().first()

        if not user:
            user = User(
                email=user_info.get("email"),
                name=user_info.get("name"),
                avatar_url=user_info.get("picture"),
                google_id=user_info.get("sub"),
                role="publisher",
                plan="free",
            )
            session.add(user)
            session.commit()
        else:
            # Update avatar if changed
            if user_info.get("picture"):
                user.avatar_url = user_info.get("picture")
            if user_info.get("name"):
                user.name = user_info.get("name")
            session.commit()

        # Set session
        from flask import session
        session["user_id"] = str(user.id)
        session["user_role"] = user.role

        return redirect(current_app.config.get("FRONTEND_URL", "/"))
    finally:
        session.close()


@auth.route("/logout", methods=["POST"])
def logout() -> tuple[Any, int]:
    """Logout user."""
    from flask import session
    session.pop("user_id", None)
    session.pop("user_role", None)
    return jsonify({"ok": True}), 200


@auth.route("/me")
def me() -> tuple[Any, int]:
    """Get current user profile."""
    from flask import session
    from sqlalchemy.orm import Session
    from sqlalchemy import select
    from pubia.models import User
    from pubia.services import DatabaseClient

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    db_client: DatabaseClient = current_app.extensions["pubia.database"]
    session_db = Session(bind=db_client.engine)
    try:
        stmt = select(User).where(User.id == user_id)
        user = session_db.execute(stmt).scalars().first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "role": user.role,
            "plan": user.plan,
        }), 200
    finally:
        session_db.close()
