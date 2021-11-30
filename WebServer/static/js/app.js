const navbarMenu = document.getElementById("navbar");
const navbarBtn = document.getElementById("navbar-btn");
const recordingBtn = document.getElementById('recording-btn');

let recording = false;

function handleBurgermenu (e) {
  navbarMenu.classList.toggle('is-active');
  navbarBtn.classList.toggle('is-active')
}

function startStopRecording (e) {
  // WS communication
  recording = !recording;
  if (recording) {
    recordingBtn.classList.remove('is-primary');
    recordingBtn.classList.add('is-danger');
    recordingBtn.textContent = "Stop"
  }
  else {
    recordingBtn.classList.add('is-primary');
    recordingBtn.classList.remove('is-danger');
    recordingBtn.textContent = "Start"
  }

}

navbarBtn.addEventListener('click', handleBurgermenu, false);
recordingBtn.addEventListener('click', startStopRecording, false);
