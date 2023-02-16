
const initCanvas = (id) => {
    return new fabric.Canvas(id, {
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: 'rgba(250,250,250,1)'
        });

}

function clearCanvas(canvas) {
    canvas.getObjects().forEach((obj) => {
        if(obj !== canvas.backgroundImage) {
            canvas.remove(obj)
        }
    })
}

function undo(btn){
    selectBtn(btn);
    if(canvas._objects.length>0){
        canvasObj.push(canvas._objects.pop());
     canvas.renderAll();
    }
}
  
function redo(btn){ 
    selectBtn(btn);
    if(canvasObj.length>0){
      _redo = true;
     canvas.add(canvasObj.pop());
    }
}

const modes = ['select', 'draw', 'text', 'erase'];
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
  canvas.freeDrawingBrush = new fabric.PencilBrush(canvas);
  canvas.freeDrawingBrush.color = penColor
  canvas.isDrawingMode = true;
  currentMode = "draw";
}

function toggleSelect(btn) {
  selectBtn(btn);
  currentMode = "select";
}

function toggleErase(btn){
    selectBtn(btn);
    currentMode = "erase";
    canvas.freeDrawingBrush = new fabric.EraserBrush(canvas);
    canvas.freeDrawingBrush.width = 10;
    canvas.isDrawingMode = true;
}

function addImage(e) {
    const input = document.getElementById('img')
    const image = input.files[0];
    reader.readAsDataURL(image);
}

function choosePenColor() {
    const chooser = document.getElementById('choosePenColor')
    chooser.addEventListener('change', (e) => {
        penColor = '#' + e.target.value
        canvas.freeDrawingBrush.color = penColor
        canvas.requestRenderAll()
    })
}


function chooseWidth() {
    const slider = document.getElementById('chooseWidth')
    slider.addEventListener('change', (e) => {
        width = e.target.value
        canvas.freeDrawingBrush.width = width
        canvas.requestRenderAll()
    })
}

function chooseTextColor() {
    const chooser = document.getElementById('chooseTextColor')
    chooser.addEventListener('change', (e) => {
        textColor = '#' + e.target.value
        canvas.freeDrawingBrush.color = textColor
        canvas.requestRenderAll()
    })
}

// reference: https://github.com/av01d/fabric-brushes
function chooseMode() {
    const chooser = document.getElementById('chooseMode')
    chooser.addEventListener('change', (e) => {
        mode = e.target.value
        if (mode=="crayon"){
            canvas.freeDrawingBrush = new fabric.CrayonBrush(canvas,
                {
                    width: 30, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 0.6 // Opacity of brush
                });
        } else if (mode=="fur"){
            canvas.freeDrawingBrush = new fabric.FurBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="ink"){
            canvas.freeDrawingBrush = new fabric.InkBrush(canvas,
                {
                    width: 30, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="longfur"){
            canvas.freeDrawingBrush = new fabric.LongfurBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="circle"){
            canvas.freeDrawingBrush = new fabric.CircleBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="marker"){
            canvas.freeDrawingBrush = new fabric.MarkerBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="ribbon"){
            canvas.freeDrawingBrush = new fabric.RibbonBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="shaded"){
            canvas.freeDrawingBrush = new fabric.ShadedBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush,
                    shadeDistance: 1000, // Shade distance
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="sketchy"){
            canvas.freeDrawingBrush = new fabric.SketchyBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="spraypaint"){
            canvas.freeDrawingBrush = new fabric.SpraypaintBrush(canvas,
                {
                    width: 30, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="square"){
            canvas.freeDrawingBrush = new fabric.SquaresBrush(canvas,
                {
                    width: 1, // Stroke width of squares
                    color: '#000', // Stroke color of squares
                    bgColor: '#fff', // Background color of squares
                    opacity: 1 // Opacity of brush
                });
        }
        else if (mode=="web"){
            canvas.freeDrawingBrush = new fabric.WebBrush(canvas,
                {
                    width: 1, // Width of brush
                    color: '#000', // Color of brush
                    opacity: 1 // Opacity of brush
                });
        }
        canvas.requestRenderAll()
    })
}

const canvas = initCanvas('canvas');
canvas.loadFromJSON(drawing, function(){
    canvas.getObjects().forEach(function(obj) {
    if (obj.link) {
      obj.on('mousedown', function(e) {
          if(currentMode=='select') {
              window.location.href = this.link;
          }
      });
    }
  });
    canvas.renderAll();
});

let penColor = '#000000'
let textColor = '#000000'
choosePenColor()
chooseTextColor()



let width = '30'
chooseWidth()

chooseMode()

  
let _redo = false;
let canvasObj = [];

let reader = new FileReader()

let inputImage = document.getElementById('img');
inputImage.addEventListener('change', addImage);

reader.addEventListener("load", () => {
    fabric.Image.fromURL(reader.result, img => {
        canvas.add(img)
        canvas.requestRenderAll()
    })
});

canvas.on('object:added',function(){
    if(!_redo){
        canvasObj = [];
    }
    _redo = false;
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
          fill: textColor
        });
            canvas.add(textbox);
        }


    }
    canvas.renderAll();
});

document.onkeydown = function (e){
    if(e.keyCode == 46){
        const selection = canvas.getActiveObject();
        if (selection.type === 'activeSelection') {
            selection.forEachObject(function(element) {
                canvas.remove(element);
            });
        }
        else{
            canvas.remove(selection);
        }
        canvas.discardActiveObject();
    }
}
function save(sync){
    $.ajax({
        type:"POST",
        async:sync,
        url: "/save_page/"+page_id,
        data: {
            data: JSON.stringify(canvas.toJSON(['link'])),
            code: cm6.getContent(),
            csrfmiddlewaretoken: csrf
        }
    });
}
window.setInterval(function (){
    save(false);
}, 50000);

window.onbeforeunload= function(event) {
     save(true);
     return "";
  };
