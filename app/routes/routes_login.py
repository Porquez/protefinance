# app/routes/routes_login.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from app.extensions import db, bcrypt  
from app.models import User
from app.forms import LoginForm

routes_login = Blueprint('routes_login', __name__)

@routes_login.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login/login.html', form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return jsonify({"success": True, "redirect_url": url_for('main.index')})  # Redirection en JSON
            else:
                return jsonify({"error": "Nom d’utilisateur ou mot de passe incorrect."}), 401
        else:
            print(form.errors)  # Debug: afficher les erreurs de validation
            return jsonify({"error": "Erreur de validation."}), 400

    return jsonify({"error": "Erreur de validation."}), 400


@routes_login.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return render_template('login/logout.html') 

