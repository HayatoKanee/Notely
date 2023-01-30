const initCanvas = (id) => {
    return new fabric.Canvas(id, {
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 'rgba(250,250,250,1)'
    });
}
const modes = ['select', 'draw', 'add_text'];


function selectBtn(btn){
  modes.forEach(mode => {
    const b = document.getElementById(mode);
    b.classList.remove('active');
  });
  btn.classList.add('active');
}

function toggleText(btn) {
    selectBtn(btn);
    canvas.isDrawingMode= false;
}

function toggleDraw(btn) {
  selectBtn(btn);
  canvas.isDrawingMode = true;
}

function toggleSelect(btn) {
  selectBtn(btn);
  canvas.isDrawingMode = false;
}


function addImage(e) {
    const input = document.getElementById('img')
    const image = input.files[0];
    reader.readAsDataURL(image)
}

const canvas = initCanvas('canvas');

let reader = new FileReader()

let inputImage = document.getElementById('img');
inputImage.addEventListener('change', addImage)

reader.addEventListener("load", () => {
    fabric.Image.fromURL(reader.result, img => {
        canvas.add(img)
        canvas.requestRenderAll()
    })
})


