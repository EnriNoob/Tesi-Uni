from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth',__name__)


@auth.route('/login', methods = ['GET', 'POST'])
def login():
    #data = request.form
    #print(data)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash('login avvenuto con successo')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('password non corretta', category = 'error')
        else:
            flash('email non esistente', category = 'error')

    return render_template("login.html", user=current_user)

@auth.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email esiste già', category ='error')
        elif len(email) < 4:
            flash('email troppo corta (deve essere maggiore di 3)', category='error')
        elif (len(firstname)) < 2:
            flash('nome troppo corto (deve essere maggiore di 2)', category='error')
        elif password1 != password2:
            flash('le password non corrispondono', category='error')
        elif (len(password1)) < 6:
            flash('password troppa corta (deve essere maggiore di 5)', category='error')
        else:
            # accesso al database
            new_user = User(email = email, first_name = firstname, password = generate_password_hash(password1, method='pbkdf2'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('account creato con successo', category='success')

            return redirect(url_for('views.home'))


    return render_template("sign_up.html", user = current_user)

