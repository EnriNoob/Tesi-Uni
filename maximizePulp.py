import openpyxl
import numpy as np
from pulp import *
# dizionario in cui si assegna uno slot ad un numero
# ogni slot dura da x fino a x + 01:00
slots_1hour_dict ={ #slot da un'ora
    "09:00" : 0,
    "10:00" : 1,
    "11:00" : 2,
    "14:00" : 3,
    "15:00" : 4,
    "16:00" : 5,
    "17:00" : 6,
    "18:00" : 7,
    "19:00" : 8,
}
slots_130_hour_dict = { # slot da un'ora e mezza
    "09:00" : 0,
    "10:30" : 1,
    "14:00" : 2,
    "15:30" : 3,
    "17:00" : 4,
    "18:30" : 5,
}
slots_half_hour = { # tutti slot da un'ora
    "09:00" : 0,
    "09:30" : 1,
    "10:00" : 2,
    "10:30" : 3,
    "11:00" : 4,
    "11:30" : 5,
    "12:00" : 6,
    "14:00" : 7,
    "14:30" : 8,
    "15:00" : 9,
    "15:30" : 10,
    "16:00" : 11,
    "16:30" : 12,
    "17:00" : 13,
    "17:30" : 14,
    "18:00" : 15,
    "18:30" : 16,
    "19:00" : 17,
    "19:30" : 18,
    "20:00" : 19,
}
# stampa un array a 3 dimensioni, typeslot mi serve soltanto per capire lo studente esatto nel foglio excel
def print_3d_array(array,typeslot):
    cont = 0
    for s,i in enumerate(typeslot):
        if i == 1:
            print (f"studente {s+1}")
            print(array[cont,:,:])
            cont += 1
            print("-------------------------")

# stampa la comparazione tra la gli array a 3 dimensioni di allievo e campo (o di 60 o di 90, dipende da cosa si è passato in typeslot) 
# stamperà per ogni studente il numero massimo di allenamenti, la sua matrice di disponibilità e la matrice con gli allenamenti effettivamente assegnati
def print_comparison_3d_array(array1,array2,trainings,typeslot):
    cont = 0
    for s,i in enumerate(typeslot):
        if i == 1:
            print (f"studente {s+1} può fare al massimo {trainings[cont]} allenamenti\n")
            for j in range(6):
                print(array1[cont,j,:],array2[cont,j,:])
            cont += 1
            print("\n")
# ci ritorna la variabile decisionale richiesta nella lista a 3 dimensioni delle variabili decisionali
def receive_decision_variables(array,student,day,slot):
    for s,i in enumerate(array):
        if s == student: # ci prendiamo quel particolare studente
            for d,j in enumerate(i):    
                if d == day:    # ci prendiamo quel particolare giorno
                    #print(j[slot])
                    return j[slot]  # ci prendiamo la variabile decisionale di quel particolare slot (x_i,j,k)

# assegnamo alla matrice allievo di un particolare slot (60 o 90) le disponibilità degli studenti
def assigning_allievo(array, dict, x,i,j,typeslot): 
    if(x == "no" or x == None): # case "no" or None in excel cell
            array[i,j,:] = 0
            return
            
    elif("poi" in x): # case "da x in poi"
        slot = x[3:8]
        array[i,j,dict[slot]:] = 1
    
    elif(x == "tutto il pome"): # case "tutto il pome"
        if typeslot == 90:
            array[i,j,dict["14:00"]:dict["17:00"]] = 1
        else :
            array[i,j,dict["14:00"]:dict["18:00"]] = 1
            
    elif("giorno" in x): # case "tutto il giorno"
        array[i,j,:] = 1
        
    elif("dopo" in x): # case "da x o dopo y"
        firstHour = x[3:8]
        secondHour = x[16:21]
        array[i,j,dict[firstHour]:] = 1
    
    else: #case "da x a y"
        firstHour = x[3:8]
        secondHour = x[11:16]
        if typeslot == 90:
            if secondHour == "12:00":
                array[i,j, dict[firstHour] : dict["10:30"] + 1] = 1
                
            elif secondHour == "20:00":
                array[i,j, dict[firstHour] : dict["18:30"] + 1] = 1
                
            else: 
                array[i,j,dict[firstHour] : dict[secondHour]] = 1
            
        else:
            if secondHour == "12:00":
                array[i,j, dict[firstHour] : dict["11:00"] + 1] = 1
                
            elif secondHour == "20:00":
                array[i,j, dict[firstHour] : dict["19:00"] + 1] = 1
                
            else: 
                array[i,j,dict[firstHour] : dict[secondHour]] = 1

