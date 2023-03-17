const objectChangedCallback = function () {
    // send a message to the channel using websockets
    const message = {
        type: 'update_canvas',
        data: canvas.toDatalessJSON(['link', 'is_table'])
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
                if (obj.is_table) {
                    obj.on('mousedblclick', function (option) {
                        const pointer = canvas.getPointer(option.e);
                        const normalized_pointer = canvas._normalizePointer(obj, pointer)
                        console.log(normalized_pointer)
                        let target;
                        obj.forEachObject(function (o) {
                            if (canvas._checkTarget(normalized_pointer, o)) {
                                target = o;
                            }
                        });
                        canvas.setActiveObject(target.item(1));
                        target.item(1).enterEditing();
                    });
                }
            });
            canvas.renderAll();
            set_send_message();
        });
    }
}
