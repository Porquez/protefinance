# app/seeds.py

def seed_natures():
    from app import db  # Déplacer l'importation ici pour éviter l'import circulaire
    from app.models import Nature  # Importer les modèles nécessaires ici

    natures = [
        {"nom": "Frais d'hébergement", "type_operation": "depense"},
        {"nom": "Charges, Transport", "type_operation": "depense"},
        {"nom": "Nourriture", "type_operation": "depense"},
        {"nom": "Habillement", "type_operation": "depense"},
        {"nom": "Fournitures administratives", "type_operation": "depense"},
        {"nom": "Impôts, taxes", "type_operation": "depense"},
        {"nom": "Santé", "type_operation": "depense"},
        {"nom": "Achats divers réparation équipement", "type_operation": "depense"},
        {"nom": "Argent de vie courante", "type_operation": "recette"},
        {"nom": "Excédent ou déficit du budget", "type_operation": "recette"},
        {"nom": "Loisirs", "type_operation": "depense"},
        {"nom": "Remboursement de dettes", "type_operation": "depense"},
    ]

    for nature_data in natures:
        # Vérifiez si la nature existe déjà
        if not Nature.query.filter_by(nom=nature_data["nom"]).first():
            nature = Nature(**nature_data)
            db.session.add(nature)

    db.session.commit()  # Validez la session

def seed_modereglement():
    from app import db  # Importation ici pour éviter l'import circulaire
    from app.models import ModeReglement  # Assurez-vous d'importer le modèle

    modereglements = [
        {"nom": "Espèces"},
        {"nom": "Carte bleue"},
        {"nom": "Virement"},
        {"nom": "Chèque"},
        {"nom": "Carte de crédit"},
    ]

    for modereglement_data in modereglements:
        # Vérifiez si le mode de règlement existe déjà
        if not ModeReglement.query.filter_by(nom=modereglement_data["nom"]).first():
            modereglement = ModeReglement(**modereglement_data)
            db.session.add(modereglement)

    db.session.commit()  # Validez la session

def seed_beneficiaires():
    from app import db  # Importer db ici pour éviter l'import circulaire
    from app.models import Beneficiaire  # Importer le modèle nécessaire

    beneficiaires = [
        {"nom": "Intermarché", "ville": "Amiens", "telephone": "0123456789"},
        {"nom": "Auchan", "ville": "Dury", "telephone": "0987654321"},
        {"nom": "Carrefour", "ville": "Amiens", "telephone": "0234567890"},
    ]

    for beneficiaire_data in beneficiaires:
        # Vérifiez si le bénéficiaire existe déjà
        if not Beneficiaire.query.filter_by(nom=beneficiaire_data["nom"]).first():
            beneficiaire = Beneficiaire(**beneficiaire_data)
            db.session.add(beneficiaire)

    db.session.commit()  # Validez la session