from datetime import datetime
from app import db

class Compte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_personne_protegee = db.Column(db.String(100), nullable=False)
    rib = db.Column(db.String(34), nullable=True)  # RIB/IBAN
    type_compte = db.Column(db.String(50), nullable=True)  # Exemple: "Compte Courant", "Compte Epargne"
    solde_initial = db.Column(db.Float, nullable=True)  # Solde initial du compte
    banque = db.Column(db.String(100), nullable=True)  # Nom de la banque
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    operations = db.relationship('Operation', backref='compte', lazy=True)

    # Méthode pour calculer le solde actuel du compte
    def solde_actuel(self):
        total_recettes = sum(op.montant for op in self.operations if op.nature.type_operation == 'recette')
        total_depenses = sum(op.montant for op in self.operations if op.nature.type_operation == 'depense')
        return self.solde_initial + total_recettes - total_depenses

    def dernieres_operations(self, limite=5):
        return Operation.query.filter_by(compte_id=self.id).order_by(Operation.date.desc()).limit(limite).all()


class Nature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)  # Ex: "Courses", "Loyer"
    type_operation = db.Column(db.Enum('recette', 'depense'), nullable=False)

    operations = db.relationship('Operation', backref='nature', lazy=True)

class Beneficiaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(15), nullable=False)

    operations = db.relationship('Operation', backref='beneficiaire', lazy=True)

class ModeReglement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    # Ajoutez d'autres colonnes si nécessaire

    operations = db.relationship('Operation', backref='mode_reglement', lazy=True)

class PieceJustificative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fichier = db.Column(db.String(100), nullable=False)  # Nom du fichier (ex : facture_01.pdf)
    chemin = db.Column(db.String(255), nullable=False)  # Chemin d'accès au fichier sur le serveur
    operation_id = db.Column(db.Integer, db.ForeignKey('operation.id'), nullable=False)  # Lien avec l'opération

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    compte_id = db.Column(db.Integer, db.ForeignKey('compte.id'))
    nature_id = db.Column(db.Integer, db.ForeignKey('nature.id'))
    beneficiaire_id = db.Column(db.Integer, db.ForeignKey('beneficiaire.id'))
    modereglement_id = db.Column(db.Integer, db.ForeignKey('mode_reglement.id'))  
    designation = db.Column(db.String(100), nullable=False)  
    numero_piece = db.Column(db.String(100), nullable=True)  # Ajout du champ numero_piece
    pieces_justificatives = db.relationship('PieceJustificative', backref='operation', lazy=True)

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