def check_dissatisfied(array, slots, nstudents, ntraining, decision_variables):
    
    for i in range(nstudents):
        sum = 0
        ones =[]
        saves =[]
        for j in range(6):
            for k in range(slots):
                if array[i,j,k] == 1:
                    saves.append(receive_decision_variables(decision_variables,i,j,k))
                    sum += array[i,j,k]
    
        if sum != ntraining[i]:
            array[i,:,:] = 0
            print(saves)
            
        
# per aprire il workbook 
workBook = openpyxl.load_workbook("vincoli2.xlsx")   # Workbook oggetto
third_sheet = workBook.sheetnames[2]
#second_sheet = workBook.sheetnames[1]               # prendiamo il nome del foglio desiderato del file excel
active_worksheet = workBook[third_sheet]             # impostiamo il foglio corrente come attivo

number_students_total = active_worksheet.max_row - 2 # numero totale degli studenti
contentRow = []

number_students1 = 0    # numero degli studenti che fanno allenamenti da un'ora
number_students130 = 0  # numero degli studenti che fanno allenamenti da un'ora e mezza
ninety = []             # raccoglie la posizione esatta degli studenti con allenamenti da un'ora del foglio excel
sixty = []              # raccoglie la posizione esatta degli studenti con allenamenti da un'ora e mezza del foglio excel

# recuperare i dati dal foglio excel
for i,row in enumerate (active_worksheet.iter_rows(min_row=3, max_col=active_worksheet.max_column, max_row=active_worksheet.max_row)):
    for cell in row:
        contentRow.append(cell.value) # una riga completa
    if contentRow[3] == 90:
        number_students130 += 1
        ninety.append(1)
        sixty.append(0)
    else: # 60
        number_students1 += 1
        sixty.append(1)
        ninety.append(0)

    contentRow.clear()

#print(f"studenti che fanno allenamento da un ora {number_students1}",sixty)    
#print(f"studenti che fanno allenamento da un ora e mezza {number_students130}",ninety)
number_training1 = np.zeros(number_students1,dtype = int)
number_training130 = np.zeros(number_students130,dtype = int)


# creazione degli array a 3 dimensioni dove 
# ogni posizione è 1 se uno certo studente i è disponibile
# di fare allenamento per quel giorno e per quel slot
# 0 altrimenti
Allievo1 = np.zeros((number_students1,6,9),dtype = int)
Allievo130 = np.zeros((number_students130,6,6),dtype = int)
# array a 3 dimensioni che verranno popolate dalla funzione obiettivo
Campo1 = np.zeros((number_students_total,6,9),dtype = int)
Campo130 = np.zeros((number_students_total,6,6),dtype = int)
#Slots = np.zeros((6,9), dtype = int)

