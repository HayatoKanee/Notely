$("#showCodeEditor").click(function () {
  $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
});

CodeMirror.fromTextArea(document.getElementById("code"), {
    lineNumbers: true,
    mode: "python"
  });