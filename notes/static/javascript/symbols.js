$("#showSymbols").click(function (){
     $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
});

$('.key').click(function (){
    t = new fabric.Text($(this).text());
    t.set({
        left: canvas.width/2,
        top: canvas.height/2
    })
    

    console.log("Text", canvas.getActiveObject().get('type'))

    if(canvas.getActiveObject().get('type') == 'i-text'){
      var itext =  canvas.getActiveObject()
      console.log("test123", itext)
      // .get('text');
      itext.insertChars($(this).text(), [{ fill: "green", fontStyle: "bold" }], 6,7);
    }

    canvas.add(itext);
    
});

