from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import oauth
from .routes import all_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=[Config.FRONTEND_URL], supports_credentials=True)

    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app