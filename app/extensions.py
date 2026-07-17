"""Flask extension instances.

Extensions are instantiated here without an app bound to them, then
initialized inside the application factory (`app/__init__.py`). This
avoids circular imports between blueprints and the extensions they use.
"""

from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
