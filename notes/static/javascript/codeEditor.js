const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    lineNumbers: true,
    mode: "python",
  });
$("#showCodeEditor").click(function () {
  $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
  editor.refresh()
});
