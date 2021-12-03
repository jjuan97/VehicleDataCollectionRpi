const navbarMenu = document.getElementById("navbar");
const navbarBtn = document.getElementById("navbar-btn");
const recordingBtn = document.getElementById('recording-btn');
const inputs = document.querySelectorAll('input');

let recording = false;
let badInputs = false;
let body = {};

const validations = {
	'number': (value) => {
		if (Number(value) > 0 ){
			body.freq = Number(value);
			return true;
		}
		else
			return false;
	},
	'text': (value) => {
		if (value !== "" ){
			body.idVehicle = value;
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
		let isOk = validations[input.type](input.value);
		validationResults.push( isOk );
		if (isOk)
			document.getElementById(input.dataset.errorMsg).classList.add('is-hidden')
		else
			document.getElementById(input.dataset.errorMsg).classList.remove('is-hidden')
	});
	return validationResults.includes(false);
}

function disableInputs (state) {
	const inputs = document.querySelectorAll('input');
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
	body.recording = state;
	const data = await fetch('./recordingTask', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(body)
	});
	const response = await data.json();
	console.log(response);
}

navbarBtn.addEventListener('click', handleBurgermenu, false);
recordingBtn.addEventListener('click', startStopRecording, false);
