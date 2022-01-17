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
let route;
let kinematicData;
let body = {};
let rowPosition;

function handleBurgermenu (e) {
	navbarMenu.classList.toggle('is-active');
	navbarBtn.classList.toggle('is-active');
}

function clickTable (event) {
    let row = event.composedPath()[1];
    rowPosition = row.rowIndex;
	//console.log(event.parent.target.parentElement);
	//alert(row.cells[0].innerHTML);
    tripIdTxt = document.getElementById('trip-id');
    tripTimeTxt = document.getElementById('trip-time');
    vehicleId = document.getElementById('vehicle-id');
    route = document.getElementById('route');
    
    tripIdTxt.textContent = row.cells[0].innerHTML;
    tripTimeTxt.textContent = row.cells[1].innerHTML;
    vehicleId.textContent = row.cells[2].innerHTML;
    route.textContent = row.cells[3].innerHTML;
    kinematicData = row.cells[4].innerHTML;
    modal.classList.toggle('is-active');
}

function showMessage(show){
    if (show)
        message.classList.remove('is-hidden');
    else
        message.classList.add('is-hidden');
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
    sendBtn.classList.add('is-loading');
    body.tripId = parseInt(tripIdTxt.textContent);
    body.date = tripTimeTxt.textContent;
    body.kinematicData = parseInt(kinematicData);
    body.vehicle = vehicleId.textContent;
    body.route = route.textContent;

    const data = await fetch('./trips', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    const response = await data.json();
    deleteRow(response.result);
    sendBtn.classList.remove('is-loading');
    exitModal();
}

async function deleteData() {
    deleteBtn.classList.add('is-loading');
    showMessage(false);
    const data = await fetch('./trips', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'text/plain'
        },
        body: parseInt(tripIdTxt.textContent)
    });
    const response = await data.json();
    deleteRow(response.result);
    deleteBtn.classList.remove('is-loading');
    exitModal();
}

function exitModal (event) {
    message.classList.add('is-hidden');
    modal.classList.toggle('is-active');
}

navbarBtn.addEventListener('click', handleBurgermenu, false);
table.addEventListener('click', clickTable, false);
sendBtn.addEventListener('click', sendData, false);
deleteBtn.addEventListener('click', (e)=>showMessage(true), false);
cancelDelBtn.addEventListener('click', (e)=>showMessage(false), false);
confirDelBtn.addEventListener('click', deleteData,false);
modalCloseBtn.addEventListener('click', exitModal, false);
modalBackground.addEventListener('click', exitModal, false);
