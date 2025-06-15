# Инициализация Flask-приложения и регистрация blueprints

from flask import Flask
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)

    # Включение CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # Разрешить запросы с любых источников к /api/*

    # Конфигурация
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Ограничение размера файла 16MB
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Регистрация blueprints
    from app.routes.api import api_bp
    from app.routes.web import web_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)

    return app