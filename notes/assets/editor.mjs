import {EditorView, basicSetup} from "codemirror"
import { python } from '@codemirror/lang-python';
import { html } from '@codemirror/lang-html';
import {indentWithTab} from "@codemirror/commands"
import {keymap} from "@codemirror/view"
import { Compartment} from '@codemirror/state';

let language = new Compartment

function createEditor(doc, id){
    const languageModes = [python(), html()];
    let x = 0;
    const changeMode = (target) =>{
        x%=languageModes.length;
       target.dispatch({
               effects: language.reconfigure(languageModes[x])
           })
        $("#lang").text(languageModes[x]);
    }
    return new EditorView({
    extensions: [basicSetup,
       keymap.of([indentWithTab,{
           key: 'Ctrl-e',
           run: (target) =>{
               x++;
               changeMode(target);
           }
       }]),
      language.of(python())
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