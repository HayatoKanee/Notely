const symbol = document.getElementById("showSymbols");
symbol.disabled = true;
$("#showSymbols").click(function (){
     $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
});
canvas.on('selection:created', function (){
   if(canvas.getActiveObject().type !== 'activeSelection'){
       if(canvas.getActiveObject().get('type') == 'i-text'){
            symbol.disabled = false;
        }
   }
});
canvas.on('selection:updated', function (){
   if(canvas.getActiveObject().type !== 'activeSelection'){
       if(canvas.getActiveObject().get('type') == 'i-text'){
            symbol.disabled = false;
            return;
        }
   }
   symbol.disabled = true;
});

canvas.on('selection:cleared', function (){
    symbol.disabled = true;
});

$('.key').click(function (){
    let itext =  canvas.getActiveObject()
    itext.insertChars($(this).text(), [{fill: "green",
        fontStyle: "bold"}], itext.selectionStart);
    canvas.renderAll()
    
});

