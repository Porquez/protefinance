# app/routes/routes_login.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from app.extensions import db, bcrypt  # Importation de db et bcrypt depuis extensions.py
from app.models import User
from app.forms import SignupForm

routes_signup = Blueprint('routes_signup', __name__)

@routes_signup.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Compte créé avec succès!', 'success')
        return redirect(url_for('routes_login.login'))
    return render_template('signup/signup.html', form=form)
