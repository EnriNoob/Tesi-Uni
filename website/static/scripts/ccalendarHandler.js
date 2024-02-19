function generateCalendar(){
    var inizioOra = document.getElementById("orainizio").value
    var div = document.getElementById("calendar")
    var fineOra = document.getElementById("orafine").value
    var slot = parseInt(document.getElementById("tiposlot").value)
    const giorni = ["L","M","M","G","V","S"]

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

    if ((mattina % (slot * 60)) != 0 || (pomeriggio % (slot * 60)) != 0 ) {
        console.log("zioboia non si può slottare");
        alert("Ciao hai messo gli slot con minutaggio spastico!!");
    }
    else{
        console.log("si può slottare");
        document.getElementById("button-calendar").style.display = "none"
        var divisionSlot = ((mattina) + (pomeriggio)) / (slot * 60)
        var table = document.createElement("table");
    
        for (let  i= 0;  i < divisionSlot + 1; i++){
            const trow = table.insertRow();
            for (let j = 0; j < 6; j++) {
                if (i == 0) {
                    const tdata = trow.insertCell()
                    giorno = document.createTextNode(giorni[j])
                    tdata.appendChild(giorno)
                } else {
                    const tdata = trow.insertCell()
                    input = document.createElement("input")
                    input.setAttribute("type","checkbox")
                    tdata.appendChild(input)
                    tdata.style.border = '1px solid black'
                    tdata.style.margin= "10px 0px 10px 0px"    
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