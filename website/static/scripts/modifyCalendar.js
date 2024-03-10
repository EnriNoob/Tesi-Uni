function generateCalendar(input){
    document.getElementById("calendar").style.visibility = "hidden"
    var chosen_id = input.getAttribute("id");
    var checkboxes = document.getElementsByClassName("checkbox-calendar")
    var tr
    for (let i = 0; i < checkboxes.length; i++) {
        if ((checkboxes[i].getAttribute("id")) == chosen_id) {
            document.getElementById(checkboxes[i].getAttribute("id")).checked = true
            //document.getElementById("tr" + checkboxes[i].getAttribute("id")).style.backgroundColor = "red"
            tr = document.getElementById("tr" + checkboxes[i].getAttribute("id"))
        } else {
            document.getElementById(checkboxes[i].getAttribute("id")).checked = false           
        }
    }
    
    insert_availability(tr.getAttribute("id"))
}

function insert_availability(trname){
    
    document.getElementById("form-main").style.visibility = "visible"
    rows = document.getElementById("table-calendars").rows
    right_row = rows[trname]
    console.log(right_row);
    

    const giorni = ["H","L","M","M","G","V","S"]
    var div = document.getElementById("calendar")
    
    var idCalendar = (right_row.cells[1]).innerHTML
    var oraInizio  = (right_row.cells[2]).innerHTML
    var oraFine = (right_row.cells[3]).innerHTML 
    var slot = (right_row.cells[4]).innerHTML
    var slotE = (right_row.cells[5]).innerHTML
    console.log(slotE);

    document.getElementById("tiposlot").value = slot
    
    if (slotE == '') {
        slotEliminatiArray = []
    }else{
        var slotEliminatiArray = slotE.split(",")
    }

    
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
    div.appendChild(table)
    
    if (slot == 60) {
        document.getElementById("90").disabled = true
        document.getElementById("60").disabled = false 
        
    } else {
        document.getElementById("60").disabled = true
        document.getElementById("90").disabled = false
        
    }
    document.getElementById("orainizio").setAttribute("value",oraInizio)
    document.getElementById("orafine").setAttribute("value",oraFine)
    document.getElementById("textid").innerText = idCalendar
    document.getElementById("textid").setAttribute("value", idCalendar)
    
    
    formSubmit = document.createElement("input")
    formSubmit.setAttribute("type", "submit")
    formSubmit.setAttribute("value", "modifica")
    formSubmit.style.display= "center"
    text = document.createElement("p")
    text.innerHTML = "puoi eliminare degli slot"
    text.style.color = "red"
    text.style.float = "center"
    div.appendChild(text)
    div.appendChild(table)
    div.appendChild(formSubmit)

}

function regenerateCalendar(){
    document.getElementById("calendar").style.visibility = "visible"
    } 

