var day = document.getElementById("giorno")
var month = document.getElementById("mese")
var year = document.getElementById("anno")
var livello = document.getElementById("livello")

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

livello.addEventListener("input", function(){
    document.getElementById("insert-availability").style.visibility = "visible"
    liv = document.getElementById("livello").value
    var slot = 0
    console.log(liv);
    if (liv == "I love tennis" || liv == "sat under 8" || liv == "sat under 10" || liv == "sat under 12" || liv == "sat under 14" || liv == "sat under 16" || liv == "sat under 18"){
        slot = 60
    }
    else{
        slot = 90
    }

    document.getElementById("calendar-list").style.display = "flex"

    var checkSlots = document.getElementsByClassName("check-slot")
    var input

    console.log();

    for (let i = 0; i < checkSlots.length; i++) {
        document.getElementById("tr" + (checkSlots[i].getAttribute("name")).slice(-1)).style.backgroundColor = "white"
        document.getElementById((checkSlots[i].getAttribute("name")).slice(-1)).disabled = false
        document.getElementById((checkSlots[i].getAttribute("name")).slice(-1)).checked = false 
   
    }
   
    for (let i = 0; i < checkSlots.length; i++) {
        
        if (checkSlots[i].innerText != slot){
            document.getElementById((checkSlots[i].getAttribute("name")).slice(-1)).disabled = true
        }
        else{
            document.getElementById((checkSlots[i].getAttribute("name")).slice(-1)).disabled = false
            document.getElementById("tr" + (checkSlots[i].getAttribute("name")).slice(-1)).style.backgroundColor = "red"
            document.getElementById((checkSlots[i].getAttribute("name")).slice(-1)).checked = true
            input = document.getElementById("tr"  + (checkSlots[i].getAttribute("name")).slice(-1))
        }  
    }
    
    insert_availability(input.getAttribute("name"))

})


function insert_availability(trname){
    document.getElementById("submit").style.visibility = "visible"
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
    console.log(slotEliminatiArray);

    var splitInizioOra = oraInizio.split(":")
    var splitFineOra =  oraFine.split(":")

    
    var startOre = parseInt(splitInizioOra[0],10)
    var startMinuti = parseInt(splitInizioOra[1],10)
    
    var endOre = parseInt(splitFineOra[0],10)
    var endMinuti = parseInt(splitFineOra[1],10)

    var secondi_giorno = (endOre * 3600 + endMinuti *60) - (startOre * 3600 + startMinuti * 60)

    var oggi = new Date(2024,1,1,startOre,startMinuti,0,0)


    div.innerHTML= " ";
    
    var divisionSlot = (secondi_giorno) / (slot * 60)

    tempoDaAggiungere = (slot * 60) * 1000
    var stringa = ""
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
                   
                    stringa = oggi.toLocaleTimeString().slice(0,5);
                    console.log(stringa);
                    console.log(oggi.getMinutes());
                    //console.log(stringa);
                    oggi.setTime(oggi.getTime() + tempoDaAggiungere)
                    
                    stringa += " - " + oggi.toLocaleTimeString().slice(0,5);
                    console.log(stringa);

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
    text = document.createElement("p")
    text.innerHTML = "aggiungi le tue disponibilità"
    text.style.color = "red"
    text.style.float = "center"
    div.appendChild(text)
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