import re
from .models import User
from . import db
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        data = request.form
        email = data.get('email')
        name = data.get('name')
        password1 = data.get('password1')
        password2 = data.get('password2')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('User already exists.', category='error')
        elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is None:
            flash('Invalid email address.', category='error')
        elif len(name) < 3:
            flash('Name is too short.', category='error')
        elif len(password1) < 8:
            flash('Password is too short.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='pbkdf2:sha1'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account successfully created.', category='success')
            user = User.query.filter_by(email=email).first()
            login_user(user)
            return redirect(url_for('views.home'))
            
        
    return render_template('sign_up.html', user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('User does not exist.', category='error')
    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))