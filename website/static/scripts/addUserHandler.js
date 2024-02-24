document.getElementById("agonistico").addEventListener("click",untoggle_dilettante)
document.getElementById("dilettante").addEventListener("click",untoggle_agonistico)

function untoggle_dilettante(){
    document.getElementById("agonistico").checked = true 
    document.getElementById("dilettante").checked = false
}

function untoggle_agonistico(){
    document.getElementById("dilettante").checked = true
    document.getElementById("agonistico").checked = false
}