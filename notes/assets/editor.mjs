import {EditorView, basicSetup} from "codemirror"
import {javascript} from "@codemirror/lang-javascript"
import {indentWithTab,defaultKeymap} from "@codemirror/commands"
import {keymap} from "@codemirror/view"
import { oneDark } from "@codemirror/theme-one-dark"

const editor = new EditorView({
  extensions: [basicSetup,
     keymap.of([indentWithTab]),
    javascript(),
      oneDark
  ],
  parent: document.querySelector('#code')
})

$("#showCodeEditor").click(function () {
  $(".modal-dialog").draggable({
    "handle": ".modal-header"
  });
});

function getContent(){
  console.log(editor.state.doc.toString());
  return editor.state.doc.toString();
}

function setContent(content){
  editor.dispatch({
    changes:{from:0, insert: content}
  });
}
export { getContent,setContent }