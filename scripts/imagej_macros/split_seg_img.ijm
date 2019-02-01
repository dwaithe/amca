

img_dir_img = "/Users/dwaithe/Documents/collaborators/WaitheD/region_prop/broad/MP6843_img_full/";
img_dir_seg = "/Users/dwaithe/Documents/collaborators/WaitheD/region_prop/broad/MP6843_seg/";
//getDirectory("image")
lim = 20;

start_xarr = newArray(0,256,0,256);
start_yarr = newArray(0,0,256,256);
start_warr = newArray(256,512,256,512);
start_harr = newArray(256,512,512,512);

file_list = getFileList(img_dir_img);
for(f=0;f<lengthOf(file_list);f++){

open(img_dir_img+file_list[f]);
//saveAs("Jpeg", "/Users/dwaithe/Documents/collaborators/WaitheD/region_prop/broad/MP6843_segs/"+count+".jpg");
//count += 1;
title = getTitle();

for(e=0;e<4;e++){
run("Clear Results");
selectWindow(title);
run("Select None");


start_x = start_xarr[e];
start_y = start_yarr[e];
start_w = start_warr[e];
start_h = start_harr[e];

//start of the code.
start0 = 0;
for(c=1;c<3;c++){
idx = indexOf(title, "w");
filename = substring(title,0,idx);
if(File.exists(img_dir_seg+filename+"_GT_0"+c+".tif")){
open(img_dir_seg+filename+"_GT_0"+c+".tif");
makeRectangle(start_x, start_y, start_w-start_x ,start_h-start_y );
run("Duplicate...", " ");
run("Select None");
}
}
