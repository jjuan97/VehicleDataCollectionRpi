const IP = '10.0.0.22';
const WSPORT = 5555;

window.addEventListener('load', ()=>{

  const socket = io();

  socket.on('connect', () => {
    console.log('WS connected: ' + socket.id);
    socket.emit('vehicleData', {data: 'I\'m connected!'});
  });

  socket.on('vehicleData', (data)=> {
    console.log(data);
    let json = JSON.parse(data);
    console.log('WS Server says: ', json);
  });

});