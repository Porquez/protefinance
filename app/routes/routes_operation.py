from app import app, db  # Importer l'instance de l'application Flask et db
from flask import render_template, redirect, url_for, request, flash, current_app, jsonify, Blueprint
from app.models import Compte, Operation, Nature, Beneficiaire, ModeReglement, PieceJustificative, Contact, Banque, ReleveCompte
from app.forms import CompteForm, OperationForm, BeneficiaireForm, ModeReglementForm, PieceJustificativeForm, ContactForm, NatureForm, BanqueForm
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image

import base64  #
import pytesseract
import os
import logging
import datetime
from datetime import datetime

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/ajouter_operation', methods=['GET', 'POST'])
def ajouter_operation():
    form = OperationForm()  # Instance du formulaire d'opération
    if form.validate_on_submit():
        montant = form.montant.data
        nature_id = form.nature.data
        compte_id = form.compte_id.data
        beneficiaire_id = form.beneficiaire.data
        designation = form.designation.data
        modereglement_id = form.modereglement.data  # Récupérer l'ID du mode de règlement

        # Créer une nouvelle opération
        nouvelle_operation = Operation(
            montant=montant,
            nature_id=nature_id,
            compte_id=compte_id,
            beneficiaire_id=beneficiaire_id,
            designation=designation,
            modereglement_id=modereglement_id,
            numero_piece=form.numero_piece.data  
        )
        
        # Traitement du fichier de pièce justificative
        if form.fichiers.data:
            fichier = form.fichiers.data
            nom_fichier = secure_filename(fichier.filename)
            chemin = os.path.join(current_app.config['UPLOAD_FOLDER'], nom_fichier)  # Utilisez le chemin de stockage défini
            fichier.save(chemin)  # Sauvegarde du fichier
            
            # Enregistrement de la pièce justificative
            piece = PieceJustificative(nom_fichier=nom_fichier, chemin=chemin, operation=nouvelle_operation)
            db.session.add(piece)  # Ajoutez la pièce justificative à la session
            
        db.session.add(nouvelle_operation)  # Ajoutez l'opération à la session
        db.session.commit()  # Validez les changements
        flash('L\'opération a été ajoutée avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('operation/ajouter_operation.html', form=form)

@app.route('/modifier_operation/<int:operation_id>', methods=['GET', 'POST'])
def modifier_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)
    # Pré-remplir le formulaire avec les données de l'opération existante
    form = OperationForm(obj=operation)  

    # Définir les choix pour les SelectField
    form.nature.choices = [(n.id, n.nom) for n in Nature.query.all()]
    form.modereglement.choices = [(m.id, m.nom) for m in ModeReglement.query.all()]
    form.beneficiaire.choices = [(b.id, b.nom) for b in Beneficiaire.query.all()]
    form.compte_id.choices = [(c.id, c.nom_personne_protegee) for c in Compte.query.all()]

    # Assurez-vous que la valeur actuelle est correctement définie
    form.nature.data = operation.nature_id  # Ceci est crucial pour que le champ select affiche la bonne valeur
    # Assurer la bonne sélection des valeurs actuelles
    form.modereglement.data = operation.modereglement_id
    form.beneficiaire.data = operation.beneficiaire_id
    form.compte_id.data = operation.compte_id

     # Récupérer le nom de fichier actuel
    current_file_name = None
    if operation.pieces_justificatives:
        current_file_name = operation.pieces_justificatives[0].nom_fichier


    if form.validate_on_submit():
        # Mettre à jour les attributs de l'opération avec les données du formulaire
        operation.montant = form.montant.data
        operation.nature_id = form.nature.data
        operation.compte_id = form.compte_id.data
        operation.beneficiaire_id = form.beneficiaire.data
        operation.designation = form.designation.data
        operation.modereglement_id = form.modereglement.data
        operation.numero_piece = form.numero_piece.data  
        operation.date = form.date.data

        # Si un fichier est téléchargé, mettre à jour la pièce justificative
        if form.fichiers.data:
            fichier = form.fichiers.data
            nom_fichier = secure_filename(fichier.filename)
            chemin = os.path.join(current_app.config['UPLOAD_FOLDER'], nom_fichier)
            fichier.save(chemin)

            # Ajouter une nouvelle pièce justificative ou remplacer l'existante
            if operation.pieces_justificatives:
                piece = operation.pieces_justificatives[0]  # Supposons qu'il n'y ait qu'une pièce
                piece.nom_fichier = nom_fichier
                piece.chemin = chemin
            else:
                nouvelle_piece = PieceJustificative(nom_fichier=nom_fichier, chemin=chemin, operation=operation)
                db.session.add(nouvelle_piece)

        db.session.commit()  # Valider les modifications dans la base de données
        flash('L\'opération a été modifiée avec succès !', 'success')
        return redirect(url_for('index'))

    return render_template('operation/modifier_operation.html', form=form, operation=operation, current_file_name=current_file_name)

@app.route('/confirmer_suppression_operation/<int:operation_id>', methods=['GET', 'POST'])
def supprimer_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)

    if request.method == 'POST':
        # Supprimer l'opération et ses pièces justificatives
        if operation.pieces_justificatives:
            for piece in operation.pieces_justificatives:
                try:
                    # Supprimez le fichier physiquement
                    os.remove(piece.chemin)
                except OSError:
                    pass  # Gestion des erreurs

            # Supprimez également les pièces justificatives de la base
            PieceJustificative.query.filter_by(operation_id=operation.id).delete()

        # Supprimer l'opération
        db.session.delete(operation)
        db.session.commit()
        flash('L\'opération et ses pièces justificatives ont été supprimées avec succès !', 'success')
        return redirect(url_for('index', compte_id=operation.compte_id))

    # Si GET, afficher une page de confirmation
    return render_template('operation/confirmer_suppression_operation.html', operation=operation)

@app.route('/confirmer_suppression_operation/<int:operation_id>', methods=['GET', 'POST'])
def confirmer_suppression_operation(operation_id):
    operation = Operation.query.get_or_404(operation_id)

    if request.method == 'POST':
        # Supprimer l'opération et ses pièces justificatives
        if operation.pieces_justificatives:
            for piece in operation.pieces_justificatives:
                try:
                    # Supprime le fichier physiquement
                    os.remove(piece.chemin)
                except OSError:
                    pass  # Gestion des erreurs

            # Supprime également les pièces justificatives de la base
            PieceJustificative.query.filter_by(operation_id=operation.id).delete()

        # Supprimer l'opération
        db.session.delete(operation)
        db.session.commit()
        flash('L\'opération et ses pièces justificatives ont été supprimées avec succès !', 'success')
        return redirect(url_for('index', compte_id=operation.compte_id))

    # Si GET, afficher une page de confirmation
    return render_template('confirmer_suppression.html', operation=operation)

