from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from . import db
from .models import Allievo, User
from .models import Calendario
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
@login_required
def create_calendar():
    # gestiamo la request del form 
    if request.method == 'POST':
        #flash('metodo post avvenuto con successo')
        starthour = request.form.get("orainizio")
        endhour = request.form.get('orafine')
        typeslot = request.form.get('tiposlot')
        # controllo che l'utente abbia inserito i campi
        if starthour == "" or endhour == "" or typeslot == "":
            flash('attenzione, non hai inserito uno di questi dati!')
            return render_template("ccalendar.html", user=current_user)
        
        orainizio = datetime.time(int(starthour[0:2]),int(starthour[3:]),0)
        orafine = datetime.time(int(endhour[0:2]),int(endhour[3:]),0)
             
        print(starthour,endhour,typeslot)
        sus = request.form.getlist('check')
        # creo i bucket dei giorni
        # LUN:0 MAR:1 MER:2 GIO:3 VEN:4 SAB:5
        buckets_days = [[] for x in range (6)]
        # inserisco nei bucket gli slot eliminati
        for check in sus:
            # spezzo es. '0-1'
            split = check.rsplit('-')
            buckets_days[int(split[1])].append(split[0])

        print(buckets_days)
        for d,day in enumerate(buckets_days):
            # controlliamo se l'utente in un giorno abbia eliminato uno solo slot
            if len(day) == 1:
                flash(f'attenzione, hai escluso nel giorno{day} un solo slot!')
                return render_template("ccalendar.html", user=current_user)
            # se no dobbiamo controllare che abbia eliminato uno solo slot in un giorno con più slot eliminati
            else:
                # scorriamo nei slot eliminati nei vari giorni
                for x,slot in enumerate(day) :
                    print(x,slot)
                    # caso in cui si parte dal primo slot eliminato nella lista (si controlla soltanto lo slot successivo)
                    if x == 0:
                        if int(day[x + 1]) - int(slot) != 1:
                            flash(f'attenzione, hai escluso nel giorno{d}={day} uno slot da mezz\'ora da solo! ovvero{slot}')
                            return render_template("ccalendar.html", user=current_user)
                    # caso in cui si arriva all'ultimo slot eliminato nella lista (si controlla soltatno lo slot precedente)
                    elif x == len(day) - 1:
                        if int(slot) - int(day[x - 1]) != 1:
                            flash(f'attenzione, hai escluso nel giorno{day} uno slot da mezz\'ora da solo! ovvero{slot}')
                            return render_template("ccalendar.html", user=current_user)
                    # caso in cui si va controllare per ogni slot eliminato quello precedente e quello successivo
                    # se la distanza di hamming non è 1 in entrambi i casi significa che la distanza tra lo slot e quello successivo o quello precedente non è 1    
                    elif (int(day[x + 1]) - int(slot)) != 1 and (int(slot) - int(day[x - 1])) != 1:
                            flash(f'attenzione, hai escluso nel giorno{day} uno slot da mezz\'ora da solo! ovvero{slot}')
                            return render_template("ccalendar.html", user=current_user)
                            
        print("è andato tutto bene")
        sloteliminati = ""
        print(buckets_days)
        # devo mettere in una stringa gli slot eliminati perchè il campo sloteliminati della tabella calendario accetta stringhe e non liste
        for x,day in enumerate(buckets_days):
            for slots in day:
                sloteliminati += f"{x}-{slots},"

        new_calendar = Calendario(oremattina = str(orainizio) , orepomeriggio= str(orafine) ,numeroslot=int(typeslot), sloteliminati = sloteliminati)
        db.session.add(new_calendar)
        db.session.commit()
        flash("creazione del calendario andato a buon fine!")
        return redirect(url_for('dashboard.home',name = admin_name)) 
    else:
        # ritorna la pagina in caso in cui l'accediamo dalla dashboard
        return render_template("ccalendar.html", user=current_user)
    
@dashboard.route('/aggiungi', methods = ['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        nome = request.form.get("nome")
        cognome = request.form.get("cognome")
        giorno_nascita = request.form.get("giorno")
        mese_nascita = request.form.get("mese")
        anno_nascita = request.form.get("anno")
        genere = request.form.get("genere")
        agonistico = request.form.get("agonistico")
        dilettante = request.form.get("dilettante")
        numero_allenamenti = request.form.get("allenamenti")
        id_calendario = request.form.get("tdata")
        d = request.form.getlist("check")

        print(nome,cognome,giorno_nascita,mese_nascita, anno_nascita, genere, agonistico, dilettante, numero_allenamenti, id_calendario, d)
        '''
        buckets_days = [[] for x in range (6)]
        # inserisco nei bucket gli slot eliminati
        for check in d:
            # spezzo es. '0-1'
            split = check.rsplit('-')
            buckets_days[int(split[1])].append(split[0])

        print(buckets_days)

        for d,day in enumerate(buckets_days):
            # controlliamo se l'utente in un giorno abbia eliminato uno solo slot
            if len(day) == 1:
                flash(f'attenzione, hai escluso nel giorno{day} un solo slot!')
                return render_template("ccalendar.html", user=current_user)
            # se no dobbiamo controllare che abbia eliminato uno solo slot in un giorno con più slot eliminati
            else:
                # scorriamo nei slot eliminati nei vari giorni
                for x,slot in enumerate(day) :
                    print(x,slot)
                    # caso in cui si parte dal primo slot eliminato nella lista (si controlla soltanto lo slot successivo)
                    if x == 0:
                        if int(day[x + 1]) - int(slot) != 1:
                            flash(f'attenzione, hai escluso nel giorno{d}={day} uno slot da mezz\'ora da solo! ovvero{slot}')
                            return render_template("ccalendar.html", user=current_user)
                    # caso in cui si arriva all'ultimo slot eliminato nella lista (si controlla soltatno lo slot precedente)
                    elif x == len(day) - 1:
                        if int(slot) - int(day[x - 1]) != 1:
                            flash(f'attenzione, hai escluso nel giorno{day} uno slot da mezz\'ora da solo! ovvero{slot}')
                            return render_template("ccalendar.html", user=current_user)
                    # caso in cui si va controllare per ogni slot eliminato quello precedente e quello successivo
                    # se la distanza di hamming non è 1 in entrambi i casi significa che la distanza tra lo slot e quello successivo o quello precedente non è 1    
                    elif (int(day[x + 1]) - int(slot)) != 1 and (int(slot) - int(day[x - 1])) != 1:
                            flash(f'attenzione, hai escluso nel giorno{day} uno slot da mezz\'ora da solo! ovvero{slot}')
                            return render_template("ccalendar.html", user=current_user)
                            
        print("è andato tutto bene")
        sloteDisponibili = ""
        print(buckets_days)
        # devo mettere in una stringa gli slot eliminati perchè il campo sloteliminati della tabella calendario accetta stringhe e non liste
        for x,day in enumerate(buckets_days):
            for slots in day:
                sloteDisponibili += f"{x}-{slots},"
        #new_allievo = Allievo(nome=nome, cognome=cognome, giornonascita=int(giorno_nascita), mesenascita=int(mese_nascita), annonascita=int(anno_nascita), numeroallenamenti=numero_allenamenti, slotdisponibilita=sloteDisponibili, id_calendario=)
        '''
        return "sus"
    else:

        calendar_list = Calendario.query.all()
        for cal in calendar_list:
            print(cal.id,cal.oremattina,cal.orepomeriggio,cal.numeroslot,cal.sloteliminati)
        
        return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)