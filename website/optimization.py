
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import false, true

from . import db
from .models import Allievo
from .models import Calendario
import numpy as np
from pulp import *


# stampa gli allievi delle categorie
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
                            return j[slot]# ci prendiamo la variabile decisionale di quel particolare slot,del giorno j,dello studente i e della categoria c (x_c_i_j_k)

# ci ritorna la variabile deciosionale del corrsipettivo giorno e slot passati  come parametri nella funzione
def receive_slots_decision_variables(array,giorno,slot):
    l = array[giorno]
    for i in l:
        temp = (str(i)).rsplit(",")
        ora =  int(temp[1])
        if ora == slot + 1: # + 1 perchè lo slot dal parametro partono da 0 mentre in array gli slot partono da 1
            return i
        

# ci ritona il numero di slot minimo di una certa categoria
def minimum_slot(category):
    if category == "I love tennis" or category == "sat under 8" or category == "sat under 10" or category == "sat under 12" or category == "sat under 14" or category == "sat under 16" or category == "sat under 18" :
        return 2 # categorie che fanno allenamento da un'ora (2 slot)
    else:
        return 3 # categorie che fanno allenamento da un'ora e mezza (3 slot)

# stampa la comparazione tra la gli array a 4 dimensioni di array1 e array2 (collezione di cubi)
# si vedrà per ogni allievo di ogni categoria gli slot da lui dichiarati disponibili a sinistra,
# e a destra gli slot allocati dall'algoritmo a destra
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

# mi serve per controllare se check1,check2 e check3 (questo opzionale) se sono già presenti in pot
def check_already_in(check1,check2,check3,pot,ms):
    # inizializzo found a falso così se in ms == 2 o ms == 3 i tre o i due campi non sono presenti in pot
    # ritorno falso che sta per "non trovato"
    found = False
    # se len di pot = 0 significa che siamo all'inizio della ricerca dei doppioni 
    if len(pot) == 0:
        return False
    # controllo ms
    if ms == 2:
        # scorro in pot a passi di due (due slot)
        for i in range(0,len(pot),ms):
            if check1 == pot[i] and check2 == pot[i + 1]:
                found = True # se entrambi i valori coincidono con la coppia in pot setto found a True
    else:
        # scorro in pot a passi di 3 (due slot)
        for i in range(0,len(pot),ms):
            if check1 == pot[i] and check2 == pot[i + 1] and check3 == pot[i + 2]:
                found = True # se i tre valori coincidono con la tripla in pot setto found a True

    return found

def check_same_slots(slot1,slot2,slot3,giorno,buckets_dfc_real,categories,atcual_category,array):

    res = [[] for _ in range(len(categories))]
    for c,cat in enumerate (buckets_dfc_real):
        # scorriamo nelle categorie e nei giorni in cui slot1, slot2 o slot3 andranno in conflitto
        # con gli slot degli altri giorni di tutte le categorie (anche se stessa purtroppo)
        ms = minimum_slot(categories[c])
        giorno_check = cat[giorno]
        #print(giorno_check)
        # print(type(giorno_check))

        if ms == 2:  # stiamo scorrendo in una categoria con allenamenti da un'ora (2 slot)
            if slot3 == 0: # caso 2 slot in confronto con 2 slot 
                for k in range(0,len(giorno_check),2):
                    if slot1 == giorno_check[k] and slot2 == giorno_check[k +1] and atcual_category == c:
                        continue # non ci interessa che slot1 e slot2 vadano in conflitto con se stessi nella stessa categoria nello stesso giorno
                    if slot1 == giorno_check[k] or slot1 == giorno_check[k + 1]\
                        or slot2 == giorno_check[k] or slot2 == giorno_check[k + 1]:
                        res[c].append([receive_slots_decision_variables(array,giorno,giorno_check[k]), receive_slots_decision_variables(array,giorno,giorno_check[k + 1])])
                    
            else: # caso 3 slot a in confronto con 2 slot
                for k in range(0,len(giorno_check),2):
                    if slot1 == giorno_check[k] or slot1 == giorno_check[k + 1]\
                        or slot2 == giorno_check[k] or slot2 == giorno_check[k + 1]\
                        or slot3 == giorno_check[k] or slot3 == giorno_check[k + 1]:
                        res[c].append([receive_slots_decision_variables(array,giorno,giorno_check[k]), receive_slots_decision_variables(array,giorno,giorno_check[k + 1])])

        if ms == 3: # stiamo scorrendo in una categoria con allenamenti da un'ora e mezza (3  slot)
            if slot3 == 0: # caso 2 slot in confronto con 3 slot
                for k in range(0,len(giorno_check),3):
                    if slot1 == giorno_check[k] or slot1 == giorno_check[k + 1] or slot1 == giorno_check[k + 2]\
                    or slot2 == giorno_check[k] or slot2 == giorno_check[k + 1] or slot2 == giorno_check[k + 2]:
                        res[c].append([receive_slots_decision_variables(array,giorno,giorno_check[k]), receive_slots_decision_variables(array,giorno,giorno_check[k + 1]), receive_slots_decision_variables(array,giorno,giorno_check[k + 2])])
            else : # caso 3 slot in confronto con 3 slot
                for k in range(0,len(giorno_check),3):
                    if slot1 == giorno_check[k] and slot2 == giorno_check[k +1]\
                        and slot3 == giorno_check[k + 2] and atcual_category == c :
                        continue # non ci interessa che slot1 e slot2 e slot 3 vadano in conflitto con se stessi nella stessa categoria nello stesso giorno

                    if slot1 == giorno_check[k] or slot1 == giorno_check[k + 1] or slot1 == giorno_check[k + 2]\
                    or slot2 == giorno_check[k] or slot2 == giorno_check[k + 1] or slot2 == giorno_check[k + 2]\
                    or slot3 == giorno_check[k] or slot3 == giorno_check[k + 1] or slot3 == giorno_check[k + 2]:
                        res[c].append([receive_slots_decision_variables(array,giorno,giorno_check[k]), receive_slots_decision_variables(array,giorno,giorno_check[k + 1]), receive_slots_decision_variables(array,giorno,giorno_check[k + 2])])
    return res      

