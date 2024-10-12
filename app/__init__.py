# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from .seeds import seed_natures,seed_beneficiaires,seed_modereglement

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')  # Créer un dossier 'uploads' dans le répertoire de votre application
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Définir le chemin de la base de données
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "../instance/protefinance.db")}'
app.config['SECRET_KEY'] = 'secret_key_here'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importez vos routes ici pour les rendre actives
from app import routes  # Cela charge les définitions de routes

# Créez les tables si elles n'existent pas déjà
with app.app_context():
    db.create_all()  # Crée les tables si elles n'existent pas
    seed_natures()  # Appelez la fonction de semence
    seed_beneficiaires()
    seed_modereglement()
