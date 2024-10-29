from app import app, db
import datetime
from flask import Blueprint, render_template
from app.models import Operation

routes_budget = Blueprint('routes_budget', __name__)

@routes_budget.route('/budget')
def budget():
    # Obtenez le dernier mois en cours
    last_month = datetime.datetime.now().month
    last_year = datetime.datetime.now().year

    # Récupérez les dépenses pour le dernier mois
    depenses = db.session.query(Operation).filter(
        db.extract('month', Operation.date) == last_month,
        db.extract('year', Operation.date) == last_year,
        Operation.nature.has(type_operation='depense')
    ).all()

    # Récupérez les recettes pour le dernier mois
    recettes = db.session.query(Operation).filter(
        db.extract('month', Operation.date) == last_month,
        db.extract('year', Operation.date) == last_year,
        Operation.nature.has(type_operation='recette')
    ).all()

    # Calculez les totaux par nature pour les dépenses
    repartition_depenses = {}
    for depense in depenses:
        nature_name = depense.nature.nom
        montant = depense.montant
        if nature_name in repartition_depenses:
            repartition_depenses[nature_name] += montant
        else:
            repartition_depenses[nature_name] = montant

    # Calculez les totaux par nature pour les recettes
    repartition_recettes = {}
    for recette in recettes:
        nature_name = recette.nature.nom
        montant = recette.montant
        if nature_name in repartition_recettes:
            repartition_recettes[nature_name] += montant
        else:
            repartition_recettes[nature_name] = montant

    # Limitez aux 3 ou 4 catégories les plus utilisées
    repartition_depenses = sorted(repartition_depenses.items(), key=lambda x: x[1], reverse=True)[:4]
    repartition_recettes = sorted(repartition_recettes.items(), key=lambda x: x[1], reverse=True)[:4]

    # Créez des listes pour les labels et les valeurs des dépenses
    labels_depenses = [item[0] for item in repartition_depenses]
    values_depenses = [item[1] for item in repartition_depenses]
    data_pairs = list(zip(labels_depenses, values_depenses))

    # Créez des listes pour les labels et les valeurs des recettes
    labels_recettes = [item[0] for item in repartition_recettes]
    values_recettes = [item[1] for item in repartition_recettes]
    revenue_pairs = list(zip(labels_recettes, values_recettes))

    # Calculez le total des recettes
    total_revenue = sum(values_recettes)

    return render_template('budget/budget.html', data_pairs=data_pairs, revenue_pairs=revenue_pairs, total_revenue=total_revenue, last_month=last_month)




