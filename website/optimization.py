import enum
from operator import index
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import Alias, create_pool_from_url
from . import db
from .models import Allievo
from .models import Calendario
from .models import Allievo
import numpy as np
from pulp import *
from math import ceil
from datetime import time


def stampa_allievi(array,categories):
    for x,cat in enumerate(array):
        print(categories[x],'\n----------------------------------')
        for i,stu in enumerate(cat):
            print(f"studente {i + 1}")
            print(stu)
# ci ritorna la variabile decisionale richiesta nella lista a 4 dimensioni delle variabili decisionali
def receive_decision_variables(array,categoria,allievo,giorno,slot):
    for cat,c in enumerate(array):
        if cat == categoria: # ci prendiamo la categoria esatta
            for alli,i in enumerate(c): 
                if alli == allievo: # ci prendiamo l'alunno esatto di quella categoria
                    for gio,j in enumerate(i):
                        if gio == giorno: # ci prendiamo l'alunno esatto di quella categoria di quel giorno
                            return j[slot]
     # ci prendiamo la variabile decisionale di quel particolare slot,del giorno j,dello studente i e della categoria c (x_c_i_j_k)

def minimum_slot(category):
    if category == "I love tennis" or category == "sat under 8" or category == "sat under 10" or category == "sat under 12" or category == "sat under 14" or category == "sat under 16" or category == "sat under 18" :
        return 2
    else:
        return 3
# stampa la comparazione tra la gli array a 3 dimensioni di allievo e campo (o di 60 o di 90, dipende da cosa si è passato in typeslot) 
# stamperà per ogni studente il numero massimo di allenamenti, la sua matrice di disponibilità e la matrice con gli allenamenti effettivamente assegnati
def print_comparison_3d_array(array1,array2,cat,nAllieviCat,allenamentiSettimana):
    
    for c,categoria in enumerate(array1):
        for i,allievo in enumerate(categoria):
            if i < len(allenamentiSettimana[c]):
                print(f"allievo {i + 1} della categoria {cat[c]} fa nella settimana {(allenamentiSettimana[c])[i]} allenamenti")
                for j in range (6):
                    print(array1[c,i,j,:],array2[c,i,j,:])
            
                print("\n")


