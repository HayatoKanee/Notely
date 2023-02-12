const link = document.getElementById("linkPage");
link.disabled = true;
$('#linkPage').click(function (){
    let selection = canvas.getActiveObject();
     $('a').click(function (e){
         e.preventDefault();
         let tag = $(this);
        selection.on('selected', function (){
                window.location.replace(tag.attr('href'));
        });
         selection.set({
             fill:'blue',
             underline: true,
             link:tag.attr('href')
         });
         canvas.discardActiveObject();
         canvas.renderAll();
         $('#closeBtn').click();
    });
});
$('#sideBtn').click(function (){
    $("a").unbind("click");
});
canvas.on('selection:created', function (){
   if(canvas.getActiveObject().type !== 'activeSelection'){
       link.disabled = false;
   }

});

canvas.on('selection:cleared', function (){
    link.disabled = true;
});


