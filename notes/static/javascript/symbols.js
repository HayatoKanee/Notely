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
    canvas.add(t);
});
