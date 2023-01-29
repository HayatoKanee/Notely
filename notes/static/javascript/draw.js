const initCanvas = (id) => {
    return new fabric.Canvas(id, {
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 'rgba(250,250,250,1)'
    });
}
const modes = ['select', 'draw'];

function selectBtn(btn){
  modes.forEach(mode => {
    const b = document.getElementById(mode);
    b.classList.remove('active');
  });
  btn.classList.add('active');
}

function toggleDraw(btn) {
  selectBtn(btn);
  canvas.isDrawingMode = true;
}

function toggleSelect(btn) {
  selectBtn(btn);
  canvas.isDrawingMode = false;
}

const canvas = initCanvas('canvas');
