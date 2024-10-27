from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import DateField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models import Nature, Beneficiaire, Compte, ModeReglement, Contact

class PieceJustificativeForm(FlaskForm):
    fichiers = FileField('Ajouter des pièces justificatives', validators=[
        FileAllowed(['pdf', 'jpg', 'png'], 'Images ou documents uniquement!')
    ])
    submit = SubmitField('Ajouter la pièce justificative')

class ModeReglementForm(FlaskForm):
    mode = SelectField('Mode de Règlement', choices=[('espece', 'Espèce'), ('cheque', 'Chèque'), ('carte', 'Carte')])
    submit = SubmitField('Ajouter le Mode de Règlement')

class BeneficiaireForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    ville = StringField('Ville', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    submit = SubmitField('Ajouter le bénéficiaire')

class CompteForm(FlaskForm):
    nom_personne_protegee = StringField('Nom de la personne protégée', validators=[DataRequired()])
    rib = StringField('RIB/IBAN', validators=[DataRequired(), Length(min=14, max=34)])
    type_compte = SelectField('Type de compte', choices=[('Compte Courant', 'Compte Courant'), ('Compte Epargne', 'Compte Epargne')], validators=[DataRequired()])
    solde_initial = FloatField('Solde initial', validators=[DataRequired()])
    banque_id = SelectField('Banque', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Ajouter le compte')

class BanqueForm(FlaskForm):
    nom = StringField('Nom de la Banque', validators=[DataRequired()])
    adresse = StringField('Adresse', validators=[DataRequired()])
    code_postal = StringField('Code Postal', validators=[DataRequired()])
    ville = StringField('Ville', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    identifiant_client = StringField('Identifiant Client', validators=[Optional()])
    nom_conseiller = StringField('Nom Conseiller', validators=[Optional()])
    submit = SubmitField('Ajouter la Banque')

class NatureForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    type_operation = SelectField('Type d\'opération', choices=[('recette', 'Recette'), ('depense', 'Dépense')], validators=[DataRequired()])
    submit = SubmitField('Ajouter la nature')

class OperationForm(FlaskForm):
    montant = FloatField('Montant', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    nature = SelectField('Nature', coerce=int)
    modereglement = SelectField('Mode réglement', coerce=int)
    beneficiaire = SelectField('Bénéficiaire', coerce=int)
    designation = StringField('Désignation', validators=[DataRequired()])
    compte_id = SelectField('Compte', coerce=int)  
    numero_piece = StringField('Numéro de Pièce')  
    fichiers = FileField('Ajouter des pièces justificatives', validators=[FileAllowed(['pdf', 'jpg', 'png'], 'Images ou documents uniquement!')])
    submit = SubmitField('Ajouter Opération')

    def __init__(self, *args, **kwargs):
        super(OperationForm, self).__init__(*args, **kwargs)
        self.nature.choices = [(n.id, n.nom) for n in Nature.query.all()]
        self.modereglement.choices = [(n.id, n.nom) for n in ModeReglement.query.all()]
        self.beneficiaire.choices = [(b.id, b.nom) for b in Beneficiaire.query.all()]
        self.compte_id.choices = [(c.id, c.nom_personne_protegee) for c in Compte.query.all()]  # Récupérer les comptes

class ContactForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    prenom = StringField('Prénom')
    societe = StringField('Société')
    adresse = StringField('Adresse')
    code_postal = StringField('Code Postal')
    ville = StringField('Ville')
    telephone = StringField('Téléphone')
    email = StringField('Email')
    numero_finess = StringField('Numéro FINESS')
    reference_client = StringField('Référence Client')
    categorie = SelectField('Catégorie', choices=[('Médecin', 'Médecin'), ('Pharmacie', 'Pharmacie'), ('Laboratoire', 'Laboratoire'), 
                                                  ('Fournisseur', 'Fournisseur'), ('Tribunal', 'Tribunal'), 
                                                  ('Tutelle', 'Tutelle'),('Autre', 'Autre')], validators=[DataRequired()])
    submit = SubmitField('Ajouter Contact')