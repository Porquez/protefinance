# scripts/manage.py

from app import db, app

@app.cli.command('initdb')
def initdb():
    """Initialiser la base de données."""
    db.create_all()
    print("Base de données initialisée.")
