$("#downloadAsPic").click(function () {
    $("#canvas").get(0).toBlob(function (blob) {
        saveAs(blob, "notely_notebook.png");
    });
});
$("#downloadAsPdf").click(function () {
    // const imgData = canvas.toDataURL("image/jpeg");

    $("#canvas").get(0).toBlob(function (blob) {
        const url = window.URL || window.webkitURL;
        const img = new Image();
        const imgSrc = url.createObjectURL(blob);
        img.src = imgSrc;

        img.onload = function () {
            const pdf = new jsPDF('l', 'px', [img.width, img.height]);
            pdf.addImage(img, 0, 0, img.width, img.height);
            pdf.save('download.pdf');
        }
    });
});