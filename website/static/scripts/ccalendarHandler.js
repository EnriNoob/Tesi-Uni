function generateCalendar(){
    var inizioOra = document.getElementById("orainizio").value
    var div = document.getElementById("calendar")
    var fineOra = document.getElementById("orafine").value
    var slot = parseInt(document.getElementById("tiposlot").value)
    const giorni = ["H","L","M","M","G","V","S"]

    var splitInizioOra = inizioOra.split(":")
    var splitFineOra =  fineOra.split(":")

    var startOre = parseInt(splitInizioOra[0],10)
    var startMinuti = parseInt(splitInizioOra[1],10)
    
    var endOre = parseInt(splitFineOra[0],10)
    var endMinuti = parseInt(splitFineOra[1],10)

    console.log(startOre,startMinuti);
    console.log(endOre,endMinuti);
    
    const inizio = startOre * 3600 + startMinuti * 60
    const fine = endOre * 3600 + endMinuti * 60

    if (inizio > fine) {
        alert("hai inserito l'orario di fine giornata maggiore di quello di inizio giornata")
        return;
    } 
    var secondi_giorno = (endOre * 3600 + endMinuti *60) - (startOre * 3600 + startMinuti * 60)

    console.log("secondi durate il giorno ", secondi_giorno);
    console.log("ore durante la giornata", secondi_giorno / 3600);
    
    var data = new Date(2024,1,1,startOre,startMinuti,0,0)
    console.log(data);
    console.log(data.getHours() + ":" + data.getMinutes());

    //controlliamo se gli orari messi dell'utente riescono ad essere divisibili senza resto dai minuti dagli slot inseriti
    if ((secondi_giorno % (slot * 60)) != 0) {
        console.log("non si può slottare");
        alert("Ciao hai messo gli slot con minutaggio spastico!!");
    }
    else{
        div.innerHTML = ""
        console.log("si può slottare");
        document.getElementById("bottone").innerHTML = "Rigenera calendario"
        var divisionSlot = (secondi_giorno) / (slot * 60)
        var table = document.createElement("table");
    
        for (let  i= 0;  i < divisionSlot + 1; i++){
            const trow = table.insertRow();
            for (let j = 0; j < 7; j++) {
                // alla prima riga metto i caratteri dei giorni che sono in giorni[j]
                if (i == 0) {
                    const tdata = trow.insertCell()
                    tdata.appendChild(document.createTextNode(giorni[j]))
                    tdata.setAttribute("id","tdata")
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
                        input.setAttribute("value", (i - 1) +"-" + (j -1))
                        tdata.appendChild(input)
                        tdata.style.border = '1px solid black'
                        tdata.style.margin= "10px 0px 10px 0px"
                    }     
                }
            }
        }
        formSubmit = document.createElement("input")
        formSubmit.setAttribute("type", "submit")
        formSubmit.setAttribute("onclick","checkSingleSlot()")
        formSubmit.style.display= "center"
        div.appendChild(table)
        div.appendChild(formSubmit)
    } 
}
function checkSingleSlot(){
    console.log("fgjnihwghiwe");
}
