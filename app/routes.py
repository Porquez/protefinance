from app import app, db  # Importer l'instance de l'application Flask et db
from flask import render_template, redirect, url_for, request, flash
from app.models import Compte, Operation, Nature, Beneficiaire, ModeReglement, PieceJustificative, Contact
from app.forms import CompteForm, OperationForm, BeneficiaireForm, ModeReglementForm, PieceJustificativeForm, ContactForm, NatureForm
from flask import current_app
from werkzeug.utils import secure_filename
import os

@app.route('/')
def index():
    comptes = Compte.query.all()  # Récupérer tous les comptes
    compte_id = request.args.get('compte_id')  # Récupérer l'ID du compte sélectionné

    if compte_id:
        compte = Compte.query.get_or_404(compte_id)
        operations = compte.dernieres_operations()  # Récupérer les dernières opérations pour le compte sélectionné
    else:
        compte = None
        operations = []

    return render_template('index.html', comptes=comptes, compte=compte, operations=operations)

@app.route('/ajouter_beneficiaire', methods=['GET', 'POST'])
def ajouter_beneficiaire():
    form = BeneficiaireForm()
    if form.validate_on_submit():
        nouveau_beneficiaire = Beneficiaire(
            nom=form.nom.data,
            ville=form.ville.data,
            telephone=form.telephone.data
        )
        db.session.add(nouveau_beneficiaire)
        db.session.commit()
        flash('Le bénéficiaire a été ajouté avec succès !', 'success')
        return redirect(url_for('ajouter_operation'))  # Rediriger vers le formulaire d'ajout d'opération
    return render_template('beneficiaire/ajouter_beneficiaire.html', form=form)

@app.route('/ajouter_operation', methods=['GET', 'POST'])
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

    return render_template('operation/modifier_operation.html', form=form, operation=operation)

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
    return render_template('confirmer_suppression.html', operation=operation)

@app.route('/ajouter_nature', methods=['GET', 'POST'])
def ajouter_nature():
    form = NatureForm()
    if form.validate_on_submit():
        nouvelle_nature = Nature(
            nom=form.nom.data,
            type_operation=form.type_operation.data  # Assurez-vous que le type_operation est défini dans le formulaire
        )
        db.session.add(nouvelle_nature)
        db.session.commit()
        flash('La nature a été ajoutée avec succès !', 'success')
        return redirect(url_for('ajouter_operation'))  # Redirige vers le formulaire d'ajout d'opération
    return render_template('nature/ajouter_nature.html', form=form)

@app.route('/gestion_comptes')
def gestion_comptes():
    return render_template('gestion_comptes.html')

@app.route('/ajouter_compte', methods=['GET', 'POST'])
def ajouter_compte():
    form = CompteForm()  # On crée une instance du formulaire défini dans forms.py
    if form.validate_on_submit():
        nom_personne_protegee = form.nom_personne_protegee.data
        nouveau_compte = Compte(nom_personne_protegee=nom_personne_protegee)
        db.session.add(nouveau_compte)
        db.session.commit()
        flash('Le compte a été ajouté avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('compte/ajouter_compte.html', form=form)

@app.route('/compte/<int:compte_id>')
def afficher_compte(compte_id):
    compte = Compte.query.get_or_404(compte_id)
    operations = compte.dernieres_operations()  # Récupérer les dernières opérations
    solde_actuel = compte.solde_actuel()  # Calculer le solde actuel
    return render_template('compte.html', compte=compte, operations=operations, solde=solde_actuel)

@app.route('/bilan/<int:compte_id>')
def bilan(compte_id):
    compte = Compte.query.get_or_404(compte_id)
    operations = compte.dernieres_operations()  # Récupérer les dernières opérations
    total_recettes = sum(op.montant for op in operations if op.nature.type_operation == 'recette')
    total_depenses = sum(op.montant for op in operations if op.nature.type_operation == 'depense')
    solde = total_recettes - total_depenses

    return render_template('bilan.html', compte=compte, operations=operations, total_recettes=total_recettes, total_depenses=total_depenses, solde=solde)

@app.route('/settings')  # Ajouter cette route
def settings():
    return render_template('settings.html')

@app.route('/logout')  # Ajouter cette route
def logout():
    return render_template('logout.html')

@app.route('/contacts')
def contacts():
    contacts = Contact.query.all()  # Récupérer tous les contacts depuis la base de données
    return render_template('contacts/index.html', contacts=contacts)

@app.route('/supprimer_contact/<int:id>', methods=['POST'])
def supprimer_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Le contact a été supprimé avec succès.', 'success')
    return redirect(url_for('contacts'))

@app.route('/ajouter_contact', methods=['GET', 'POST'])
def ajouter_contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Récupérer les données du formulaire
        nouveau_contact = Contact(
            nom=form.nom.data,
            prenom=form.prenom.data,
            societe=form.societe.data,
            adresse=form.adresse.data,
            code_postal=form.code_postal.data,
            ville=form.ville.data,
            telephone=form.telephone.data,
            email=form.email.data,
            numero_finess=form.numero_finess.data,
            reference_client=form.reference_client.data,
            categorie=form.categorie.data
        )
        # Ajouter le contact à la base de données
        db.session.add(nouveau_contact)
        db.session.commit()
        flash('Le contact a été ajouté avec succès !', 'success')
        return redirect(url_for('contacts'))
    return render_template('contacts/ajouter_contact.html', form=form)
