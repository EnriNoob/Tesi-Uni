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

    const oraMezzogiorno = 12 * 3600
    const oraInizioPomeriggio = 14 * 3600

    var mattina = oraMezzogiorno - (startOre * 3600 + startMinuti * 60)
    var pomeriggio = (endOre * 3600 + endMinuti *60) - oraInizioPomeriggio

    console.log("secondi dall'ora scelta fino alle 12", mattina);
    console.log("secondi dell'ora di fine", pomeriggio);
    
    //controlliamo se gli orari messi dell'utente riescono ad essere divisibili senza resto dai minuti dagli slot inseriti
    if ((mattina % (slot * 60)) != 0 || (pomeriggio % (slot * 60)) != 0 ) {
        console.log("zioboia non si può slottare");
        alert("Ciao hai messo gli slot con minutaggio spastico!!");
    }
    else{
        div.innerHTML = ""
        console.log("si può slottare");
        document.getElementById("bottone").innerHTML = "Rigenera calendario"
        var divisionSlot = ((mattina) + (pomeriggio)) / (slot * 60)
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
                        // quando ore arriva a 12 lo devo far saltare a 14
                        if(startOre == 12){
                            startOre= 14
                        }
                        // per aggiungere uno zero ai minuti quando si arriva al 00:59 
                        if(startMinuti == 0){
                            var stringa = startOre + ":" + startMinuti + "0"
                        }
                        else{
                            var stringa = startOre + ":" + startMinuti
                        }
                        startMinuti += slot
                        if(startMinuti == 60){
                            startOre += 1
                            startMinuti = 0 
                            stringa +=  "-" + startOre + ":" + startMinuti + "0"
                        }
                        else if(startMinuti >= 90){
                            if((startMinuti - 90) == 30){
                                startOre += 2
                                startMinuti = 0
                                stringa +=  "-" + startOre + ":" + startMinuti + "0"
                            }
                            else{
                                startOre += 1
                                startMinuti = 30
                             stringa +=  "-" + startOre + ":" + startMinuti
                            }
                            
                        }else{
                            stringa += "-" + startOre + ":" + startMinuti
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
                        tdata.appendChild(input)
                        tdata.style.border = '1px solid black'
                        tdata.style.margin= "10px 0px 10px 0px"
                    }     
                }
            }
        }
        formSubmit = document.createElement("input")
        formSubmit.setAttribute("type", "submit")
        formSubmit.style.display= "center"
        div.appendChild(table)
        div.appendChild(formSubmit)
    }   
}
/*
function clearDiv(elementID){
    elementID.innerHTML = ""
}
*/
