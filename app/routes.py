from app import app, db  # Importer l'instance de l'application Flask et db
from flask import render_template, redirect, url_for, request, flash, current_app
from app.models import Compte, Operation, Nature, Beneficiaire, ModeReglement, PieceJustificative, Contact, Banque, ReleveCompte
from app.forms import CompteForm, OperationForm, BeneficiaireForm, ModeReglementForm, PieceJustificativeForm, ContactForm, NatureForm, BanqueForm
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

import pytesseract
import os
import logging
import datetime
from datetime import datetime

@app.route('/')
def index():
    comptes = Compte.query.all()  
    compte_id = request.args.get('compte_id')

    if compte_id:
        compte = Compte.query.get_or_404(compte_id)

        # Récupérer les opérations manuelles
        operations_manuelles = compte.dernieres_operations()

        # Récupérer les opérations importées (mais ne les inclure pas par défaut)
        operations_importees = ReleveCompte.query.filter_by(compte_id=compte_id).all()

        # Par défaut, afficher uniquement les opérations manuelles
        operations = [(op, 'manuelle') for op in operations_manuelles]

        # Calcul des totaux pour les opérations manuelles
        total_recettes = sum(op.montant for op in operations_manuelles if op.montant > 0)
        total_depenses = sum(-op.montant for op in operations_manuelles if op.montant < 0)

        solde = total_recettes - total_depenses
        nombre_operations = len(operations)
        selected_compte_id = compte.id  # Définit l'ID du compte sélectionné
    else:
        compte = None
        operations = []
        total_recettes = total_depenses = solde = nombre_operations = 0
        selected_compte_id = None  # Aucun compte sélectionné

    return render_template('index.html', comptes=comptes, compte=compte, operations=operations, 
                           total_recettes=total_recettes, total_depenses=total_depenses, 
                           solde=solde, nombre_operations=nombre_operations,
                           selected_compte_id=selected_compte_id)  # Passez-le au modèle


@app.route('/formulaire_banque', methods=['GET', 'POST'])
def formulaire_banque():
    form = BanqueForm()  # Remplacez FormBanque par le nom réel de votre formulaire de création de banque
    if request.method == 'POST' and form.validate_on_submit():
        nom = form.nom.data  # Exemple de champ du formulaire
        adresse = form.adresse.data
        telephone = form.telephone.data  # Optionnel

        # Ajoutez ici la logique pour enregistrer la banque dans la base de données
        nouvelle_banque = Banque(nom=nom, adresse=adresse, telephone=telephone)
        db.session.add(nouvelle_banque)
        db.session.commit()

        return redirect(url_for('index'))  # Rediriger vers la page d'accueil après l'ajout

    return render_template('banque/formulaire_banque.html', form=form)  # Assurez-vous de passer le formulaire au template

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
    return render_template('compte/gestion_comptes.html')

@app.route('/ajouter_compte', methods=['GET', 'POST'])
def ajouter_compte():
    form = CompteForm()
    # Récupérer toutes les banques pour remplir le champ de sélection
    form.banque_id.choices = [(b.id, b.nom) for b in Banque.query.all()]

    if form.validate_on_submit():
        nouveau_compte = Compte(
            nom_personne_protegee=form.nom_personne_protegee.data,
            rib=form.rib.data,
            type_compte=form.type_compte.data,
            solde_initial=form.solde_initial.data,
            banque_id=form.banque_id.data  # Assigner l'ID de la banque
        )
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

@app.route('/import_releve', methods=['GET', 'POST'])
def import_releve():
    operations = []  # Initialiser les opérations ici
    natures = Nature.query.all()  # Récupérer toutes les natures
    if request.method == 'POST':
        file = request.files['file']

        # Vérifier si un fichier PDF a bien été sélectionné
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'relevecompte', filename)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            logging.info(f'Fichier sauvegardé : {file_path}')
            
            flash('Importation en cours, veuillez patienter...', 'info')
            transactions = extract_transactions(file_path)
 
            logging.info(f'Transactions extraites : {transactions}')
            flash(f'{len(transactions)} opérations extraites.', 'info')

            # Passer les opérations extraites à une nouvelle page pour validation
            compte_id = request.form.get('compte_id')
            return render_template('relevebanque/valider_releve.html', operations=transactions, compte_id=compte_id, natures=natures)

    return redirect(url_for('index'))