def checks_no_conflit(collapse_sl,cate):
    no_conflicts = 0
    for g in collapse_sl:
        if len(g) == 0:
            no_conflicts += 1

    if no_conflicts == len(cate):
        return True
    else:
        return False       

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
        id_allievi_per_categoria = [[] for x in range(len(categories))] # per salvarmi gli id degli studenti di ogni categoria di categories
        
        # popolo le tre variabili appena viste
        for i,allievo in enumerate(alunni_del_calendario):
            numeri_allievi_per_categoria[categories.index(allievo.livello)] += 1
            numeri_allenamenti_a_settimana[categories.index(allievo.livello)].append(allievo.numeroallenamenti)
            id_allievi_per_categoria[categories.index(allievo.livello)].append(allievo.id)
        
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
        # inseriamo in Allievi le disponibilità di tutti gli allievi di tutte le categorie che hanno riferito
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
        # funzione obiettivo da massimizzare (ovvero massimizzare il numero di studenti soddisfatti)
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
                            #students_one.append(0)
                        if k == 1: # perchè potrebbe essere 5 che sta per slot eliminato
                            students_one.append(receive_decision_variables(students_variables,cat,allievo,giorni,slots))      
                    #print(f"students_one{students_one} del giorno{giorni}")
                    if not(len(students_zero) == 0):
                        problem += lpSum(1 * students_zero) == 0
                        
                    if not(len(students_one) == 0):
                        if len(students_one) >= ms:
                            if ms == 2:
                                #students_one_str = [x.name if x != 0 else 0 for x in students_one]
                                #print(students_one_str)
                                for z in range(0,len(students_one), 2):
                                    problem += lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1])
                            
                            else: #ms == 3 
                                #students_one_str = [x.name if x != 0 else 0 for x in students_one]
                                #print(students_one_str)
                                for z in range(0,len(students_one), 3):
                                    problem += lpDot(1, students_one[z]) == lpDot(1, students_one[z + 1])
                                    problem += lpDot(1, students_one[z + 1]) == lpDot(1, students_one[z + 2])
                        problem += lpDot(1,students_one) <= ms #solo un allenamento al giorno (3 o 2 slot) 
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
                    
                    problem += lpSum(1 * students_one) <= (((numeri_allenamenti_a_settimana[cat])[allievo]) * ms)
                    students_one.clear()

        # risoluzione dei problemi
        status = problem.solve(PULP_CBC_CMD(msg = False))
        print(problem)
        print(status)
        
        # le variabili decisionali sono state allocate/decise dall'algorimo, quindi popolo Campi
        for v in problem.variables():
            if v.varValue == 1.0:
                # spezzo per es temp = (v.name).rsplit(",") :  x_1,1,2,3
                # int((temp[0])[2:]) - 1 = 1 //categoria
                # int(temp[1]) - 1 = 1 //allievo
                # int(temp[2]) - 1 = 2  //giorno
                # int(temp[3]) - 1 = 3  //slot
                # int mi serve per avere gli indici in intero e - 1 perchè gli inidici in Campi partono da 0
                temp = (v.name).rsplit(",") 
                Campi[int((temp[0])[2:]) - 1,int(temp[1]) - 1,int(temp[2]) - 1, int(temp[3]) - 1] = 1
        
        
        print_comparison_3d_array(Allievi,Campi,numeri_allenamenti_a_settimana,id_allievi_per_categoria,categories)
        print ("valore ottimo per gli studenti scelti ", problem.objective.value())
        print(numeri_allievi_per_categoria)
        print(numeri_allenamenti_a_settimana)
        print(id_allievi_per_categoria)
        print(categories)
        
        # ora dobbiamo trovare a chi non è stato soddisfatto
        for c,categoria in enumerate(Campi):
            ms = minimum_slot(categories[c])
            for i,allievi in enumerate(categoria):
                if allievo < (len(numeri_allenamenti_a_settimana[c])):
                    sum = 0
                    for j,giorni in enumerate(allievi):
                        for k,slots in enumerate(giorni):
                            if Campi[c,i,j,k] == 1:
                                sum += 1
               
                    if sum != (numeri_allenamenti_a_settimana[c][i] * ms):
                        print(f"studente{i + 1} della categoria {categories[c]} rimarrà insodisfatto")
                        Campi[c,i,:,:] = 0
        
        # creo i bucket dove ogni bucket è un giorno (6 giorni)
        # in ogni giorno ci sono tutti gli slot che l'algoritmo ha assegnato e che dopo abbiamo controllato chi era soddisfatto
        # questi bucket ci sono per ogni categoria ( for c in range(len(categories)))
        buckets_day_for_categories = [[ [] for d in range(6) ] for c in range(len(categories))]
        buckets_day_for_categories_real = [[ [] for d in range(6) ] for c in range(len(categories))]
        
        # Ora raggruppo tutti gli slot veramente assegnati nei bucket di tutte le categorie
        for c,categoria in enumerate(Campi):
            for i,allievi in enumerate(categoria):
                for j,giorni in enumerate(allievi): 
                    for k,slots in enumerate(giorni):
                        if Campi[c,i,j,k] == 1:
                            buckets_day_for_categories[c][j].append(k)
        
        # stampo i bucket
        for c,cat in enumerate(buckets_day_for_categories):
            print(f"categoria {categories[c]}")
            for giorni in cat:
                print (giorni)
        print("\n")    
        # eliminiamo i doppioni in buckets_day_for_categories, per farlo prendo gli slot allocati dall'algoritmo e messi in buck buckets_day_for_categories
        # e per ogni coppia o tripla, cerco se ho già inserito in passato quella determinata coppia o tripla
        for c,cat in enumerate(buckets_day_for_categories):
            print(f"categoria {categories[c]}")
            ms = minimum_slot(categories[c])
            for j,giorni in enumerate(cat):
                # ripulisco pair_or_triples così non conterrà gli slot assegnati in altri giorni
                pair_or_triples = []
                # con questo for scorro in un particolare giorno (bucket) di una particolare categoria
                for z in range (0,len(giorni),ms):
                    
                    if  ms == 2:   # se la categoria ha alunni che fanno allenamento da un'ora
                        if z == 0: # caso in cui si parte dall'inizio (li devo mettere per forza)
                            # metto gli slot allocati in buckets_day_for_categories_real
                            buckets_day_for_categories_real[c][j].append(giorni[z])
                            buckets_day_for_categories_real[c][j].append(giorni[z + 1])
                            # metto in "saccoccia" gli slot appena trovati (a coppia), in modo che se ricompaiono nello stesso giorno non si vanno a rimetterli in buckets_day_for_categories_real
                            pair_or_triples.append(giorni[z])
                            pair_or_triples.append(giorni[z + 1])
                            continue
                        else: # dalla seconda iterazione in poi (z = 2)
                            temp1 = giorni[z]
                            temp2 = giorni[z + 1]
                            # controllo se temp1 e temp2 (due slot allocati) siano già stati presi
                            if check_already_in(temp1,temp2,0,pair_or_triples,ms) == True:
                                # se si vuol dire non li mettiamo in buckets_day_for_categories_real (perchè) non voglio doppioni
                               continue
                            else:
                                # se no significa che non sono ancora stati trovati/messi, quindi li mettiamo in buckets_day_for_categories_real
                                buckets_day_for_categories_real[c][j].append(giorni[z])
                                buckets_day_for_categories_real[c][j].append(giorni[z + 1])
                                # e metto in "saccoccia" questi slot appena trovati
                                pair_or_triples.append(giorni[z])
                                pair_or_triples.append(giorni[z + 1])

                    if ms == 3: # se la categoria ha alunni che fanno allenamento da un'ora e mezza
                        if z == 0: # caso in cui si parte dall'inizio (li devo mettere per forza)
                            # metto gli slot allocati in buckets_day_for_categories_real
                            buckets_day_for_categories_real[c][j].append(giorni[z])
                            buckets_day_for_categories_real[c][j].append(giorni[z + 1])
                            buckets_day_for_categories_real[c][j].append(giorni[z + 2])
                            # metto in "saccoccia" gli slot appena trovati (a tripla), in modo che se ricompaiono nello stesso giorno non si vanno a rimetterli in buckets_day_for_categories_real
                            pair_or_triples.append(giorni[z])
                            pair_or_triples.append(giorni[z + 1])
                            pair_or_triples.append(giorni[z + 2])
                            continue
                        else: # dalla seconda iterazione in poi (z = 3)
                            temp1 = giorni[z]
                            temp2 = giorni[z + 1]
                            temp3 = giorni[z + 2]
                            
                            if check_already_in(temp1,temp2,temp3,pair_or_triples,ms) == True:
                               # se si vuol dire non li mettiamo in buckets_day_for_categories_real (perchè) non voglio doppioni
                               continue
                            else:
                                # se no significa che non sono ancora stati trovati/messi, quindi li mettiamo in buckets_day_for_categories_real
                                buckets_day_for_categories_real[c][j].append(giorni[z])
                                buckets_day_for_categories_real[c][j].append(giorni[z + 1])
                                buckets_day_for_categories_real[c][j].append(giorni[z + 2])
                                # e metto in "saccoccia" questi slot appena trovati
                                pair_or_triples.append(giorni[z])
                                pair_or_triples.append(giorni[z + 1])
                                pair_or_triples.append(giorni[z + 2])

        print("\n")
        # stampo i bucket
        for c,cat in enumerate(buckets_day_for_categories_real):
            print(f"categoria {categories[c]}")
            for giorni in cat:
                print (giorni)
        print("\n")
        # inizializzazione problema finale
        final_problem = LpProblem("resfinale", sense=LpMinimize)
        # variabili decisionali dei slot per ogni giorno del calendario passato in input
        slots_variables = [
            [LpVariable(name=f"y{j+1},{k+1}", cat=LpBinary) for k in range(numeri_slot)]
                for j in range (6)
            ]
        # variabili decisionali per "decidere" quali slot assegnare a quale gruppo
        # in sostanza con questi riusciamo a capire quali gruppi sono stati assegnati agli slot
        # nel res finale
        x_variables = [LpVariable(name= f"x_{i+1}", cat=LpBinary) for i in range (1500)]
        # funzione obiettivo : minimizzare il numero di slot ovvero di ore utlizzate
        final_problem += lpDot(1,slots_variables)
        
        categorie_segnaposto = {}
        # mi prendo la prima categoria 
        solo = 0
        cont = 0
        for c,cat in enumerate(buckets_day_for_categories_real):
            print("#" * 30,f"categoria {categories[c]}", "#" * 30,)
            ms = minimum_slot(categories[c])
            # mi prendo i bucket (giorni) di una categoria
            for j,giorno in enumerate(cat):
                print("-" * 30,f"giorno {j + 1}","-" * 30)
                print(giorno)
                if len(giorno) == 0:
                    continue # potrebbe essere che in un giorno non c'e nessun studente, quindi si va al prossimo giorno

                # mi prendo gli slot di quel giorno
                for k in range(0,len(giorno),ms):
                    if ms == 2: # se siamo in una categoria in cui ci sono allievi che fanno allenamenti da un'ora (2 slot)
                        print(giorno[k], giorno[k + 1])
                        # presi i "campioni" ovvero gli slot, andiamo a vedere se c'e conflitto con altri slot nello stesso giorno nelle diverse categorie
                        collapse_slots = check_same_slots(giorno[k],giorno[k + 1],0,j,buckets_day_for_categories_real,categories,c,slots_variables)
                        print(collapse_slots)

                        # se non ci sono conflitti gli slot campioni ci saranno sicuramente alla fine
                        if checks_no_conflit(collapse_slots,categories) == True:
                            final_problem += lpDot(1,[receive_slots_decision_variables(slots_variables,j,giorno[k]),receive_slots_decision_variables(slots_variables,j,giorno[k + 1])]) == 2
                            categorie_segnaposto[f"solo {solo}"] = f"{categories[c]}"
                            solo += 1
                        # se no dobbiamo metterli in relazione con gli altri conflitti
                        else:
                            temp = []
                            final_problem += lpDot(1,[receive_slots_decision_variables(slots_variables,j,giorno[k]),receive_slots_decision_variables(slots_variables,j,giorno[k + 1])]) >= lpDot(2,x_variables[cont])
                            categorie_segnaposto[x_variables[cont].name] = f"{categories[c]}"
                            temp.append(x_variables[cont])
                            cont += 1
                            # i conflitti sono in collapse_slots e ci saranno conflitti per categoria (g) e tanti conflitti quanti ci sono in item
                            for g,group in enumerate(collapse_slots):
                                for item in group:
                                    print (item)
                                    if len(item) == 2:
                                        # significa che 2 slot vanno in conflitto con altri 3 slot
                                        final_problem += lpDot(1,item) >= lpDot(2,x_variables[cont])
                                        categorie_segnaposto[x_variables[cont].name] = f"{categories[g]}"
                                        temp.append(x_variables[cont])
                                        cont += 1
                                        
                                    if len(item) == 3:
                                        # significa che 2 slot vanno in conflitto con altri 3 slot
                                        final_problem += lpDot(1,item) >= lpDot(3,x_variables[cont])
                                        categorie_segnaposto[x_variables[cont].name] = f"{categories[g]}"
                                        temp.append(x_variables[cont])
                                        cont += 1
                                        
                            final_problem += lpDot(1,temp) >= 1

                    if ms == 3: # se siamo in una categoria in cui ci sono allievi che fanno allenamenti da un'ora e mezza
                        print(giorno[k], giorno[k + 1], giorno [k + 2])
                        collapse_slots = check_same_slots(giorno[k],giorno[k + 1],giorno[k + 2],j,buckets_day_for_categories_real,categories,c,slots_variables)
                        print(collapse_slots)

                        if checks_no_conflit(collapse_slots,categories) == True:
                            final_problem += lpDot(1,[receive_slots_decision_variables(slots_variables,j,giorno[k]),receive_slots_decision_variables(slots_variables,j,giorno[k + 1]),receive_slots_decision_variables(slots_variables,j,giorno[k + 2])]) == 3
                            categorie_segnaposto[f"solo {solo}"] = f"{categories[c]}"
                            solo += 1

                        else:
                            temp = []
                            final_problem += lpDot(1,[receive_slots_decision_variables(slots_variables,j,giorno[k]),receive_slots_decision_variables(slots_variables,j,giorno[k + 1]),receive_slots_decision_variables(slots_variables,j,giorno[k + 2])]) >= lpDot(3,x_variables[cont])
                            temp.append(x_variables[cont])
                            categorie_segnaposto[x_variables[cont].name] = f"{categories[c]}"
                            cont += 1
                            for g,group in enumerate(collapse_slots):
                                for item in group:
                                    print (item)
                                    if len(item) == 2:
                       
                                        final_problem += lpDot(1,item) >= lpDot(2,x_variables[cont])
                                        categorie_segnaposto[x_variables[cont].name] = f"{categories[g]}"
                                        temp.append(x_variables[cont])
                                        cont += 1

                                    if len(item) == 3:
                                        final_problem += lpDot(1,item) >= lpDot(3,x_variables[cont])
                                        categorie_segnaposto[x_variables[cont].name] = f"{categories[g]}"
                                        temp.append(x_variables[cont])
                                        cont += 1
                            # tutte le variabili decisionali x che saranno associate agli slot in conflitto 
                            # >= 1 così solo uno sopravviverà
                            final_problem += lpDot(1,temp) >= 1

            print("#" * 60)
            print('\n')

        #print(final_problem)
        solve = final_problem.solve(PULP_CBC_CMD(msg = False))
 
        for v in  final_problem.variables():
            print(v.name, "=", v.varValue)

        print ("valore ottimo degli slot minimi ", final_problem.objective.value())

        res = np.zeros((6,numeri_slot),dtype = int)

        for v in final_problem.variables():
            if "y" in v.name and v.varValue == 1:
                temp = (v.name).rsplit(",")
                #print(temp[0]+","+temp[1])
                res[int((temp[0])[1:]) - 1][int(temp[1]) - 1] = 1
    
        print(res)

        for key in categorie_segnaposto:
            print(key,categorie_segnaposto[key])

                
        return render_template("dashopti.html", user = current_user)
    else:
        return render_template("dashopti.html", user = current_user)