optimization = Blueprint('optimization',__name__,template_folder="templates/optimization")
@optimization.route('/', methods = ['GET', 'POST'])
@login_required
def opti():
    if request.method == 'POST':
        # mi prendo l'id del calendario selezionato dall'admin dalla pagina
        # in seguito mi prendro il calendario giusto
        # poi mi prendo gli allievi associati a quel calendario
        idcal = request.form.get("cal")
        calendario = Calendario.query.filter_by(id = idcal).first()
        alunni_del_calendario = Allievo.query.filter_by(id_calendario = calendario.id).all()
        sl = calendario.sloteliminati
        ora_inizio = calendario.oremattina
        ora_fine = calendario.orepomeriggio
        slot_eliminati = (sl[0:len(sl) - 1]).split(",")
        orai = int(ora_inizio[0:2])
        mi = int(ora_inizio[3:5])
        oraf = int(ora_fine[0:2])
        mf = int(ora_fine[3:5])

        secondi_giorno = (oraf * 3600 + mf * 60) - (orai * 3600 + mi * 60)
        numeri_slot = secondi_giorno // (30 * 60) 
        # categories conterrà le categorie presenti degli allievi associati al calendario
        categories = []
        for i,allievo in enumerate(alunni_del_calendario):
            if not(allievo.livello in categories):
                categories.append(allievo.livello)
        print(categories)

        numeri_allenamenti_a_settimana = [[] for x in range(len(categories))] # per salvarmi il numero di allenamenti a settimana richiesta dagli allievi per ogni categoria di categories
        numeri_allievi_per_categoria = [0 for x in range(len(categories))] # per salvarmi il numero di allievi per ogni categoria di categories
        
        # popolo le due variabili appena viste
        for i,allievo in enumerate(alunni_del_calendario):
            numeri_allievi_per_categoria[categories.index(allievo.livello)] += 1
            numeri_allenamenti_a_settimana[categories.index(allievo.livello)].append(allievo.numeroallenamenti)
        

        # Dichiarazione degli array a 4 dimensioni
        # Allievi[c,i,j,k] = 1 se l'allievo i di una categoria c è disponibile nel giorno j nello slot k
        # 0 altrimenti
        # Campi[c,i,j,k] verrà popolata dal problema di ottimizzazione
        Allievi = np.zeros((len(categories),max(numeri_allievi_per_categoria),6,numeri_slot),dtype = int)
        Campi = np.zeros((len(categories),max(numeri_allievi_per_categoria),6,numeri_slot),dtype = int)
        # SOLO SE SI CONO SLOT ELIMINATI, vado a popolare gli slot eliminati del calendario nella matrice Allievi e Campo con il valore 5, anche
        print(slot_eliminati,len(slot_eliminati))
        if len(slot_eliminati) != 1 and slot_eliminati[0] != '':
            for slotEliminato in slot_eliminati:
                Allievi[:,:,int(slotEliminato[0:1]),int(slotEliminato[2:])] = 5
                Campi[:,:,int(slotEliminato[0:1]),int(slotEliminato[2:])] = 5
        # Reinizializzo numeri_allievi_per_categoria perchè devo indicizzare l'allievo della categoria giusto da 0
        # es (sat u8 0, sat u8 1, pre ago u8 2 NO)
        # es (sat u8 0, sat u8 1, pre ago u8 0 SI)
        numeri_allievi_per_categoria = [0 for x in range(len(categories))]
        # inseriamo in Allievi le disponibilità di tutti gli allievi di tutte le categorie in tutti i giorni
        for i,alunno in enumerate(alunni_del_calendario):
            #bucket_days = [ [] for d in range(6)]
            l = (alunno.slotdisponibilita)
            livelli = l[0:len(l) - 1].split(",")
            for item in livelli:
                Allievi[categories.index(alunno.livello),numeri_allievi_per_categoria[categories.index(alunno.livello)],int(item[0:1]),int(item[2:])] = 1
            numeri_allievi_per_categoria[categories.index(alunno.livello)] += 1
        print(numeri_allievi_per_categoria)
        stampa_allievi(Allievi,categories)
        
        # creazioni del problema di programmazione lineare intera
        problem = LpProblem("Maximize_student", sense=LpMaximize)
        # variabili decisionali x es x0,1,3,4 (studente 1 della categoria i love tennis nel giorno mercoledi allo slot 4)
        # LA RIGA -> if ((not(f"{j}-{k}") in slot_eliminati) and (numeri_allievi_per_categoria[c] != 0))
        # mi serve per filtrare le variabili decisionali che devono essere inizializzate in students_variables
        # non ci vanno quelle variabili decisionali in cui ci sono degli slot eliminati e quando i numeri di allievi di una certa categoria sono diverso da 0
        students_variables =[
            [
            [   
            [LpVariable(name=f"x_{c+1},{i+1},{j+1},{k+1}", cat=LpBinary) for k in range(numeri_slot) if (not (f"{j}-{k}") in slot_eliminati)]
                for j in range(6)
            ] for i in range(max(numeri_allievi_per_categoria))
        ] for c in range(len(categories))
        ]
        # funzione obiettivo da massimizzare
        problem += lpDot(1,students_variables)
        
        # per stampare le variabili decisionali presenti attualmente create
        '''
        for i,cat in enumerate(students_variables):
            if numeri_allievi_per_categoria[i] != 0:
                print(f"categoria {categories[i]}")
            else:
                continue
            for j,student in enumerate(cat):
                print(f"studente{j+1}")
                for week in student:
                    if len(week) != 0:
                        print(week) 
        '''
        
        #---------------------------vincoli------------------------
        # 2) vincolo // ogni studente si allena al massimo una volta al giorno
        # per farlo dobbiamo controllare l'array 3d allievo e vedere quale studente per un certo giorno per un certo slot è libero (1, 0 altrimenti)
        # una volta capito se è libero dobbiamo prendere la variabile decisionale corrispondente (di quello studente per quel certo giorno per quel certo slot) 
        # e mettere tutte le variabili decisionali di uno studente di un giorno (o più) in una espressione lineare e controllare che sia <=1
        # 1) vincolo // aggiunto se no uno studente non ha disponibilità per un certo giorno per uno certo slot la variabile decisionale corrispondente è uguale a 0
        # i = studente, j = giorno, k = slot
        students_one = []
        students_zero = []
        for cat,c in enumerate(Allievi):
            #print(f"categoria = {categories[cat]}")
            ms = minimum_slot(categories[cat])
            for allievo,i in enumerate(c):
                #print(f"allievo = {allievo}")        
                for giorni,j in enumerate(i):
                    for slots,k in enumerate(j):
                        if k == 0:
                            students_zero.append(receive_decision_variables(students_variables,cat,allievo,giorni,slots))
                            students_one.append(0)
                        if k == 1: # perchè potrebbe essere 5 che sta per slot eliminato
                            students_one.append(receive_decision_variables(students_variables,cat,allievo,giorni,slots))      
                    #print(f"students_one{students_one} del giorno{giorni}")
                    if not(len(students_zero) == 0):
                        problem += lpSum(1 * students_zero) == 0
                        
                    if not(len(students_one) == 0):
                        if len(students_one) >= ms:
                            if ms == 2:
                                students_one_str = [x.name if x != 0 else 0 for x in students_one]
                                print(students_one_str)
                                z = 0
                                while(z < len(students_one_str)):
                                    if students_one_str[z] == 0:
                                        z = z + 1
                                        continue
                                    elif students_one_str.index(students_one_str[z]) == len(students_one_str) - 1:
                                        problem += lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1])
                                        print(lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1]))
                                        break
                                    elif students_one_str[z + 1] == 0:
                                        problem += lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1])
                                        print(lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1]))
                                        z = z + 1
                                    else:
                                        problem += lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1])
                                        print(lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1]))
                                        z = z + 2
                              
                            else: #ms == 3 
                                students_one_str = [x.name if x != 0 else 0 for x in students_one]
                                print(students_one_str)
                                z = 0
                                while(z < len(students_one_str)):

                                    if students_one_str[z] == 0:
                                        z = z + 1
                                        continue

                                    elif students_one_str.index(students_one_str[z]) == len(students_one_str) - 1:
                                        problem += lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1])
                                        problem += lpDot(1, students_one[z - 1]) <= lpDot(1, students_one[z - 2])

                                        print(lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1]))
                                        print(lpDot(1, students_one[z - 1]) <= lpDot(1, students_one[z - 2]))
                                        z = z + 1
                                        break

                                    elif students_one_str.index(students_one_str[z + 1]) == len(students_one_str) - 1:
                                        problem += lpDot(1, students_one[z + 1]) <= lpDot(1, students_one[z])
                                        problem += lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1])
                                        
                                        print(lpDot(1, students_one[z + 1]) <= lpDot(1, students_one[z]))
                                        print(lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1]))
                                        break
                                    
                                    elif students_one_str[z + 1] == 0:
                                        problem += lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1])
                                        problem += lpDot(1, students_one[z - 1]) <= lpDot(1, students_one[z - 2])
                                        
                                        print(lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1]))
                                        print(lpDot(1, students_one[z - 1]) <= lpDot(1, students_one[z - 2]))
                                        z = z + 1
                                    elif students_one_str[z + 2] == 0:
                                        problem += lpDot(1, students_one[z + 1]) <= lpDot(1, students_one[z])
                                        problem += lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1])
                                        
                                        print(lpDot(1, students_one[z + 1]) <= lpDot(1, students_one[z]))
                                        print(lpDot(1, students_one[z]) <= lpDot(1, students_one[z - 1]))
                                        z = z + 2

                                    else:# caso in cui students_one_str[z] ha davanti a se students_one_str[z + 1] e students_one_str[z + 2] variabili decisionali
                                        problem += lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1])
                                        problem += lpDot(1, students_one[z + 1]) == lpDot(1, students_one[z + 2])
                                        
                                        print(lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1]))
                                        print(lpDot(1, students_one[z + 1]) == lpDot(1, students_one[z + 2]))
                                        z = z + 3 
                                #print(students_one_str)
                                '''
                                for z in range(0,len(students_one),1):
                                    
                                    problem += lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1])
                                    problem += lpDot(1, students_one[z + 1]) == lpDot(1, students_one[z + 2])

                                    if students_one_str.index(students_one_str[z + 2]) == len(students_one_str) - 1:
                                        break 
                                '''
                        problem += lpDot(1,students_one) <= ms #solo un allenamento al giorno (2 slot) 
                    students_one.clear()
                    students_zero.clear()
            print("-" * 50)
        
        # vincolo 3 // per ogni slot ci devono essere al massimo 4 allievi (fatto per ogni categoria)
        for cat, c in enumerate(categories):
            print(f"categoria{categories[cat]} cat {cat} in cui ci sono {numeri_allievi_per_categoria[cat]}")

            for day in range(6):
                for slot in range(numeri_slot):
                    for student in range(numeri_allievi_per_categoria[cat]):
                        #print(f"student {student} in range {numeri_allievi_per_categoria[cat]}")
                        #print(day,slot,student,f"valore slot {Allievi[cat,student,day,slot]}")
                        if(Allievi[cat,student,day,slot] == 1):
                            #print(cat,student,day,slot)
                            students_one.append(receive_decision_variables(students_variables,cat,student,day,slot))
        
                    if not(len(students_one) == 0):
                        problem += lpSum(1 * students_one) <= 4
                        #print(lpSum(1 * students_one) <= 4)
                        students_one.clear()
      
        # vincolo 4 // uno studente si allena al massimo il numero di allenamenti da lui dichiarato
        for cat,c in enumerate(Allievi):
            print(f"categoria = {categories[cat]}")
            ms = minimum_slot(categories[cat])
            for allievo,i in enumerate(c):
                #print(f"indice cat: {cat} e indice allievo: {allievo}")
                #print(f"numeri_allievi_per_categoria[cat] -> {numeri_allievi_per_categoria[cat]}")
                if allievo < (len(numeri_allenamenti_a_settimana[cat])):
                    #print(f"studente = {s+ 1}")
                    for giorno,j in enumerate(i):        
                        for slot,k in enumerate(j):
                            if k == 1:
                                students_one.append(receive_decision_variables(students_variables,cat,allievo,giorno,slot)) 
                    
                    problem += lpSum(1 * students_one) <= ( ((numeri_allenamenti_a_settimana[cat])[allievo]) * ms)
                    students_one.clear()

        # risoluzione dei problemi
        status = problem.solve(PULP_CBC_CMD(msg = False))
        print(problem)
        for v in problem.variables():
            if v.varValue == 1.0:
                temp = (v.name).rsplit(",") 
                Campi[int((temp[0])[2:]) - 1,int(temp[1]) - 1,int(temp[2]) - 1, int(temp[3]) - 1] = 1
        
        
        print_comparison_3d_array(Allievi,Campi,categories,numeri_allievi_per_categoria,numeri_allenamenti_a_settimana)
        print ("valore ottimo per gli studenti scelti ", problem.objective.value())
        print(numeri_allievi_per_categoria)
        print(numeri_allenamenti_a_settimana)
        print(categories)
        
        return render_template("dashopti.html", user = current_user)
    else:
        return render_template("dashopti.html", user = current_user)