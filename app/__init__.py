# app/__init__.py
from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from .extensions import db, bcrypt  # Importer db et bcrypt depuis extensions.py
from flask_login import LoginManager
import os

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', f'sqlite:///{os.path.join(app.root_path, "../instance/protefinance.db")}')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_here')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialiser les extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

# Configurer LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes_login.login'  

app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.secret_key = app.config['SECRET_KEY'] 
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Enregistrer les blueprints et créer les tables
with app.app_context():
    from app.routes.routes_signup import routes_signup
    from .routes.routes import main_blueprint
    from .routes.routes_login import routes_login
    app.register_blueprint(main_blueprint)
    app.register_blueprint(routes_login)
    app.register_blueprint(routes_signup)

    db.create_all()
