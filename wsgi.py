"""WSGI entry point used by gunicorn in production (Render)."""

from app import create_app

app = create_app("production")

if __name__ == "__main__":
    app.run()
