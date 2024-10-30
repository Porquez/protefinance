from flask import Flask, request, abort
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from .extensions import db, bcrypt  # Importer db et bcrypt depuis extensions.py
from flask_login import LoginManager
import os

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', f'sqlite:///{os.path.join(app.root_path, "../instance/protefinance.db")}')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Définir le filtre sum avant l'initialisation de l'application
def sum_filter(values):
    return sum(values)

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

# Enregistrer le filtre dans l'environnement Jinja
app.jinja_env.filters['sum'] = sum_filter

# Définir les adresses IP autorisées
ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '44.226.145.213,54.187.200.255,34.213.214.55,35.164.95.156,44.230.95.183,44.229.200.200').split(',')

@app.before_request
def limit_remote_addr():
    # Vérifier si l'adresse IP du client est dans la liste des adresses autorisées
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)  # Interdit si l'adresse IP n'est pas dans la liste

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# Enregistrer les blueprints et créer les tables
with app.app_context():
    from app.routes.routes_signup import routes_signup
    from .routes.routes import main_blueprint
    from .routes.routes_login import routes_login
    from .routes.routes_budget import routes_budget
    app.register_blueprint(main_blueprint)
    app.register_blueprint(routes_login)
    app.register_blueprint(routes_signup)
    app.register_blueprint(routes_budget)

    db.create_all()
