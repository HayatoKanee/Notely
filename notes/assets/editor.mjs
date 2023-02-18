import {EditorView, basicSetup} from "codemirror"
import {javascript} from "@codemirror/lang-javascript"
import {indentWithTab,defaultKeymap} from "@codemirror/commands"
import {keymap} from "@codemirror/view"


function createEditor(doc, id){
    return new EditorView({
    extensions: [basicSetup,
       keymap.of([indentWithTab]),
      javascript()
    ],
        doc:doc,
    parent: document.querySelector(id)
  });
}
$("#showCodeEditor").click(function () {
  $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
});
export { createEditor }