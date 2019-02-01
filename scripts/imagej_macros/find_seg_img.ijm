title = getTitle();
cnt = roiManager("count");
for(c=0;c<cnt;c++){
	selectWindow(title);
	roiManager("select", c);
	//run("Specify...", " oval");
	run("Level Sets", "method=[Active Contours] use_level_sets grey_value_threshold=3 distance_threshold=0.50 advection=1.50 propagation=1 curvature=1 grayscale=5 convergence=0.002 region=inside");
	run("Create Selection");
	run("Make Inverse");
	selectWindow("Segmentation of "+title);
	rename("before");
	selectWindow("Segmentation progress of "+title);
	close();
	//exit();
	//selectWindow(title);
	//run("Restore Selection");
	//run("Level Sets", "method=[Active Contours] use_level_sets grey_value_threshold=50 distance_threshold=0.50 advection=1.50 propagation=1 curvature=0.50 grayscale=20 convergence=0.0080 region=outside");
	
	//selectWindow("before");
	//close();
	
	//selectWindow("Segmentation progress of "+title);
	//close();
	}
run("Images to Stack", "name=Stack title=before use");
run("Z Project...", "projection=[Max Intensity]");
//run("Merge Channels...", "c1=MAX_Stack-1 c2=F01_120_GT_01-1 create keep");
selectWindow("MAX_Stack");
//close();
selectWindow("Stack");
close();