import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
    # 强制指定模板目录为项目根目录下的 templates
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    # 强制指定静态文件目录为项目根目录下的 static
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 确保上传目录存在
    upload_dir = os.path.join(static_dir, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    app.config['UPLOAD_FOLDER'] = upload_dir

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .movie import movie as movie_blueprint
    app.register_blueprint(movie_blueprint, url_prefix='/movie')

    return app