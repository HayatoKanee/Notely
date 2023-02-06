const initCanvas = (id) => {
    return new fabric.Canvas(id, {
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 'rgba(250,250,250,1)'
        });

}
const modes = ['select', 'draw', 'text'];
let currentMode;

function selectBtn(btn){
  modes.forEach(mode => {
    const b = document.getElementById(mode);
    b.classList.remove('active');
  });
  canvas.isDrawingMode= false;
  btn.classList.add('active');
}

function toggleText(btn) {
    selectBtn(btn);
    currentMode = "text";
}

function toggleDraw(btn) {
  selectBtn(btn);
  canvas.freeDrawingBrush.color = color
  canvas.isDrawingMode = true;
  currentMode = "draw";
}

function toggleSelect(btn) {
  selectBtn(btn);
  currentMode = "select";
}


function addImage(e) {
    const input = document.getElementById('img')
    const image = input.files[0];
    reader.readAsDataURL(image);
}

function chooseColor() {
    const chooser = document.getElementById('chooseColor')
    chooser.addEventListener('change', (e) => {
        color = '#' + e.target.value
        canvas.freeDrawingBrush.color = color
        canvas.requestRenderAll()
    })
}

const canvas = initCanvas('canvas');
canvas.loadFromJSON(drawing);
canvas.renderAll();

let color = '#000000'
chooseColor()

let reader = new FileReader()

let inputImage = document.getElementById('img');
inputImage.addEventListener('change', addImage);

reader.addEventListener("load", () => {
    fabric.Image.fromURL(reader.result, img => {
        canvas.add(img)
        canvas.requestRenderAll()
    })
});

canvas.on('mouse:down', function(options) {
    if(currentMode==='text'){
        let pointer = canvas.getPointer(options.e);
        if (!options.target) {
            let textbox = new fabric.IText('Input', {
          left: pointer.x,
          top: pointer.y,
          fontSize: 20,
          fontFamily: 'Arial',
          fill: color
        });
            canvas.add(textbox);
        }


    }
    canvas.renderAll();
});

window.setInterval(function (){
    $.ajax({
        type:"POST",
        url: "/save_page/"+page_id,
        data: {
            data: JSON.stringify(canvas.toDatalessJSON()),
            csrfmiddlewaretoken: csrf
        }
    });
}, 3000);
