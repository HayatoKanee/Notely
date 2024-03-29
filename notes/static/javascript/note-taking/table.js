function insertTable(rows, columns) {
    var cellWidth = 100;
    var cellHeight = 50;

    var cells = [];

    for (var r = 0; r < rows; r++) {
        for (var c = 0; c < columns; c++) {
            var rect = new fabric.Rect({
                left: c * cellWidth,
                top: r * cellHeight,
                fill: null,
                width: cellWidth,
                height: cellHeight,
                stroke: 'black',
                strokeWidth: 1
            });

            var text = new fabric.IText("", {
                left: c * cellWidth + 5,
                top: r * cellHeight + 5,
                width: cellWidth - 10,
                height: cellHeight - 10,
                fontSize: 16,
                editable: true,
                selectable: true,
                evented: true,
                pointerEvents: 'auto',
            });

            var group = new fabric.Group([rect, text], {
                left: c * cellWidth,
                top: r * cellHeight,
            });

            cells.push(group);
        }
    }

    var table = new fabric.Group(cells, {
        left: 100,
        top: 100,
        width: columns * cellWidth,
        height: rows * cellHeight,
        is_table: true
    });
    table.on('mousedblclick', function (option) {
        const pointer = canvas.getPointer(option.e);
        const normalized_pointer = canvas._normalizePointer(obj, pointer)
        let target;
        table.forEachObject(function (o) {
            if (canvas._checkTarget(normalized_pointer, o)) {
                target = o;
            }
        });
        canvas.setActiveObject(target.item(1));
        target.item(1).enterEditing();

        // console.log(target.item(1).hiddenTextarea)
    });
    canvas.add(table);

    text.bringToFront();

}

var modal = document.getElementById("tableModal");
var btn = document.getElementById("table");
var span = document.getElementsByClassName("close")[0];
var submitBtn = document.getElementById("submitTable");


btn.onclick = function () {
    modal.style.display = "block";
}

span.onclick = function () {
    modal.style.display = "none";
}

submitBtn.onclick = function () {
    var rows = document.getElementById("rows").value;
    var columns = document.getElementById("columns").value;

    insertTable(rows, columns);
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}