cont1 = 0
cont130 = 0
switch = True
# assegnamo agli array 3d allievo1 e 130 le diponibilità
for i,row in enumerate (active_worksheet.iter_rows(min_row=3, max_col=active_worksheet.max_column, max_row=active_worksheet.max_row)):
    # adding to contentRow all the values of the tuple that we get with iter_rows
    for cell in row:
        contentRow.append(cell.value)

    # prendere il numero di allenemanti massimi di ogni studente
    if "1" in contentRow[2] or "2" in contentRow[2] or "3" in contentRow[2] or "4" in contentRow[2]:
        string = contentRow[2]
        if contentRow[3] == 90:
                number_training130[cont130] = int(string[0:1])     
        else:
                number_training1[cont1] = int(string[0:1])
    # lettura degli slot 
    for j,x in enumerate(contentRow[4:10]):
        if contentRow[3] == 90:
            assigning_allievo(Allievo130,slots_130_hour_dict,x,cont130,j,90)
            switch= True
        else:
            assigning_allievo(Allievo1,slots_1hour_dict,x,cont1,j,60)
            switch = False

    if(switch):
        cont130 +=1
    else :
        cont1 += 1

    contentRow.clear()
#print_3d_array(Allievo1,number_training1)
#print_3d_array(Allievo130,number_training130)
#print(number_training1)
#print(number_training130)

# creazioni dei problemi di programmazione intera
problem1 = LpProblem("Maximize_student_1", sense=LpMaximize)
problem130 = LpProblem("Maximize_student_130", sense=LpMaximize)
i = 0
j = 0 
# variabili decisionali, x per quelli da un'ora e y per quelli da un'ora e mezza
students_variables1 =[
    [   
    [LpVariable(name=f"x_{i+1},{j+1},{k+1}", cat=LpBinary) for k in range(9)]
        for j in range(6)
    ] for i in range(number_students1)
]
students_variables130 =[
    [   
    [LpVariable(name=f"y_{i+1},{j+1},{k+1}", cat=LpBinary) for k in range(6)]
        for j in range(6)
    ] for i in range(number_students130)
]
# funzioni obiettivo da massimizzare
problem1 += lpDot(1,students_variables1)
problem130 += lpDot(1,students_variables130)

#---------------------------vincoli------------------------
# 2) vincolo // ogni studente si allena al massimo una volta al giorno
# per farlo dobbiamo controllare l'array 3d allievo e vedere quale studente per un certo giorno per un certo slot è libero (1, o altrimenti)
# una volta capito se è libero dobbiamo prendere la variabile decisionale corrispondente (di quello studente per quel certo giorno per quel certo slot) 
# e mettere tutte le variabili decisionali di uno studente di un giorno (o più) in una espressione lineare e controllare che sia <=1
# 1) vincolo // aggiunto se no uno studente non ha disponibilità per un certo giorno per uno certo slot la variabile decisionale corrispondente è uguale a 0
# i = studente, j = giorno, k = slot
students_one = []
students_zero = []
for s,i in enumerate(Allievo1):
    #print(f"studente = {s+ 1}")
    for d,j in enumerate(i):        
        for o,k in enumerate(j):
            if k == 0:
                students_zero.append(receive_decision_variables(students_variables1,s,d,o))
            else: # k == 1
                students_one.append(receive_decision_variables(students_variables1,s,d,o))

        #print(students_one)
        if not(len(students_zero) == 0):
            problem1 += lpSum(1 * students_zero) == 0
        
        if not(len(students_one) == 0):
            problem1 += lpSum(1 * students_one) <= 1
        
        students_one.clear()
        students_zero.clear()
# vincolo 3 // per ogni slot ci devono essere al massimo 4 allievi

for day in range(6):
    for slot in range(9):
        for student in range(number_students1):
            if(Allievo1[student,day,slot] == 1):
                students_one.append(receive_decision_variables(students_variables1,student,day,slot))
        if not(len(students_one) == 0):
            problem1 += lpSum(1 * students_one) <= 4
            students_one.clear()
    
# vincolo 4 // uno studente si allena al massimo il numero di allenamenti da lui dichiarato
for s,i in enumerate(Allievo1):
    #print(f"studente = {s+ 1}")
    for d,j in enumerate(i):        
        for o,k in enumerate(j):
            if k == 1:
                students_one.append(receive_decision_variables(students_variables1,s,d,o)) 

    problem1 += lpSum(1 * students_one) <= number_training1[s]
    students_one.clear()

