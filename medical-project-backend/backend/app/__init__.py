import atexit
from flask import Flask, jsonify, request, Response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException
from .routes.patients import patients_bp
from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.medical_history import history_bp
from .routes.visits import visits_bp
from .docs import docs_bp
from .routes.doctors import doctors_bp
from .routes.establishments import establishments_bp
from .routes.coordinates import coordinates_bp
from .routes.parents import parents_bp
from .routes.mfa import mfa_bp
from .config import Config
from flask_bcrypt import Bcrypt
from .db import Database
from .models import ErrorResponse
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import datetime
from .services.token_service import is_token_blacklisted


def create_app(config_file: str = "config.toml", use_test_db: bool = False):
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "skip_zrok_interstitial"]
        }
    })

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            res = Response()
            res.headers['X-Content-Type-Options'] = '*'
            return res

    bcrypt = Bcrypt(app)
    app.config['BCRYPT'] = bcrypt

    load_dotenv()

    if use_test_db:
        user = os.getenv("INF6150_TEST_DATABASE_USER")
        password = os.getenv("INF6150_TEST_DATABASE_PASSWORD")

        in_container = os.getenv(
            "INF6150_SERVER_IN_CONTAINER", 'True').lower() in ('true', '1', 't')
        if in_container:
            host = os.getenv("INF6150_TEST_DATABASE_DOCKER_HOST")
            port = os.getenv("INF6150_TEST_DATABASE_DOCKER_PORT")
        else:
            host = os.getenv("INF6150_TEST_DATABASE_HOST")
            port = os.getenv("INF6150_TEST_DATABASE_PORT")

        database = os.getenv("INF6150_TEST_DATABASE_NAME")
        app.config['TESTING'] = True
    else:
        user = os.getenv("INF6150_DATABASE_USER")
        password = os.getenv("INF6150_DATABASE_PASSWORD")

        in_container = os.getenv(
            "INF6150_SERVER_IN_CONTAINER", 'True').lower() in ('true', '1', 't')
        if in_container:
            host = os.getenv("INF6150_DATABASE_DOCKER_HOST")
            port = os.getenv("INF6150_DATABASE_DOCKER_PORT")
        else:
            host = os.getenv("INF6150_DATABASE_HOST")
            port = os.getenv("INF6150_DATABASE_PORT")

        database = os.getenv("INF6150_DATABASE_NAME")

    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']

    app.config['JWT_HEADER_NAME'] = 'Authorization'

    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    app.config['JWT_COOKIE_SECURE'] = os.getenv("INF6150_JWT_COOKIE_SECURE")
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # Enable CSRF protection

    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    app.config['JWT_REFRESH_TOKEN_EXPIRES_DAYS'] = int(
        os.getenv("INF6150_JWT_REFRESH_EXPIRATION_DAYS", "30"))

    app.config['JWT_SECRET_KEY'] = os.getenv("INF6150_JWT_SECRET_KEY")
    token_expiry_days = int(os.getenv("INF6150_JWT_EXPIRATION_DAYS", "1"))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(
        days=token_expiry_days)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return is_token_blacklisted(jti)

    # Optional: Handle expired or invalid tokens
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'error': 'Token has expired',
            'message': 'Please log in again'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'status': 'error',
            'error': 'Invalid token',
            'message': 'Signature verification failed'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'status': 'error',
            'error': 'Authorization required',
            'message': 'Request does not contain a token'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'status': 'error',
            'error': 'Token has been revoked',
            'message': 'Please log in again'
        }), 401

    db_instance = Database(user, password, host, port, database)
    app.config['DATABASE'] = db_instance

    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(
        history_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(
        visits_bp, url_prefix='/api')
    app.register_blueprint(
        coordinates_bp, url_prefix='/api')
    app.register_blueprint(
        parents_bp, url_prefix='/api')
    app.register_blueprint(doctors_bp, url_prefix='/api/doctors')
    app.register_blueprint(establishments_bp, url_prefix='/api/establishments')
    app.register_blueprint(docs_bp, url_prefix='/')
    app.register_blueprint(mfa_bp, url_prefix='/api/mfa')

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        error_response = ErrorResponse(error=error.errors())
        return jsonify(error_response.model_dump()), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        error_response = ErrorResponse(error=error.description)
        return jsonify(error_response.model_dump()), error.code

    @app.errorhandler(Exception)
    def handle_exception(error):
        error_response = ErrorResponse(error=str(error))
        return jsonify(error_response.model_dump()), 500

    atexit.register(db_instance.close_pool)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Docker healthcheck"""
        try:
            with db_instance.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    return app
