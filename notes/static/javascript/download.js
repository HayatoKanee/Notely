$("#downloadAsPic").click(function(){
	$("#canvas").get(0).toBlob(function(blob){
		saveAs(blob, "notely_notebook.png");
	});
});