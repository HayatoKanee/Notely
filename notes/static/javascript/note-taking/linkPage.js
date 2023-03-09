const link = document.getElementById("linkPage");
link.disabled = true;
$('#linkPage').click(function () {
    const selection = canvas.getActiveObject();
    $('a').click(function (e) {
        e.preventDefault();
        const tag = $(this);
        const underline = new fabric.Path('M' + selection.left + ',' + (selection.top + selection.height) + ' L' + (selection.left + selection.width) + ',' + (selection.top + selection.height));
        underline.set({
            stroke: 'blue',
            strokeWidth: 1,
            selectable: false
        });
        const text = new fabric.Text('page ' + tag.attr('data-page-num'), {
            left: selection.left + selection.width + 10,
            top: selection.top,
            fontFamily: 'Arial',
            fontSize: 12,
            fill: 'black',
            visible: false
        });
        canvas.remove(selection);

        const obj = new fabric.Group([selection, underline, text]);
        obj.on('mousedown', function (e) {
            if (currentMode === 'select') {
                window.location.replace(tag.attr('href'));
            }
        });
        obj.set({
            link: tag.attr('href')
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
        canvas.add(obj);
        canvas.discardActiveObject();
        canvas.renderAll();
        $('#closeBtn').click();
    });
});
$('#sideBtn').click(function () {
    $("a").unbind("click");
});
canvas.on('selection:created', function () {
    if (canvas.getActiveObject().type !== 'activeSelection') {
        link.disabled = false;
    }

});

canvas.on('selection:cleared', function () {
    link.disabled = true;
});


