
for(file=32;file<97;file++){
roiManager("reset");
newImage("image", "8-bit black", 532, 532, 1);
run("Bio-Formats Importer", "open=/Users/dwaithe/Desktop/C127_DAPI/1086"+file+".jpg.ome.tif autoscale color_mode=Default display_rois rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");

roiCount = roiManager("count");
for(i=0;i<roiCount;i++){
	
	selectWindow("image");
	roiManager("select", i);
	run("Enlarge...", "enlarge=1");
	run("Colors...", "foreground=white background=black selection=cyan");
	run("Fill");
	run("Colors...", "foreground=black background=white selection=cyan");
	run("Draw");
	}
saveAs("Jpeg", "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/Faster-RCNN-TensorFlow-Python3.5/data/c127_dapi_class/2018/seg_outputs/1086"+file+".jpg");
run("Close All");
}