const table = document.getElementById('table');
const modal = document.getElementById('modal');
const sendBtn = document.getElementById('send');
const cancelBtn = document.getElementById('cancel');
const modalCloseBtn = document. getElementsByClassName('modal-close')[0];
const modalBackground = document. getElementsByClassName('modal-background')[0];

let tripIdTxt;

function clickTable (event) {
    let row = event.path[1];
	//console.log(event.parent.target.parentElement);
	//alert(row.cells[0].innerHTML);
    tripIdTxt = document.getElementById('trip-id');
    let tripTimeTxt = document.getElementById('trip-time');
    tripIdTxt.textContent = row.cells[0].innerHTML
    tripTimeTxt.textContent = row.cells[1].innerHTML
    modal.classList.toggle('is-active');
}

async function sendData (event) {
    let tripId = parseInt(tripIdTxt.textContent)
    console.log(tripId)
    // TODO: Send data to backend and firebase
    /*const data = await fetch('./trips', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    const response = await data.json();
    console.log(response);*/
}


function exitModal (event) {
    modal.classList.toggle('is-active');
}

table.addEventListener('click', clickTable, false);
sendBtn.addEventListener('click', sendData, false);
cancelBtn.addEventListener('click', exitModal, false);
modalCloseBtn.addEventListener('click', exitModal, false);
modalBackground.addEventListener('click', exitModal, false);
