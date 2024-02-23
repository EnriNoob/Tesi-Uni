from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from . import db
from .models import User
from datetime import datetime


from calendar import Calendar
from tabnanny import check
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Calendario, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import datetime




dashboard = Blueprint('dashboard',__name__,template_folder="templates/dashboard")
admin_name = ""

@dashboard.route('/')
@login_required
def home_without_name():
    #admin = User.query.filter_by(first_name = "enri").first()
    return render_template("home.html", user=current_user, name = admin_name)


@dashboard.route('/<name>')
@login_required
def home(name):
    #admin = User.query.filter_by(first_name = "enri").first()
    global admin_name
    admin_name = name
    return render_template("home.html", user=current_user, name = name)


@dashboard.route('/ccalendar', methods=['GET', 'POST'])
def create_calendar():
    if request.method == 'POST':
        #flash('metodo post avvenuto con successo')
        starthour = request.form.get("orainizio")
        endhour = request.form.get('orafine')
        typeslot = request.form.get('tiposlot')
        if starthour == "" or endhour == "" or typeslot == "":
            flash('attenzione, non hai inserito uno di questi dati!')
            return render_template("ccalendar.html", user=current_user)
        
        print(starthour,endhour,typeslot)
        sus = request.form.getlist('check')
        buckets_days = [[] for x in range (6)]
        
        for check in sus:
            split = check.rsplit('-')
            buckets_days[int(split[1])].append(split[0])
            
        for day in buckets_days:
            # controlliamo se l'utente in un giorno abbia eliminato uno solo slot
            if len(day) == 1:
                flash(f'attenzione, hai inserito nel giorno{day} un solo slot!')
                return render_template("ccalendar.html", user=current_user)
            
        sloteliminati = ""
        print(buckets_days)
        for x,day in enumerate(buckets_days):
            for slots in day:
                sloteliminati += f"{x}-{slots}, "

        orainizio = datetime.time(int(starthour[0:2]),int(starthour[3:]),0)
        orafine = datetime.time(int(endhour[0:2]),int(endhour[3:]),0)

        new_calendar = Calendario(oremattina = str(orainizio) , orepomeriggio= str(orafine) ,numeroslot=int(typeslot), sloteliminati = sloteliminati)
        db.session.add(new_calendar)
        db.session.commit()

        secondiInizio = orainizio.hour * 3600 + orainizio.minute * 60 
        secondiFine = orafine.hour * 3600 + orafine.minute * 60

        print(secondiInizio)
        print(secondiFine)

        if secondiInizio > secondiFine:
            flash('attenzione, hai inserito l\'ora di inizio maggiore dell\'ora di fine!')
            return render_template("ccalendar.html", user=current_user)
        else:
            return redirect(url_for('dashboard.home',name = admin_name))  
    else:
        return render_template("ccalendar.html", user=current_user)

@dashboard.route('/aggiungi', methods = ['GET', 'POST'])
def create_user():
    return render_template("aggiungi.html", user=current_user)