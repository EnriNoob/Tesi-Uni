
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import false, true




from . import db
from .models import Allievo as Al
from .models import Calendario
import numpy as np
from pulp import *
import json

# stampa gli allievi delle categorie
def stampa_allievi(array,categories):
    for x,cat in enumerate(array):
        print(categories[x],'\n----------------------------------')
        for i,stu in enumerate(cat):
            print(f"studente {i + 1}")
            print(stu)

def receive_student_decision_variables(array,categoria,allievo,giorno,slot):
    for cat,c in enumerate(array):
        if cat == categoria: # ci prendiamo la categoria esatta
            for alli,i in enumerate(c): 
                if alli == allievo: # ci prendiamo l'alunno esatto di quella categoria
                    for gio,j in enumerate(i):
                        if gio == giorno: # ci prendiamo l'alunno esatto di quella categoria di quel giorno
                            return j[slot]# ci prendiamo la variabile decisionale di quel particolare slot,del giorno j,dello studente i e della categoria c (x_c_i_j_k)

def print_comparison_3d_array(array1,array2,allenamentiSettimana,idAlievi,cat):
    
    for c,categoria in enumerate(array1):
        print( "-" * 30 + f"categoria {cat[c]}" + "-" * 30)
        print('\n')
        for i,allievo in enumerate(categoria):
            # ci sono categoria che hanno un numero di allievi minore rispetto al numero di allievi massimo di una certa categoria
            # se non lo mettessi andrebbe in list index out of range
            if i < len(allenamentiSettimana[c]):
                print(f"allievo {i + 1} con id {idAlievi[c][i]} della categoria {cat[c]} fa nella settimana {(allenamentiSettimana[c])[i]} allenamenti")
                for j in range (6):
                    print(array1[c,i,j,:],array2[c,i,j,:])
                print("\n")

# ci ritorna la variabile deciosionale del corrsipettivo giorno e slot passati  come parametri nella funzione
def receive_slots_decision_variables(array,giorno,slot):
    l = array[giorno]
    for i in l:
        temp = (str(i)).rsplit(",")
        ora =  int(temp[1])
        if ora == slot + 1: # + 1 perchè lo slot dal parametro partono da 0 mentre in array gli slot partono da 1
            return i

def check_already_in(slot,array):
    print(slot,array)
    found = False
    if len(array) == 0:
        return found
    
    elif slot in array:
        found = True
    else:
        found = False

    return found

def receive_boh(array1,array2,j,k):
    
    for key, value in array1.items():
        temp = value.split("_")
        if int(temp[1][1:2]) == j + 1 and int(temp[1][3:]) == k + 1 and key in array2:
            return temp[0]
        
    return 0

