srcdir = "/Users/dwaithe/Downloads/full_stack_sparse/";
FolderList = getFileList(srcdir); 
xCoords = newArray(FolderList.length);
yCoords = newArray(FolderList.length);
xCoords_val = newArray(FolderList.length);
yCoords_val = newArray(FolderList.length);

img_size = 512;
pxsz = 0.26;

c =0
for (k=0; k<FolderList.length; k++) { 
        m=FolderList[k]; 
        //print(m);
		u1 = "x_"; 
		n1 = indexOf (m,u1); 
		u2 = "y_";
		n2 = indexOf (m,u2); 
		u3 = ".tif";
		n3 = indexOf (m,u3); 
		val0 =substring(m,n1+2,n2);
		val1 = substring(m,n2+2,n3);
		
		//print(val0,val1); 
		xCoords[c] =  parseFloat(val0);
		yCoords[c] =  parseFloat(val1);
		xCoords_val[c] = val0;
		yCoords_val[c] = val1;
		c+=1;
        //print(FolderList[k]); //The name of the folder is printed 
        //run("Image Sequence...", "open=[SourceDir+FolderList[k]] sort"); //but the images will not be opend 

} 

    xCoords_sorted = Array.copy(xCoords);
	Array.sort(xCoords_sorted);
	yCoords_sorted = Array.copy(yCoords);
	Array.sort(yCoords_sorted);

	minX = xCoords_sorted[0];
	minY = yCoords_sorted[0];
	maxX = xCoords_sorted[xCoords_sorted.length-1];
	maxY = yCoords_sorted[yCoords_sorted.length-1];

	//print(minX,maxX);
	//print(minY,maxY);
	
	if((minY)<(maxY)){
	}else
	{
	minYb = minY;
	minY = maxY;
	maxY = minYb;
	}
	
	
	if((minX)<(maxX)){
	}else
	{
	minXb = minX;
	minX = maxX;
	maxX = minXb;
	
	}
	//print(minX,maxX);
	//print(minY,maxY);
	
	
	sizeY = (maxY)-(minY);
	sizeX = (maxX)-(minX);
	//print(sizeX,sizeY);
	sizeX = (sizeX/pxsz)+img_size;
	sizeY = (sizeY/pxsz)+img_size;
	//print(sizeX,sizeY);
	
	//newImage("out", "RGB black", sizeX, sizeY, 1);
//print("minX",minX,"minY",minY);
for (k=0; k<xCoords.length; k++) { 
//open the files.

	filepath = srcdir+"img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+".tif";
	open(filepath);	
	ex = getTitle();
	 
	a = exec("stat", "-f%m", filepath);
	print(ex,'\t',nSlices,'\t',a);
	
	
	//run("Z Project...", "projection=[Max Intensity]");
	//run("Remove Overlay");
	//run("Flatten");
	//run("Flip Horizontally");
	//run("Flip Vertically");
	///run("Select All");
	//run("Specify...", "width="+(img_size)+" height="+(img_size)+" x=0 y=0");
	//run("Copy");
	
	//selectWindow("out");
	//setPasteMode("Add");
	
	//print("minX",minX,"minY",minY);
	//xco = ((xCoords[k]-minX)/pxsz);
	//yco = ((yCoords[k]-minY)/pxsz);
	//print(xco,yco);
	//run("Specify...", "width="+(img_size)+" height="+(img_size)+" x="+xco+" y="+yco+"");
	//run("Paste");
	//setForegroundColor(255,255,255);
	//run("Draw");
	close("img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+".tif");
	close("MAX_img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+".tif");
	close("MAX_img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+"-1.tif");
	//exit();
}
run("Select All");
//run("Flip Horizontally");
rename("out_minX"+minX+"_minY"+minY);
	

	