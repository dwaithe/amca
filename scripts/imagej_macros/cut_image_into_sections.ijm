////////////////
//Script for taking an image with ROI and cutting it up into segments.
//This works well with a large image which has been fully labelled and needs
//to be divided into smaller sections.
//--------inputs:
//An image (large) labelled with regions added to the ROI Manager.
//--------outputs:
//several images of width and height (size)
//
//by Dominic waithe (c).
///////////////

size = 125//size of segments
path = "/Users/dominicwaithe/Documents/collaborators/WaitheD/micro_vision/acquisitions/20200413_10x/small/"



function crop(a0,a1,a2,a3,title,window){
setBatchMode(true);
count = roiManager("count");
for(i=0;i<count;i++){
	selectWindow(title);
	roiManager("select",i);
	getSelectionBounds(x, y, width, height);
	selectWindow(window);
	if ((x >a0 || x +width >a0) && (y> a1 || y+height > a1) && x < a0+a2 && y < a1+a3){
	b0 = x-a0; b1 = y-a1;  b2 =width; b3 = height;
	if (b0<0) b0 = 0;
	if (b1<0) b1 = 0;
	if (b0+width >size) b2 = b0+width-size+1;
	if (b1+height >size) b3 = b1+height-size+1;

    makeRectangle(b0, b1, b2, b3);
    run("Add Selection...");
    
	print(x,y,width,height);
	
	}}
run("Select None");
setBatchMode(false);}

title = getTitle();
ext_pos = lengthOf(title)
subTitle = substring(title, 0,ext_pos-4);


selectWindow(title);
a0 = 0;a1 = 0; a2 = size; a3 = size;
makeRectangle(a0,a1,a2,a3);
run("Duplicate...", "title="+subTitle+"a");
crop(a0,a1,a2,a3,title,subTitle+"a");
//run("Size...", "width=500 height=500 depth=1 constrain average interpolation=Bilinear");
saveAs("TIFF", path+subTitle+"_a.tif");

selectWindow(title);
a0 = 0;a1 = size; a2 = size; a3 = size;
makeRectangle(a0,a1,a2,a3);
run("Duplicate...", "title="+subTitle+"b");
crop(a0,a1,a2,a3,title,subTitle+"b");
//run("Size...", "width=500 height=500 depth=1 constrain average interpolation=Bilinear");
saveAs("TIFF", path+subTitle+"_b.tif");

selectWindow(title);
a0 = size;a1 = 0; a2 = size; a3 = size;
makeRectangle(a0,a1,a2,a3);
run("Duplicate...", "title="+subTitle+"c");
crop(a0,a1,a2,a3,title,subTitle+"c");
//run("Size...", "width=500 height=500 depth=1 constrain average interpolation=Bilinear");
saveAs("TIFF", path+subTitle+"_c.tif");

selectWindow(title);
a0 = size;a1 = size; a2 = size; a3 = size;
makeRectangle(a0,a1,a2,a3);
run("Duplicate...", "title="+subTitle+"d");
crop(a0,a1,a2,a3,title,subTitle+"d");
//run("Size...", "width=500 height=500 depth=1 constrain average interpolation=Bilinear");
saveAs("TIFF", path+subTitle+"_d.tif");

run("Close All");