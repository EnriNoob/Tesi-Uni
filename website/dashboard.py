from time import mktime
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import null
from . import db
from .models import Allievo, User
from .models import Calendario
from datetime import date, datetime


from calendar import Calendar
from tabnanny import check
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Calendario, User, Allievo
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
        if starthour == "-" or endhour == "-" or typeslot == "-":
            flash('attenzione, non hai inserito uno di questi dati!', category='success')
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
           
        print("è andato tutto bene")
        sloteliminati = ""
        print(buckets_days)
        # devo mettere in una stringa gli slot eliminati perchè il campo sloteliminati della tabella calendario accetta stringhe e non liste
        for x,day in enumerate(buckets_days):
            for slots in day:
                sloteliminati += f"{x}-{slots},"
                

        new_calendar = Calendario(oremattina = str(orainizio) , orepomeriggio= str(orafine) ,numeroslot=int(typeslot), sloteliminati = sloteliminati[:-1])
        db.session.add(new_calendar)
        db.session.commit()
        flash("creazione del calendario andato a buon fine!",category='success')
        return redirect(url_for('dashboard.home',name = admin_name)) 
    else:
        # ritorna la pagina in caso in cui l'accediamo dalla dashboard
        calendar_list = Calendario.query.all()
        if len(calendar_list) == 2:
            flash("ci sono già i due calendari con slot da 60 e 90 minuti", category='error')
            return redirect(url_for('dashboard.home',name = admin_name)) 
        elif len(calendar_list) == 1:
            slot = int(calendar_list[0].numeroslot)
            return render_template("ccalendar.html", user=current_user, slot = slot)
            pass
        else:
            return render_template("ccalendar.html", user=current_user, slot = 0)

@dashboard.route('/modificacalendario', methods=['GET', 'POST'])
@login_required
def modify_calendar():
    calendar_list = Calendario.query.all()
    if request.method == 'POST':
        starthour = request.form.get("orainizio")
        endhour = request.form.get('orafine')
        print(starthour)
        print(endhour)
        typeslot = request.form.get('tiposlot')
        idcal = request.form.get("textid")
        # controllo che l'utente abbia inserito i campi
        if starthour == "-" or endhour == "-" or typeslot == "-":
            flash('attenzione, non hai inserito uno di questi dati!', category='error')
            return render_template("ccalendar.html", user=current_user)
        
        orainizio = datetime.time(int(starthour[0:2]),int(starthour[3:5]),0)
        orafine = datetime.time(int(endhour[0:2]),int(endhour[3:5]),0)
             
        print(starthour,endhour,typeslot)
        sus = request.form.getlist('check')
        # creo i bucket dei giorni
        # LUN:0 MAR:1 MER:2 GIO:3 VEN:4 SAB:5
        buckets_days = [[] for x in range (6)]
        # inserisco nei bucket gli slot eliminati
        for check in sus:
            # spezzo es. '0-1'
            split = check.rsplit('-')
            buckets_days[int(split[0])].append(split[1])

        print(buckets_days)
        sloteliminati = ""
        print(buckets_days)
        # devo mettere in una stringa gli slot eliminati perchè il campo sloteliminati della tabella calendario accetta stringhe e non liste
        for x,day in enumerate(buckets_days):
            for slots in day:
                sloteliminati += f"{x}-{slots},"
        
        actual_calendar = Calendario.query.filter_by(id=idcal).first()
        actual_calendar.oremattina = str(orainizio)
        actual_calendar.orepomeriggio = str(orafine)
        actual_calendar.sloteliminati = sloteliminati[:-1]
        db.session.commit()

        student_list = Allievo.query.filter_by(id_calendario = idcal).all()

        for stu in student_list:
            stu.slotdisponibilita = ""

        db.session.commit()
        new_calendar_list = Calendario.query.all()
        flash(f"modifica del calendario con id:{idcal} avvenuta con successo", category="success")
        return render_template("modificacalendario.html", user=current_user,calendar_list = new_calendar_list)
    else:
        return render_template("modificacalendario.html", user=current_user,calendar_list = calendar_list)


