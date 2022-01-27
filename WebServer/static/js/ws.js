window.addEventListener('load', ()=>{
  const moduleNames = ['acc-data', 'gyr-data', 'mag-data', 'gps-data', 'obd-data'];

  const socket = io();

  socket.on('connect', () => {
    console.log('WS connected: ' + socket.id);
    socket.emit('vehicleDataConnect', {data: 'I\'m connected!'});
  });
  
  socket.on('vehicleDataConnect', (data)=> {
    console.log(data);
    let json = JSON.parse(data);
    console.log('WS Server says: ', json);
  });

  socket.on('vehicleData', (data)=> {
    //console.log(data);
    let json = JSON.parse(data);
    //console.log('WS Server says: ', json);
    
    for (let name of moduleNames) {
      let card = document.getElementById(name);
      let fields = card.querySelectorAll('.level-right');
      fields.forEach( (field) => {
        field.textContent = json[field.dataset.key].toString();
      });
    }
    
  });

});
