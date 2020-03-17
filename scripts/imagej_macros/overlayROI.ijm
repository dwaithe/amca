dir = "/Users/dominicwaithe/Desktop/erythroid/";
n=0;
count = 0;
list = getFileList(dir);
      for (i=0; i<list.length; i++) {
          if (endsWith(list[i], "all.tiff")){}
             
          else {
          	 if (endsWith(list[i], ".tiff")){
             showProgress(n++, count);
             path = dir+list[i];
             processFile(dir,list[i]);}
          }
      }
 function processFile(path,name) {
    
	win1 = name;
	print("win1",win1);
	win2 = replace(win1, ".tiff", "all.tiff");
	print("win2",win2);
	open(path+win1);
	open(path+win2);
	selectWindow(win1);
	run("Overlay Options...", "stroke=green width=1 fill=None set apply");
	selectWindow(win2);
	run("Overlay Options...", "stroke=red width=1 fill=None set apply");
	run("To ROI Manager");
	selectWindow(win1);
	run("From ROI Manager");
	run("Flatten");
	win3 = replace(win1, ".tiff", "");
	run("Enhance Contrast...", "saturated=0.9");
	saveAs("Jpeg", path+win3);
	run("Close All");
	}