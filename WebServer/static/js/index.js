const navbarMenu = document.getElementById("navbar");
const navbarBtn = document.getElementById("navbar-btn");
const recordingBtn = document.getElementById('recording-btn');
const inputs = [
	...document.querySelectorAll('input'), 
	...document.querySelectorAll('select')
];

let recording = false;
let badInputs = false;
let requestBody = {};

const validations = {
	'frequency': (input) => {
		let value = input.value;
		if (Number(value) > 0 ){
			requestBody.freq = Number(value);
			return true;
		}
		else
			return false;
	},
	'vehicle': (select) => {
		let index = select.selectedIndex;
		if (Number(index) != 0){
			requestBody.idVehicle = select.value;
			return true;
		}
		else
			return false;
	},
	'route': (select) => {
		let index = select.selectedIndex;
		if (Number(index) != 0){
			requestBody.route = select.value;
			return true;
		}
		else
			return false;
	}
}

function handleBurgermenu (e) {
	navbarMenu.classList.toggle('is-active');
	navbarBtn.classList.toggle('is-active');
}

function validateInputs(){
	let validationResults = [];
	
	inputs.forEach(input => {
		let isOk = validations[input.name](input);
		validationResults.push( isOk );
		if (isOk)
			document.getElementById(input.dataset.errorMsg).classList.add('is-hidden')
		else
			document.getElementById(input.dataset.errorMsg).classList.remove('is-hidden')
	});
	return validationResults.includes(false);
}

function disableInputs (state) {
	inputs.forEach(i => {
		i.disabled = state;
	});
}

function startStopRecording (e) {
	let badInputs = validateInputs();

	if (!badInputs) {
		recording = !recording;
		if (recording) {
			sendRequest(true);
			recordingBtn.classList.remove('is-primary');
			recordingBtn.classList.add('is-danger');
			recordingBtn.textContent = "Stop";
			disableInputs(true);
		}
		else {  
			sendRequest(false);
			recordingBtn.classList.add('is-primary');
			recordingBtn.classList.remove('is-danger');
			recordingBtn.textContent = "Start";
			disableInputs(false);
		}
	}
}

async function sendRequest(state){
	requestBody.recording = state;
	const data = await fetch('./recordingTask', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(requestBody)
	});
	const response = await data.json();
	console.log(response);
}

navbarBtn.addEventListener('click', handleBurgermenu, false);
recordingBtn.addEventListener('click', startStopRecording, false);