@dashboard.route('/aggiungi', methods = ['GET', 'POST'])
@login_required
def create_user():
    calendar_list = Calendario.query.all()
    if request.method == 'POST':
        # prendo i dati dal form 
        nome = request.form.get("nome")
        cognome = request.form.get("cognome")
        giorno_nascita = request.form.get("giorno")
        mese_nascita = request.form.get("mese")
        anno_nascita = request.form.get("anno")
        genere = request.form.get("genere")
        livello = request.form.get("livello")
        numero_allenamenti = request.form.get("allenamenti")
        id_calendario = request.form.get("idcalendar")
        d = request.form.getlist("check")

        print(nome,cognome,giorno_nascita,mese_nascita, anno_nascita, genere, livello, numero_allenamenti, id_calendario, d)

        # controllo se l'utente non abbia inserito nome o cognome
        if nome == "" or cognome == "":
            flash("non hai inserito nome oppure cognome", category='error')
            return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
        
        if giorno_nascita == None or mese_nascita == None or anno_nascita == None:
            flash("non hai inserito il giorno o mese o anno di nascita", category='error')
            return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
        
        if genere == None or numero_allenamenti == None:
            flash("non hai genere o livello o numero di allenamenti", category='error')
            return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
    
        # data di oggi
        struct_time_oggi = date.today().timetuple()

        # data di nascita dell'allievo
        struct_time_nascita = date(int(anno_nascita), int(mese_nascita), int(giorno_nascita)).timetuple()
        # da 2024 in giu 
        match livello:
            #bambini di 3 e 4 anni 2020 <= nascita <= 2021
            case "I love tennis": 
                low_bound = date(struct_time_oggi.tm_year - 4, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 3, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
                
            # bambini dai 5 ai 8 anni, 2016 <= nascita <= 2019    
            case "sat under 8" | "pre ago under 8" | "ago under 8":
                low_bound = date(struct_time_oggi.tm_year - 8, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 5, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
                
            # bambini dai 9 ai 10 anni, 2014 <= nascita <= 2015
            case "sat under 10" | "pre ago under 10" | "ago under 10":
                # 2014 < 2015
                low_bound = date(struct_time_oggi.tm_year - 10, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 9, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()  
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
                
            # bambini dai 11 ai 12 anni, 2012 <= nascita <= 2013
            case "sat under 12" | "pre ago under 12" | "ago under 12":
                low_bound = date(struct_time_oggi.tm_year - 12, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 11, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple() 
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
                
            # bambini dai 13 ai 14 anni, 2010 <= nascita <= 2011
            case "sat under 14" | "pre ago under 14" | "ago under 14":
                low_bound = date(struct_time_oggi.tm_year - 14, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 13, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()  
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
            
            # bambini dai 15 ai 16 anni, 2008 <= nascita <= 2009
            case "sat under 16" | "pre ago under 16" | "ago under 16":
                low_bound = date(struct_time_oggi.tm_year - 16, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 15, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
            
            # bambini dai 17 ai 18 anni, 2008 <= nascita <= 2009
            case "sat under 18" | "pre ago under 18" | "ago under 18":
                low_bound = date(struct_time_oggi.tm_year - 16, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                high_bound = date(struct_time_oggi.tm_year - 15, struct_time_oggi.tm_mon, struct_time_oggi.tm_mday).timetuple()
                if not (mktime(low_bound) <= mktime(struct_time_nascita) and mktime(struct_time_nascita) <=  mktime(high_bound)):
                    flash(f"hai inserito un'anno di nascita sbagliato {anno_nascita}, per il livelllo {livello}", category='error')
                    return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
            case _ : 
                print("non hai messo nessuna categoria")
                
        slotDisponibili = ""
        buckets_days = [[] for x in range (6)]
        # inserisco nei bucket gli slot in cui gli studenti sono disponibili a fare allenamento
        for check in d:
            # spezzo es. '0-1'
            split = check.rsplit('-')
            buckets_days[int(split[0])].append(split[1])

        print(buckets_days)
        
        count = 0
        for d,day in enumerate(buckets_days):
            if len (day) > 0:
                count += 1
    
        if count < int(numero_allenamenti):
                flash(f"il numero di slot inseriti: {count} non soddisfa il numero di allenamenti a settimana dell'allievo {numero_allenamenti}" , category='error')
                return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)
        
        print("è andato tutto bene")
        # devo mettere in una stringa gli slot disponibili perchè il campo sloteliminati della tabella calendario accetta stringhe e non liste
        
        for x,day in enumerate(buckets_days):
            for slots in day:
                slotDisponibili += f"{x}-{slots},"

        new_allievo = Allievo(nome=nome, cognome=cognome, giornonascita=int(giorno_nascita), mesenascita=int(mese_nascita), annonascita=int(anno_nascita),genere = genere,livello = livello, numeroallenamenti=numero_allenamenti, slotdisponibilita=slotDisponibili[:-1], id_calendario= int(id_calendario))
        db.session.add(new_allievo)
        db.session.commit()
        flash("aggiunta dell'utente andato a buon fine!", category='success')
        return redirect(url_for('dashboard.home',name = admin_name)) 
    else:
        return render_template("aggiungi.html", user=current_user, calendar_list = calendar_list)

@dashboard.route('/modificaallievo', methods=['GET', 'POST'])
@login_required
def modify_student():
    calendar_list = Calendario.query.all()
    student_list =  Allievo.query.all()
    if request.method == 'POST':

        nome = request.form.get("nome")
        cognome = request.form.get("cognome")
        numero_allenamenti = request.form.get("allenamenti")
        id_allievo = request.form.get("idallievo")   
        d = request.form.getlist("check")
        elimina = request.form.get("elimina")

        print(f"id_allievo {id_allievo}")
        print(nome)
        print(cognome)
        print(numero_allenamenti)
        # se l'admin ha selezionato nel checkbox di eliminare l'allievo elimina sarà on 
        if elimina == "on":
            temp = Allievo.query.filter_by(id = id_allievo).first()
            # devo toglierlo dalla lista perchè in student_list l'allievo da eliminare è ancora presente e verrà passato nel render template
            student_list.remove(temp)
            db.session.delete(temp)
            db.session.commit()
            flash(f"eliminazione dell'allievo {nome} {cognome} con id {id_allievo} avvenuto con sucesso",category="success")
            return render_template("modificaallievo.html", user = current_user, student_list = student_list, calendar_list = calendar_list)

        slotDisponibili = ""
        buckets_days = [[] for x in range (6)]
        # inserisco nei bucket gli slot in cui gli studenti sono disponibili a fare allenamento
        for check in d:
            # spezzo es. '0-1'
            split = check.rsplit('-')
            buckets_days[int(split[0])].append(split[1])

        print(buckets_days)
        
        count = 0
        for d,day in enumerate(buckets_days):
            if len (day) > 0:
                count += 1
    
        if count < int(numero_allenamenti):
                flash(f"il numero di slot inseriti {count} non soddisfa il numero di allenamenti a settimana dell'allievo: {numero_allenamenti}", category='error')
                redirect(url_for('dashboard.modify_student'))
        
        print("è andato tutto bene")
        # devo mettere in una stringa gli slot disponibili perchè il campo sloteliminati della tabella calendario accetta stringhe e non liste
        
        for x,day in enumerate(buckets_days):
            for slots in day:
                slotDisponibili += f"{x}-{slots},"

        actual_student = Allievo.query.filter_by(id=id_allievo).first()
        actual_student.slotdisponibilita = slotDisponibili[:-1]
        db.session.commit()
        flash(f"modifica all'allievo {nome} {cognome} con id {id_allievo} avvenuto con successo",category="success")
        return render_template("modificaallievo.html", user = current_user, student_list = student_list, calendar_list = calendar_list)
    else:
        return render_template("modificaallievo.html", user = current_user, student_list = student_list, calendar_list = calendar_list)
