"""Local development entry point. Run with: python run.py"""

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402

app = create_app("development")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
