# app/routes/routes_login.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required,current_user
from app.extensions import db, bcrypt  
from app.models import User, UserConnection
from app.forms import LoginForm,VerificationForm
from datetime import datetime

routes_login = Blueprint('routes_login', __name__)

@routes_login.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Récupérer l'adresse IP et définir le nom de la machine
            ip_address = request.remote_addr
            machine_name = request.headers.get('User-Agent')  # Utiliser l'agent utilisateur comme nom de machine, par exemple
            
            # Créer une entrée UserConnection avec l'adresse IP et le nom de la machine
            new_connection = UserConnection(
                user_id=user.id,
                start_time=datetime.now(),
                ip_address=ip_address,
                machine_name=machine_name
            )
            db.session.add(new_connection)
            db.session.commit()
            return jsonify({"success": True, "redirect_url": url_for('index')})
        else:
            return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect."}), 401
    return render_template('login/login.html', form=form)


@routes_login.context_processor
def inject_last_connection():
    if current_user.is_authenticated:
        last_connection = UserConnection.query.filter_by(user_id=current_user.id).order_by(UserConnection.start_time.desc()).first()
        return {'last_connection': last_connection}
    return {}

@routes_login.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return render_template('login/logout.html') 

@routes_login.route('/verify', methods=['GET', 'POST'])
def verify_account():
    form = VerificationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verification_code == form.verification_code.data:
            user.verification_code = None  #
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('Code de vérification incorrect.', 'danger')
    return render_template('verify.html', form=form)
