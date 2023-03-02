
  const objectChangedCallback = function (){
      // send a message to the channel using websockets
      const message = {
        type: 'update_canvas',
        data: canvas.toDatalessJSON(['link'])
      };
      socket.send(JSON.stringify(message));
  }
  canvas.on('object:added', objectChangedCallback);
      canvas.on('object:modified', objectChangedCallback);
      canvas.on('object:removed', objectChangedCallback);
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === "update_canvas") {
            canvas.off();
            canvas.loadFromJSON(data.data, function(){
                canvas.getObjects().forEach(function(obj) {
                if (obj.link) {
                  obj.on('mousedown', function(e) {
                      if(currentMode=='select') {
                          window.location.href = this.link;
                      }
                  });
                }
              });
                canvas.renderAll();
                canvas.on('object:added', objectChangedCallback);
      canvas.on('object:modified', objectChangedCallback);
      canvas.on('object:removed', objectChangedCallback);
            });
        }
    }