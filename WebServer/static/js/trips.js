const navbarMenu = document.getElementById("navbar");
const navbarBtn = document.getElementById("navbar-btn");
const table = document.getElementById('table');
const modal = document.getElementById('modal');
const message = document.getElementById('message');
const cancelDelBtn = document.getElementById('cancel-delete');
const confirDelBtn = document.getElementById('confirm-delete');
const sendBtn = document.getElementById('send');
const deleteBtn = document.getElementById('delete');
const modalCloseBtn = document. getElementsByClassName('modal-close')[0];
const modalBackground = document. getElementsByClassName('modal-background')[0];

let tripIdTxt;
let tripTimeTxt;
let vehicleId;
let kinematicData;
let body = {};
let rowPosition;

function handleBurgermenu (e) {
	navbarMenu.classList.toggle('is-active');
	navbarBtn.classList.toggle('is-active');
}

function clickTable (event) {
    let row = event.path[1];
    rowPosition = row.rowIndex;
	//console.log(event.parent.target.parentElement);
	//alert(row.cells[0].innerHTML);
    tripIdTxt = document.getElementById('trip-id');
    tripTimeTxt = document.getElementById('trip-time');
    vehicleId = document.getElementById('vehicle-id');
    tripIdTxt.textContent = row.cells[0].innerHTML;
    tripTimeTxt.textContent = row.cells[1].innerHTML;
    vehicleId.textContent = row.cells[2].innerHTML;
    kinematicData = row.cells[3].innerHTML;
    modal.classList.toggle('is-active');
}

function showMessage(){
    message.classList.toggle('is-hidden');
}

function deleteRow(cond){
    if (cond == true){
        table.deleteRow(rowPosition);
    }
    else{
        alert("Ocurrio un problema subiendo los datos, volver a intentar");
    }
}

async function sendData() {
    body.tripId = parseInt(tripIdTxt.textContent);
    body.date = tripTimeTxt.textContent;
    body.kinematicData = parseInt(kinematicData);
    body.vehicle = vehicleId.textContent;

    const data = await fetch('./trips', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    const response = await data.json();
    deleteRow(response.result);
}

async function deleteData() {
    const data = await fetch('./trips', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'text/plain'
        },
        body: parseInt(tripIdTxt.textContent)
    });
    const response = await data.json();
    deleteRow(response.result);
    showMessage();
}

function exitModal (event) {
    modal.classList.toggle('is-active');
}

navbarBtn.addEventListener('click', handleBurgermenu, false);
table.addEventListener('click', clickTable, false);
sendBtn.addEventListener('click', sendData, false);
deleteBtn.addEventListener('click', showMessage, false);
cancelDelBtn.addEventListener('click', showMessage,false);
confirDelBtn.addEventListener('click', deleteData,false);
modalCloseBtn.addEventListener('click', exitModal, false);
modalBackground.addEventListener('click', exitModal, false);