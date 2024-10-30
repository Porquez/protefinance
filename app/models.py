from datetime import datetime
from app import db

# Modéle de base de données pour stocker les informations d'identification des utilisateurs
from flask_bcrypt import Bcrypt

from flask_login import UserMixin

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verification_code = db.Column(db.String(6), nullable=True)  # Stocke le code de vérification

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
        
class UserConnection(db.Model):
    __tablename__ = 'UserConnections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # Relation avec la table User
    user = db.relationship('User', backref='connections')       # Relation pour accéder a l'utilisateur associé a la connexion
    machine_name = db.Column(db.String(100))
    ip_address = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    login_url = db.Column(db.String(200))
    status = db.Column(db.String(20))
    error_message = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReleveCompte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compte_id = db.Column(db.Integer, db.ForeignKey('compte.id'), nullable=False)  # Lien avec le compte
    date_operation = db.Column(db.DateTime, nullable=False)  # Date de l'opération
    designation = db.Column(db.String(100), nullable=False)  # Désignation de l'opération
    debit = db.Column(db.Float, nullable=True)  # Montant débit
    credit = db.Column(db.Float, nullable=True)  # Montant crédit
    nature_id = db.Column(db.Integer, db.ForeignKey('nature.id'), nullable=True)  # Lien avec la nature

    compte = db.relationship('Compte', backref='releves')  # Relation inverse avec Compte
    nature = db.relationship('Nature', backref='releves', lazy=True)  # Relation avec Nature

    def __repr__(self):
        return f'<ReleveCompte {self.designation}, Date: {self.date_operation}, Debit: {self.debit}, Credit: {self.credit}>'

class Banque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    code_postal = db.Column(db.String(10), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    identifiant_client = db.Column(db.String(100), nullable=True)
    nom_conseiller = db.Column(db.String(100), nullable=True)
    
    comptes = db.relationship('Compte', backref='banque', lazy=True)

class Compte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_personne_protegee = db.Column(db.String(100), nullable=False)
    rib = db.Column(db.String(34), nullable=True)  # RIB/IBAN
    type_compte = db.Column(db.String(50), nullable=True)  # Exemple: "Compte Courant", "Compte Epargne"
    solde_initial = db.Column(db.Float, nullable=True)  # Solde initial du compte
    numero_compte = db.Column(db.String(20), nullable=True)
    banque_id = db.Column(db.Integer, db.ForeignKey('banque.id'), nullable=True)  # Relation avec la banque
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    operations = db.relationship('Operation', backref='compte', lazy=True)

    # Méthode pour calculer le solde actuel du compte
    def solde_actuel(self):
        total_recettes = sum(op.montant for op in self.operations if op.nature.type_operation == 'recette')
        total_depenses = sum(op.montant for op in self.operations if op.nature.type_operation == 'depense')
        return self.solde_initial + total_recettes - total_depenses

    def dernieres_operations(self, limite=10):  # Correction of the limit parameter to a realistic value
        return Operation.query.filter_by(compte_id=self.id).order_by(Operation.date.desc()).limit(limite).all()

class Nature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)  # Ex: "Courses", "Loyer"
    type_operation = db.Column(db.Enum('recette', 'depense'), nullable=False)

    operations = db.relationship('Operation', backref='nature', lazy=True)

    def __repr__(self):
        return f'<Nature {self.nom}, Type: {self.type_operation}>'

class Beneficiaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(15), nullable=False)

    operations = db.relationship('Operation', backref='beneficiaire', lazy=True)

    def __repr__(self):
        return f'<Beneficiaire {self.nom}, Ville: {self.ville}>'

class ModeReglement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

    operations = db.relationship('Operation', backref='mode_reglement', lazy=True)

    def __repr__(self):
        return f'<ModeReglement {self.nom}>'

class PieceJustificative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fichier = db.Column(db.String(100), nullable=False)  # Nom du fichier (ex : facture_01.pdf)
    chemin = db.Column(db.String(255), nullable=False)  # Chemin d'accès au fichier sur le serveur
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'), nullable=False)  # Lien avec l'opération

    def __repr__(self):
        return f'<PieceJustificative {self.nom_fichier}>'

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    compte_id = db.Column(db.Integer, db.ForeignKey('compte.id'))
    nature_id = db.Column(db.Integer, db.ForeignKey('nature.id'))
    beneficiaire_id = db.Column(db.Integer, db.ForeignKey('beneficiaire.id'))
    modereglement_id = db.Column(db.Integer, db.ForeignKey('mode_reglement.id'))
    designation = db.Column(db.String(100), nullable=False)
    numero_piece = db.Column(db.String(100), nullable=True)
    pieces_justificatives = db.relationship('PieceJustificative', backref='operation', lazy=True)
    pointage_id = db.Column(db.Integer, db.ForeignKey('releve_compte.id'))  # Lien vers le relevé bancaire correspondant

    def est_pointee(self):
        return self.pointage_id is not None

    def __repr__(self):
        return f'<Operation {self.designation}, Montant: {self.montant}, Date: {self.date}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    societe = db.Column(db.String(150))
    adresse = db.Column(db.String(255))
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    numero_finess = db.Column(db.String(20))
    reference_client = db.Column(db.String(50))
    categorie = db.Column(db.String(50), nullable=False)  # Médecin, Pharmacie, etc.

    def __repr__(self):
        return f'<Contact {self.nom}>'
