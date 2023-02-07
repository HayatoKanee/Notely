$("#showSymbols").click(function (){
     $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
});

$('.key').click(function (){
    canvas.add(new fabric.Text($(this).text()));
});
