function close_popup(){
    document.getElementById("popup-content").style.visibility = "hidden"
    document.getElementsByTagName("body")[0].style.overflow = "auto"
    
}
function generate_popup(checkbox_input){
    document.getElementsByTagName("body")[0].style.overflow = "hidden"
    console.log(checkbox_input);
    id = checkbox_input.getAttribute("id");
    document.getElementById("popup-content").style.visibility = "visible"

    rows = document.getElementById("table-students").rows
    //right_row = row["tr" + id]
    right_row = rows["tr" + id]
    console.log(right_row);
    
    var idstu = (right_row.cells[1]).innerText
    var nome = (right_row.cells[2]).innerText
    var cognome = (right_row.cells[3]).innerText
    var gnascita = (right_row.cells[4]).innerText
    var mnascita = (right_row.cells[5]).innerText
    var anascita = (right_row.cells[6]).innerText
    var genere = (right_row.cells[7]).innerText
    var livello = (right_row.cells[8]).innerText
    var numeroallenamenti = (right_row.cells[9]).innerText
    var slotdisponibilita = (right_row.cells[10]).innerText
    var idcal = (right_row.cells[11]).innerText

    document.getElementById("idallievo").setAttribute("value",idstu)
    document.getElementById("nome").setAttribute("value",nome)
    document.getElementById("cognome").setAttribute("value",cognome)
    document.getElementById("giorno").setAttribute("value",gnascita)
    document.getElementById("mese").setAttribute("value",mnascita)
    document.getElementById("anno").setAttribute("value",anascita)
    document.getElementById("genere").setAttribute("value",genere)
    document.getElementById("allenamenti").setAttribute("value",numeroallenamenti)
    document.getElementById("allenamenti").value = numeroallenamenti
    document.getElementById("livello").value = livello
    document.getElementById("slotdisponibilita").setAttribute("value",slotdisponibilita)
    
    uncheck_others_tr(id)
    put_slots(idcal)

}

function uncheck_others_tr(id) {
    
    checkboxes_list = document.getElementsByClassName("checkbox-calendar")
    //console.log(checkboxes_list);
    //console.log(typeof(checkboxes_list));
    Array.from(checkboxes_list).forEach(function (element) {
        console.log(element)
        if (element.getAttribute("id") != id){
            element.checked = false
        }
        else{
            element.checked = true
        }
    });
  
    /*
    tr_list.forEach(element => {
        console.log(element);
        
        if (element.getAttribute("id") != trname){
            element.checkecd = false
        }
        else{
            element.checkecd = true
        }
        
    });
    */
    
}

function put_slots(idcal){
    rows = document.getElementById("table-calendars").rows
    right_row = rows["tr" + idcal]
    console.log(right_row);
    

    const giorni = ["H","L","M","M","G","V","S"]
    var div = document.getElementById("calendar")
    
    var idCalendar = (right_row.cells[1]).innerHTML
    var oraInizio  = (right_row.cells[2]).innerHTML
    var oraFine = (right_row.cells[3]).innerHTML 
    var slot = (right_row.cells[4]).innerHTML
    var slotE = (right_row.cells[5]).innerHTML
    

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
    submit = document.createElement("input")
    submit.setAttribute("type","submit")
    submit.setAttribute("id","submit")
    div.appendChild(submit)

    console.log(slotEliminatiArray.length);
    if (slotEliminatiArray.length > 0){
        for (let i = 0; i < slotEliminatiArray.length; i++) {
            document.getElementById(slotEliminatiArray[i]).disabled = true
        }
    } 

}

