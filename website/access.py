from calendar import Calendar
from os import name
from tabnanny import check
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Calendario, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import datetime

# un blueprint è un modo di organizzare un gruppo di view correlati, quindi invece di registrare view direttamente all'applicazione
# essi vengono registrati nel blueprint
# questo blueprint è per i blog post functions
# questo server per l'autenticazione insomma
access = Blueprint('access',__name__, template_folder='templates/access')

# aut.route associa l'url /login con la funzione view login in riga 18
# quando flask riceve questo url la view corrispondente si attiva e manda una risposta nel return 
# (in questo caso manda alla home se il login è avvenuto con successo, se no renderizza login di nuovo)
@access.route('/', methods = ['GET', 'POST'])
def login():
    # se l'utente ha inviato un form (POST) dobbiamo verificare che il metodo della risposta e POST
    if request.method == 'POST':
        # request.form è un0 speciale dict mappando chiavi del form inviato con valori
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password,password):
                flash('login avvenuto con successo')
                login_user(user, remember=False)
                return redirect(url_for('dashboard.home', name = user.first_name))
            else:
                flash('password non corretta', category = 'error')
        else:
            flash('email non esistente', category = 'error')

    return render_template("login.html", user=current_user)

@access.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('access.login'))

@access.route('/sign-up', methods = ['GET', 'POST'])
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
            # inserimento di un record (INSERT INTO user...)= nella tabella user 
            new_user = User(email = email, first_name = firstname, password = generate_password_hash(password1, method='pbkdf2'))
            db.session.add(new_user)
            # commit per salvare le modifiche
            db.session.commit()
            login_user(new_user, remember=False)
            flash('account creato con successo', category='success')
            # una volta creato l'account dobbiamo far reidirezionare l'admin al login
            # url_for genera l'url per la login view
            # redirect genera un reindirizzamento risposta all'url generato 
            return redirect(url_for('access.login'))


    return render_template("sign_up.html", user = current_user)