# stessa cosa ma per gli studenti da un'ora e mezza
students_one = []
students_zero = []
for s,i in enumerate(Allievo130):
    #print(f"studente = {s+ 1}")
    for d,j in enumerate(i):        
        for o,k in enumerate(j):
            if k == 0:
                students_zero.append(receive_decision_variables(students_variables130,s,d,o))
            else: # k == 1
                students_one.append(receive_decision_variables(students_variables130,s,d,o))

        #print(students_one)
        if not(len(students_zero) == 0):
            problem130 += lpSum(1 * students_zero) == 0
        
        if not(len(students_one) == 0):
            problem130 += lpSum(1 * students_one) <= 1
        
        students_one.clear()
        students_zero.clear()

for day in range(6):
    for slot in range(6):
        for student in range(number_students130):
            if(Allievo130[student,day,slot] == 1):
                students_one.append(receive_decision_variables(students_variables130,student,day,slot))
        if not(len(students_one) == 0):
            problem130 += lpSum(1 * students_one) <= 4
            students_one.clear()
    

for s,i in enumerate(Allievo130):
    #print(f"studente = {s+ 1}")
    for d,j in enumerate(i):        
        for o,k in enumerate(j):
            if k == 1:
                students_one.append(receive_decision_variables(students_variables130,s,d,o)) 

    problem130 += lpSum(1 * students_one) <= number_training130[s]
    students_one.clear()

# risoluzione dei problemi
status1 = problem1.solve(PULP_CBC_CMD(msg = False))
status130 = problem130.solve(PULP_CBC_CMD(msg = False))

# riempire la matrice campo (il risultato con le variabili decisionali scelte)
# 60
for v in problem1.variables():
    
    if v.varValue == 1.0:
        if v.name[3] != ',': # x_32,4,9
            Campo1[int(v.name[2:4]) - 1,int(v.name[5:6]) - 1,int(v.name[-1]) - 1] = 1
        else:                # x_1,2,3
            Campo1[int(v.name[2:3]) - 1,int(v.name[4:5]) - 1,int(v.name[-1]) - 1] = 1
# 90
for v in problem130.variables():
    print(v)
    if v.varValue == 1.0:
        if v.name[3] != ',': # x_32,4,9
            Campo130[int(v.name[2:4]) - 1,int(v.name[5:6]) - 1,int(v.name[-1]) - 1] = 1
        else:                # x_1,2,3
            Campo130[int(v.name[2:3]) - 1,int(v.name[4:5]) - 1,int(v.name[-1]) - 1] = 1
'''
# per controllare se la matrice campo rispetta il vincolo 3
test = []
for day in range(6):
    for slot in range(5):
        cont = 0
        for student in range(number_students130):
            if(Campo130[student,day,slot] == 1):
                students_one.append(Campo130[student,day,slot])
                test.append(receive_decision_variables(students_variables130,student,day,slot))
                cont += 1
        
        if(len(test) != 0):
            print(test)
            pass
        students_one.clear()
        test.clear()
        if cont > 4 or len(students_one) > 4:
            print(f"c'è uno slot in cui ci sono 5 o più studenti nel giorno{day + 1} e slot{slot + 1}")
'''
#print_comparison_3d_array(Allievo,Campo,numberOfStudents)
#print_3d_array(Campo130,ninety)
#print_3d_array(Campo1,sixty)
#print(problem1)
#print(problem130)
s1 = number_students1 / 4
s15 = number_students130 / 4

check_dissatisfied(Campo1, 9, number_students1, number_training1, students_variables1) 
check_dissatisfied(Campo130, 6, number_students130, number_training130, students_variables130)

print_comparison_3d_array(Allievo1,Campo1,number_training1,sixty)
print_comparison_3d_array(Allievo130,Campo130,number_training130,ninety)

print ("valore ottimo per gli studenti da un'ora= ", problem1.objective.value())
print ("valore ottimo per gli studenti da un'ora e mezza = ", problem130.objective.value())

print(s1,s15)

final_problem = LpProblem("resfinale", sense=LpMaximize)