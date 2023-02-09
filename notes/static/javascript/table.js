
function insertTable(rows, columns) {
    var cellWidth = 100;
    var cellHeight = 50;
    
    var cells = [];
  
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < columns; c++) {
        var rect = new fabric.Rect({
          left: c * cellWidth,
          top: r * cellHeight,
          fill: 'white',
          width: cellWidth,
          height: cellHeight,
          stroke: 'black',
          strokeWidth: 1
        });
        
        var text = new fabric.IText("test", {
          left: c * cellWidth + 5,
          top: r * cellHeight + 5,
          width: cellWidth - 10,
          height: cellHeight - 10,
          fontSize: 16,
          editable: true,
          selectable:true,
          evented: true,
          pointerEvents: 'auto',
        });
        
        var group = new fabric.Group([rect, text], {
          left: c * cellWidth,
          top: r * cellHeight,
        });
  
        cells.push(group);
      }
    }
  
    var table = new fabric.Group(cells, {
      left: 100,
      top: 100,
      width: columns * cellWidth,
      height: rows * cellHeight,
    });

    canvas.add(table);

    text.bringToFront();

  }

var modal = document.getElementById("myModal");
var btn = document.getElementById("table");
var span = document.getElementsByClassName("close")[0];
var submitBtn = document.getElementById("submit-button");



btn.onclick = function() {
  modal.style.display = "block";
}

span.onclick = function() {
  modal.style.display = "none";
}

submitBtn.onclick = function() {
  var rows = document.getElementById("rows").value;
  var columns = document.getElementById("columns").value;
  
  insertTable(rows, columns);
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}