@app.route('/valider_releve', methods=['POST'])
def valider_releve():
    operations = request.form
    compte_id = request.form.get('compte_id')
    selected_operations = request.form.getlist('selected_operations')
    
    logging.info('Validation des opérations...')
    
    for index in selected_operations:
        date_operation = request.form.get(f'date_operation_{index}')
        designation = request.form.get(f'designation_{index}')
        debit = request.form.get(f'debit_{index}')
        credit = request.form.get(f'credit_{index}')
        nature = request.form.get(f'nature_{index}')

        # Enregistrer uniquement les opérations sélectionnées
        releve = ReleveCompte(
            compte_id=compte_id,
            date_operation=date_operation,
            designation=designation,
            debit=debit,
            credit=credit,
            nature_id=nature
        )
        db.session.add(releve)
        logging.info(f'Opération ajoutée : {releve}')

    db.session.commit()
    flash('Les opérations ont été validées avec succès.')
    return redirect(url_for('index'))

import logging
from pdf2image import convert_from_path
import pytesseract

def extract_transactions(file_path):
    transactions = []
    logging.basicConfig(level=logging.INFO)
    
    # Convertir le PDF en images
    logging.info('Conversion du PDF en images...')
    try:
        images = convert_from_path(file_path)
        logging.info(f'{len(images)} images créées à partir du PDF.')
    except Exception as e:
        logging.error(f'Erreur lors de la conversion du PDF en images: {e}')
        return transactions

    # Extraire le texte de chaque image
    for index, image in enumerate(images):
        logging.info(f'Extraction du texte de l\'image {index + 1}...')
        try:
            text = pytesseract.image_to_string(image, lang='fra')
            if text:
                lines = text.split('\n')
                for line in lines:
                    if line.strip():  # Ignorer les lignes vides
                        parts = line.split()
                        logging.info(f'Ligne à traiter : {parts}')
                        # Vérification du format attendu
                        if len(parts) >= 5 and '/' in parts[0]:  
                            try:
                                # Construire le libellé et la date correctement
                                date_str = parts[0] 
                                libelle = ' '.join(parts[1:-1])  # Libellé de l'opération
                                montant_str = parts[-1].replace(',', '.').replace('€', '').strip()  # Montant
                                try:
                                    montant = float(montant_str) if montant_str else 0.0  # Défaut à 0.0 si vide
                                except ValueError:
                                    logging.error(f'Erreur de conversion du montant : {montant_str}')
                                    montant = 0.0  # Ou gérer comme bon vous semble

                                # Extraire le montant et parse la date
                                date = parse_date(date_str)
                                montant = float(montant_str) if montant_str else None

                                # Ventiler le débit ou le crédit
                                if any(word in libelle for word in ["Achat", "ACHAT", "Carte", "CARTE", "Prélèvement", "PRELEVEMENT"]):
                                    debit = montant if montant >= 0 else None
                                    credit = None
                                elif any(word in libelle for word in ["Virement", "VIREMENT"]):
                                    credit = montant if montant >= 0 else None
                                    debit = None
                                else:
                                    debit = 0
                                    credit = 0

                                # Ajouter l'opération à la liste
                                transactions.append({
                                    'date': date,
                                    'operation': libelle,
                                    'debit': debit,
                                    'credit': credit,
                                    'nature': "A classer"  # Nature par défaut
                                })
                                logging.info(f'Transaction ajoutée : {transactions[-1]}')
                            except Exception as e:
                                logging.error(f'Erreur lors du traitement de la ligne: {line}, erreur: {e}')
                        else:
                            logging.warning(f'Nombre de colonnes insuffisant dans la ligne: {line}')
            else:
                logging.warning('Aucun texte extrait de l\'image.')
        except Exception as e:
            logging.error(f'Erreur lors de l\'extraction du texte de l\'image {index + 1}: {e}')

    return transactions

def parse_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d/%m')
        if len(date_str.split('/')) == 2:
            return date_obj.replace(year=datetime.now().year)
        return date_obj
    except ValueError as e:
        logging.error(f'Erreur de parsing de date: {e} pour la chaîne: {date_str}')
        return None

