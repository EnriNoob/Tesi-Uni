var day = document.getElementById("giorno")
var month = document.getElementById("mese")
var year = document.getElementById("anno")
const giorni_nei_mesi = [31,28,31,30,31,30,31,31,30,31,30,31]

month.addEventListener("input", function(){
    var mese = month.value
    console.log(mese);
    var giorni_nel_mese = giorni_nei_mesi[mese - 1]

    for (let i = 1; i <= 31; i++) {
        document.getElementById("d" + i).disabled = false
        if (i>=giorni_nel_mese + 1) {
                document.getElementById("d" + i).disabled = true
        }
    }
    if (mese == 2)
        if(parseInt(year.value) % 400 == 0 || (parseInt(year.value) % 4 == 0 && parseInt(year.value) % 100 != 0))
            document.getElementById("d29").disabled = false 
})

year.addEventListener("input", function(){
    var anno = year.value
    let mese = month.value
    console.log(mese);
    if (mese == 2) {
        if (anno % 400 == 0 || (anno %4 == 0 && anno % 100 != 0) ) {
            document.getElementById("d29").disabled = false
        }
        else{
        document.getElementById("d29").disabled = true
        }
    }
})

function uncheck_other_checkboxes(input){
    var calendarsLength = (document.getElementsByClassName("checkbox-calendar")).length
    document.getElementById("tr" + input.name).style.backgroundColor = "red"
    for (var i = 1 ;  i <= calendarsLength ; i++){
        if (parseInt(input.name) != i){
            document.getElementById(i).checked = false
            document.getElementById("tr" + i).style.backgroundColor = "white"
        }      
    }
    insert_availability(input, "tr" + input.name)
}

function insert_availability(input,trname){
    rows = document.getElementById("table-calendars").rows;
    var right_row = rows[trname]

    const giorni = ["H","L","M","M","G","V","S"]
    var div = document.getElementById("insert-availability")
    
    var idCalendar = (right_row.cells[1]).innerHTML
    var oraInizio  = (right_row.cells[2]).innerHTML
    var oraFine = (right_row.cells[3]).innerHTML 
    var slot = (right_row.cells[4]).innerHTML
    var slotE = (right_row.cells[5]).innerHTML
    var slotEliminatiArray = slotE.split(",")
    slotEliminatiArray.splice((slotEliminatiArray.length) - 1,1)
    console.log(slotEliminatiArray);

    var splitInizioOra = oraInizio.split(":")
    var splitFineOra =  oraFine.split(":")

    
    var startOre = parseInt(splitInizioOra[0],10)
    var startMinuti = parseInt(splitInizioOra[1],10)
    
    var endOre = parseInt(splitFineOra[0],10)
    var endMinuti = parseInt(splitFineOra[1],10)

    var secondi_giorno = (endOre * 3600 + endMinuti *60) - (startOre * 3600 + startMinuti * 60)

    var data = new Date(2024,1,1,startOre,startMinuti,0,0)


    div.innerHTML= " ";
    
    var divisionSlot = (secondi_giorno) / (slot * 60)
    var table = document.createElement("table");
    
    for (let  i= 0;  i < divisionSlot + 1; i++){
        const trow = table.insertRow();
        for (let j = 0; j < 7; j++) {
            // alla prima riga metto i caratteri dei giorni che sono in giorni[j]
            if (i == 0) {
                const tdata = trow.insertCell()
                tdata.appendChild(document.createTextNode(giorni[j]))
                
            } 
            // in tutte le altre righe metto gli orari e i checkbox
            else {
                // nella prima colonna metto gli orari slottati bene
                if (j == 0){
                    // per evitare di aggiunger 0 al 30 
                    if(data.getMinutes() == 30){
                        stringa = + data.getHours() + ":" + data.getMinutes()
                    }
                    // per aggiungere 0 ad esempio (9:0)
                    else{
                        stringa = + data.getHours() + ":" + data.getMinutes() + "0"
                    }
                    // se passiamo all'ora successiva (9:30 + 0:30)
                    if (data.getMinutes() + slot == 60){
                        data.setHours(data.getHours() + 1)
                        data.setMinutes(0)
                        stringa += " - " + data.getHours() + ":" + data.getMinutes() + "0"
                    }
                    // aggiungiamo i successivi 30 minuti di uno slot che parte alle x:00 (9:00 - 9:30)
                    else{
                        data.setMinutes(data.getMinutes() + 30)
                        stringa += " - " + data.getHours() + ":" + data.getMinutes()
                    }
                    
                    const t_data_hour = trow.insertCell()
                    label = document.createElement("label")
                    label.innerHTML = "" + stringa
                    t_data_hour.appendChild(label)
                }
                // nelle altre colonne metto i checkbox
                else {
                    const tdata = trow.insertCell()
                    input = document.createElement("input")
                    input.setAttribute("type","checkbox")
                    // devo fare (i - 1) perchè la riga 0 è occupata dalle iniziali dei giorni
                    // devo fare (j - 1) perchè la colonna 0 è occupata dagli orari degli slot
                    //input.setAttribute("value", (i - 1) +"-" + (j -1))
                    input.setAttribute("name", "check")
                    input.setAttribute("id", (j - 1) +"-" + (i -1))
                    input.setAttribute("value", (j - 1) +"-" + (i -1))
                    tdata.appendChild(input)
                    tdata.style.border = '1px solid black'
                    tdata.style.margin= "10px 0px 10px 0px"
                }     
            }
        }
    }
    div.appendChild(table)
    document.getElementById("idcalendar").value = idCalendar
    
    console.log("lunghezza ",slotEliminatiArray.length);
    for (let i = 0; i < slotEliminatiArray.length; i++) {
        document.getElementById(slotEliminatiArray[i]).disabled = true
    }
    //console.log(idCalendar.innerHTML)
    //console.log(oraInizio.innerHTML);
    //console.log(oraFine.innerHTML);
    //console.log(slot.innerHTML);
  
    /*
    for (let i = 2; i < 6; i++) {
        cell = right_row.cells[i];
        console.log(i + " -> " + cell.innerHTML);   
    }
    */
}