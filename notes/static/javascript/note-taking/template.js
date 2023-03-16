const addTemplate = document.getElementById("addTemplate");
addTemplate.disabled = true;

canvas.on('selection:created', function () {
    addTemplate.disabled = false;
});

canvas.on('selection:updated', function () {
    addTemplate.disabled = false;
});

canvas.on('selection:cleared', function () {
    addTemplate.disabled = true;
});

function createThumbnail(jsonData, thumbnailWidth, thumbnailHeight, callback) {
    const offScreenCanvas = new fabric.StaticCanvas();
    offScreenCanvas.setWidth(thumbnailWidth);
    offScreenCanvas.setHeight(thumbnailHeight);
    fabric.util.enlivenObjects(JSON.parse(jsonData), function (enlivenedObjects) {
        const group = new fabric.Group(enlivenedObjects);

        const scaleX = thumbnailWidth / group.width;
        const scaleY = thumbnailHeight / group.height;
        const scale = Math.min(scaleX, scaleY);

        group.set({
            scaleX: scale,
            scaleY: scale,
            left: 0,
            top: 0
        });
        offScreenCanvas.add(group);
        offScreenCanvas.renderAll();
        const thumbnailSrc = offScreenCanvas.toDataURL({format: 'png'});
        callback(thumbnailSrc);
    });
}

const thumbnailWidth = 200;
const thumbnailHeight = 100;

const templateItems = document.querySelectorAll('.template-item');
templateItems.forEach((templateItem) => {
    const jsonData = templateItem.getAttribute('data-content');

    createThumbnail(jsonData, thumbnailWidth, thumbnailHeight, (thumbnailSrc) => {
        templateItem.innerHTML = "<img src='" + thumbnailSrc + "' style='border: 1px solid black;'>";
    });
});

$('#addTemplate').click(function () {
    const selectedObjects = canvas.getActiveObjects();
    const jsonData = JSON.stringify(selectedObjects);

    $.ajax({
        url: template_url,
        type: 'POST',
        data: {
            template_content: jsonData,
            csrfmiddlewaretoken: csrf
        },
        success: function (data) {
            const template = $('<div></div>');
            template.attr("type", "button");
            template.addClass("col template-item");
            template.attr("data-content", jsonData);
            template.css("margin-top", "20px");
            createThumbnail(jsonData, thumbnailWidth, thumbnailHeight, (thumbnailSrc) => {
                template.html("<img src='" + thumbnailSrc + "' style='border: 1px solid black;'>");
            });
            $('#templateList').append(template);
            template.click(function () {
                loadTemplates($(this).data('content'));
            });
        },
        error: function (error) {
            alert('Error saving template');
        }
    });
});

$('.template-item').click(function () {
    loadTemplates($(this).data('content'));
});

function loadTemplates(content) {
    fabric.util.enlivenObjects(content, function (enlivenedObjects) {
        const group = new fabric.Group(enlivenedObjects);
        canvas.add(group);
        canvas.renderAll();
    });
}