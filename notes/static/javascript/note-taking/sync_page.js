const objectChangedCallback = function () {
    // send a message to the channel using websockets
    const message = {
        type: 'update_canvas',
        data: canvas.toDatalessJSON(['link'])
    };
    socket.send(JSON.stringify(message));
}

function set_send_message() {
    canvas.on('object:added', objectChangedCallback);
    canvas.on('object:modified', objectChangedCallback);
    canvas.on('object:removed', objectChangedCallback);
}
set_send_message();
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === "update_canvas") {
        canvas.off('object:added', objectChangedCallback);
        canvas.off('object:modified', objectChangedCallback);
        canvas.off('object:removed', objectChangedCallback);
        canvas.loadFromJSON(data.data, function () {
            canvas.getObjects().forEach(function (obj) {
                if (obj.link) {
                    obj.on('mousedown', function (e) {
                        if (currentMode == 'select') {
                            window.location.href = this.link;
                        }
                    });
                    obj.on('mouseover', function () {
                        obj.item(2).set({
                            visible: true
                        });
                        canvas.renderAll();
                    });

                    obj.on('mouseout', function () {
                        obj.item(2).set({
                            visible: false
                        });
                        canvas.renderAll();
                    });
                }
            });
            canvas.renderAll();
            set_send_message();
        });
    }
}