optimization = Blueprint('optimization',__name__,template_folder="templates/optimization")
@optimization.route('/', methods = ['GET', 'POST'])
@login_required
def opti():
    students_list = Al.query.all()
    calendar_list = Calendario.query.all()
    if request.method == 'POST':
        # mi prendo l'id del calendario selezionato dall'admin dalla pagina
        # in seguito mi prendro il calendario giusto
        # poi mi prendo gli allievi associati a quel calendario
        idcal = request.form.get("idcal")
        print(idcal)
        alunni_soddisfatti = []
        alunni_insoddisfatti = []
        calendario = Calendario.query.filter_by(id = idcal).first()
        alunni_del_calendario = Al.query.filter_by(id_calendario = calendario.id).all()
        # dati del calendario
        sl = calendario.sloteliminati
        ora_inizio = calendario.oremattina
        ora_fine = calendario.orepomeriggio
        slot_eliminati = (sl[0:len(sl) - 1]).split(",")
        orai = int(ora_inizio[0:2])
        mi = int(ora_inizio[3:5])
        oraf = int(ora_fine[0:2])
        mf = int(ora_fine[3:5])
        # dobbiamo calcolarci il numero degli slot durante il giorno
        secondi_giorno = (oraf * 3600 + mf * 60) - (orai * 3600 + mi * 60)
        numeri_slot = secondi_giorno // (calendario.numeroslot * 60) 
        # categories conterrà le categorie presenti degli allievi associati al calendario
        categories = []
        
        for i,allievo in enumerate(alunni_del_calendario):
            if not(allievo.livello in categories):
                categories.append(allievo.livello)
            
        print(categories)

        numeri_allenamenti_a_settimana = [[] for x in range(len(categories))] # per salvarmi il numero di allenamenti a settimana richiesta dagli allievi per ogni categoria di categories
        numeri_allievi_per_categoria = [0 for x in range(len(categories))] # per salvarmi il numero di allievi per ogni categoria di categories
        id_allievi_per_categoria = [[] for x in range(len(categories))] # per salvarmi gli id degli studenti di ogni categoria di categories
        
        # popolo le tre variabili appena viste
        for i,allievo in enumerate(alunni_del_calendario):
            numeri_allievi_per_categoria[categories.index(allievo.livello)] += 1
            numeri_allenamenti_a_settimana[categories.index(allievo.livello)].append(allievo.numeroallenamenti)
            id_allievi_per_categoria[categories.index(allievo.livello)].append(allievo.id)
        
        print(numeri_allievi_per_categoria)
        print(f"totale allievi {sum(numeri_allievi_per_categoria)}")
        print(numeri_allenamenti_a_settimana)
        print(id_allievi_per_categoria)

        # Dichiarazione degli array a 4 dimensioni
        # Allievi[c,i,j,k] = 1 se l'allievo i di una categoria c è disponibile nel giorno j nello slot k
        # 0 altrimenti
        # Campi[c,i,j,k] verrà popolata dal problema di ottimizzazione
        Allievi = np.zeros((len(categories),max(numeri_allievi_per_categoria),6,numeri_slot),dtype = int)
        Campi = np.zeros((len(categories),max(numeri_allievi_per_categoria),6,numeri_slot),dtype = int)
        #Campi = np.zeros((len(categories),max(numeri_allievi_per_categoria),6,numeri_slot),dtype = int)

        # Reinizializzo numeri_allievi_per_categoria perchè devo indicizzare l'allievo della categoria giusto da 0
        # es (sat u8 0, sat u8 1, pre ago u8 2 NO)
        # es (sat u8 0, sat u8 1, pre ago u8 0 SI)
        numeri_allievi_per_categoria = [0 for x in range(len(categories))]
        # inseriamo in Allievi le disponibilità di tutti gli allievi di tutte le categorie che hanno riferito
        for i,alunno in enumerate(alunni_del_calendario):
            #bucket_days = [ [] for d in range(6)]
            l = (alunno.slotdisponibilita)
            livelli = l.split(",")
            for item in livelli:
                Allievi[categories.index(alunno.livello),numeri_allievi_per_categoria[categories.index(alunno.livello)],int(item[0:1]),int(item[2:])] = 1
            numeri_allievi_per_categoria[categories.index(alunno.livello)] += 1

        
        #stampa_allievi(Allievi,categories)

        # creazioni del problema di programmazione lineare intera
        problem = LpProblem("Maximize_student", sense=LpMaximize)
        # variabili decisionali x es x0,1,3,4 (studente 1 della categoria i love tennis nel giorno mercoledi allo slot 4)
        # LA RIGA -> if ((not(f"{j}-{k}") in slot_eliminati) and (numeri_allievi_per_categoria[c] != 0))
        # mi serve per filtrare le variabili decisionali che devono essere inizializzate in students_variables
        # non ci vanno quelle variabili decisionali in cui ci sono degli slot eliminati e quando i numeri di allievi di una certa categoria sono diverso da 0
        students_decision_variables =[
            [
            [   
            [LpVariable(name=f"x_{c+1},{i+1},{j+1},{k+1}", cat=LpBinary) for k in range(numeri_slot)]
                for j in range(6)
            ] for i in range(max(numeri_allievi_per_categoria))
        ] for c in range(len(categories))
        ]
        ccategories_decisione_variables = [LpVariable(name = f"c{i + 1}", cat=LpBinary) for i in range(150)]

        slots_decision_variables = [
            [LpVariable(name=f"y{j+1},{k+1}", cat=LpBinary) for k  in range(numeri_slot)]
                for j in range (6)
        ]
        print(slots_decision_variables)
        # funzione obiettivo da massimizzare (ovvero massimizzare il numero di studenti soddisfatti)
        problem += lpDot(1,[students_decision_variables, slots_decision_variables])
        #problem += lpDot(1,[slots_decision_variables])

        # vincolo 1 (students_one) : ogni studente indipendentemente dalla categoria, si allena al giorno una sola volta (quindi un solo slot permesso)
        # vincolo 2 (students_zero) : vengono messe a 0 le variabili decisionali in cui l'allievo non ha messo disponibilita
        students_one = []
        students_zero = []
        for c,cat in enumerate(Allievi):
            #print(f"categoria = {categories[cat]}")
            for i,allievo in enumerate(cat):
                #print(f"allievo = {allievo}")
                if i < numeri_allievi_per_categoria[c]:
                    for j,giorni in enumerate(allievo):
                        for k,slots in enumerate(giorni):
                            if slots == 1:
                                students_one.append(receive_student_decision_variables(students_decision_variables,c,i,j,k))
                            if slots == 0:
                                students_zero.append(receive_student_decision_variables(students_decision_variables,c,i,j,k))
                                
                        if students_one:
                            problem += lpDot(1,students_one) <= 1
                        if students_zero:
                            problem += lpDot(1,students_zero) == 0

                        students_one.clear()
                        students_zero.clear()
        
        # vincolo 3: per ogni slot ci devono essere al massimo 4 allievi (fatto per ogni categoria) 
        for c, cat in enumerate(categories):
            print(f"categoria{categories[c]} cat {c} in cui ci sono {numeri_allievi_per_categoria[c]}")
            for day in range(6):
                for slot in range(numeri_slot):
                    for student in range(numeri_allievi_per_categoria[c]):
                        #print(f"student {student} in range {numeri_allievi_per_categoria[cat]}")
                        #print(day,slot,student,f"valore slot {Allievi[cat,student,day,slot]}")
                        if(Allievi[c,student,day,slot] == 1):
                            #print(cat,student,day,slot)
                            students_one.append(receive_student_decision_variables(students_decision_variables,c,student,day,slot))

                    if students_one:
                        problem += lpSum(1 * students_one) <= 4
                        #print(lpSum(1 * students_one) <= 4)
                        students_one.clear()
        # vincolo 4 : ogni studente deve allenarsi tante volte quanto ne ha richiesto l'allievo stesso
                        
        for c,cat in enumerate(Allievi):
            print(f"categoria = {categories[c]}")
            
            for allievo,i in enumerate(cat):
                #print(f"indice cat: {cat} e indice allievo: {allievo}")
                #print(f"numeri_allievi_per_categoria[cat] -> {numeri_allievi_per_categoria[cat]}")
                if allievo < (len(numeri_allenamenti_a_settimana[c])):
                    #print(f"studente = {s+ 1}")
                    for giorno,j in enumerate(i):        
                        for slot,k in enumerate(j):
                            if k == 1:
                                students_one.append(receive_student_decision_variables(students_decision_variables,c,allievo,giorno,slot)) 
                    
                    problem += lpSum(1 * students_one) <= (((numeri_allenamenti_a_settimana[c])[allievo]))
                    students_one.clear()
        
        # vincolo 5: per ogni slot ci devono essere al massimo 4 allievi ma stavolta di una sola categoria
        # (allievi di diverse categorie non si allenano insieme)
        categorie_segnaposto = {}
        cont = 0  
        for day in range(6):
            for slot in range(numeri_slot):
                temp = []
                for c, cat in enumerate(categories):
                    for student in range(numeri_allievi_per_categoria[c]):

                        #print(f"student {student} in range {numeri_allievi_per_categoria[cat]}")
                        #print(day,slot,student,f"valore slot {Allievi[cat,student,day,slot]}")
                        if(Allievi[c,student,day,slot] == 1):
                            #print(cat,student,day,slot)
                            students_one.append(receive_student_decision_variables(students_decision_variables,c,student,day,slot))

                    if students_one:
                        ns = len(students_one) if len(students_one) < 4 else 4
                        problem += lpSum(1 * students_one) >= lpDot(ns,ccategories_decisione_variables[cont])
                        categorie_segnaposto[ccategories_decisione_variables[cont].name] = f"{categories[c]}_{receive_slots_decision_variables(slots_decision_variables,day,slot)}"
                        temp.append(ccategories_decisione_variables[cont])
                        cont += 1
                        #print(lpSum(1 * students_one) <= 4)
                        students_one.clear()
                problem+= lpDot(1,temp) >= lpDot(1,receive_slots_decision_variables(slots_decision_variables,day,slot))
        
        # vincolo 6: gli slot in cui non stati richiesti da nessuno li metto a 0
        buckets_day_for_all_categories = [[] for d in range(6)]   
        # Ora raggruppo tutti gli slot veramente assegnati nei bucket di tutte le categorie
        for c,categoria in enumerate(Allievi):
            for i,allievi in enumerate(categoria):
                for j,giorni in enumerate(allievi): 
                    for k,slots in enumerate(giorni):
                        if Allievi[c,i,j,k] == 1:
                            if k in buckets_day_for_all_categories[j]:
                                pass
                            else:
                                buckets_day_for_all_categories[j].append(k)

        print(buckets_day_for_all_categories)
        # imposto gli slot mai utilizzati a 0 (potrebbero essere degli slot eliminati dal calendario)
        for d,day in enumerate(buckets_day_for_all_categories):
            for z in range(numeri_slot):
                if z in day:
                    continue
                else:
                    problem += lpDot(1,receive_slots_decision_variables(slots_decision_variables,d,z)) == 0
                    #print(receive_slots_decision_variables(slots_decision_variables,z,d))


        print(problem)
        solve = problem.solve(PULP_CBC_CMD(msg = False))

        res = np.zeros((6,numeri_slot),dtype = int)
        store_c = []
        for v in problem.variables():
            if "y" in v.name and v.varValue == 1:
                temp = (v.name).rsplit(",")
                #print(temp[0]+","+temp[1])
                res[int((temp[0])[1:]) - 1][int(temp[1]) - 1] = 1

            if "x" in v.name and v.varValue == 1:
                #print(v.name, "=", v.varValue)
                temp = (v.name).rsplit(",") 
                Campi[int((temp[0])[2:]) - 1,int(temp[1]) - 1,int(temp[2]) - 1, int(temp[3]) - 1] = 1

            if "c" in v.name:
                print(v.name, "=", v.varValue)
                if v.varValue == 1:
                    store_c.append(v.name)
                
              
        print_comparison_3d_array(Allievi,Campi,numeri_allenamenti_a_settimana,id_allievi_per_categoria,categories)
        print(res)
        print ("valore ottimo degli slot minimi ", problem.objective.value())
        for key, value in categorie_segnaposto.items():
            print(key, ":", value)

        print(store_c)
        unsatified = 0
        # ora dobbiamo trovare a chi non è stato soddisfatto
        for c,categoria in enumerate(Campi):
            for i,allievi in enumerate(categoria):
                if i < (len(numeri_allenamenti_a_settimana[c])):
                    somma = 0
                    for j,giorni in enumerate(allievi):
                        for k,slots in enumerate(giorni):
                            if Campi[c,i,j,k] == 1:
                                somma += 1
               
                    if somma != (numeri_allenamenti_a_settimana[c][i]):
                        print(f"studente{i + 1} della categoria {categories[c]} rimarrà insodisfatto")
                        alunni_insoddisfatti.append(Al.query.filter_by(id = id_allievi_per_categoria[c][i]).first())
                        Campi[c,i,:,:] = 0

        all_info = [["" for i in range(6)] for k in range(numeri_slot)]
        
        for c,cat in enumerate(Campi):
            for i,allievi in enumerate(cat):
                print(f"studente{i + 1} della categoria {categories[c]}")
                if i < (numeri_allievi_per_categoria[c]):
                    somma = 0
                    for j,giorni in enumerate(allievi):
                        for k,slots in enumerate(giorni):
                            if Campi[c,i,j,k] == 1 and categories[c] == receive_boh(categorie_segnaposto,store_c,j,k): 
                                somma += 1
                    
                    if somma == (numeri_allenamenti_a_settimana[c][i]): 
                        print(f"studente{i + 1} della categoria {categories[c]} è stato soddisfatto")
                        temp = Al.query.filter_by(id = id_allievi_per_categoria[c][i]).first()

                        alunni_soddisfatti.append(temp)
                    else:
                        print(f"studente{i + 1} della categoria {categories[c]} rimarrà insodisfatto")
                        if not (Al.query.filter_by(id = id_allievi_per_categoria[c][i]).first() in alunni_insoddisfatti):
                            alunni_insoddisfatti.append(Al.query.filter_by(id = id_allievi_per_categoria[c][i]).first())
                        Campi[c,i,:,:] = 0
        
        for c,cat in enumerate(Campi):
            for i,allievi in enumerate(cat):
                print(f"studente{i + 1} della categoria {categories[c]}")
                if i < (numeri_allievi_per_categoria[c]):
                    for j,giorni in enumerate(allievi):
                        for k,slots in enumerate(giorni):
                            if Campi[c,i,j,k] == 1 and categories[c] == receive_boh(categorie_segnaposto,store_c,j,k):
                                temp = Al.query.filter_by(id = id_allievi_per_categoria[c][i]).first()
                                all_info[k][j] += f"{categories[c]}_{temp.nome}_{temp.cognome}/"
                                
        print_comparison_3d_array(Allievi,Campi,numeri_allenamenti_a_settimana,id_allievi_per_categoria,categories)
        for row in all_info:
            print(row)

        return render_template("dashoptires.html", user = current_user, calendar_list = calendar_list, students_list = students_list,risultato = all_info, numeroslot=numeri_slot, satisfied_student = alunni_soddisfatti, unsatisfied_student = alunni_insoddisfatti,)
    else:
        return render_template("dashopti.html", user = current_user, calendar_list= calendar_list, students_list = students_list)

