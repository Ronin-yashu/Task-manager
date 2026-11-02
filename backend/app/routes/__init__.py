from .auth import bp as auth_bp
from .users import bp as users_bp
from .tasks import bp as tasks_bp

all_blueprints = [auth_bp, users_bp, tasks_bp]