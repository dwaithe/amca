//This script generates an overview image of a dataset.

srcdir = "/Volumes/Dominic/2021_01_22_0004_20x_air/";
img_size = 1024;// for 20x
pxsz = 665.60/1024;

//srcdir = "//Volumes/Dominic/2021_01_22_0005_40x_air/";
//img_size = 1024; //for 100x
//pxsz = 332/1024;

setBatchMode("hide");
FolderList = getFileList(srcdir); 

xCoords = newArray(FolderList.length);
yCoords = newArray(FolderList.length);
xCoords_val = newArray(FolderList.length);
yCoords_val = newArray(FolderList.length);

c =0
for (k=0; k<FolderList.length; k++) { 
        m=FolderList[k]; 
        u3 = ".tif";
        print(indexOf (m,u3));
        
        if (indexOf (m,u3) > -1){
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
}
xCoords = Array.trim(xCoords, c);
yCoords = Array.trim(yCoords, c);
xCoords_val = Array.trim(xCoords_val, c);
yCoords_val = Array.trim(yCoords_val, c);

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
	print(minX,maxX);
	print(minY,maxY);
	
	
	sizeY = (maxY)-(minY);
	sizeX = (maxX)-(minX);
	//print(sizeX,sizeY);
	sizeX = round((sizeX/pxsz)+img_size);
	sizeY = round((sizeY/pxsz)+img_size);

	newImage("out", "16-bit black", sizeX, sizeY, 1);
//exit();	
//print("minX",minX,"minY",minY);
for (k=0; k<xCoords.length; k++) { 
//open the files.

	filepath = srcdir+"img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+".tif";
	print(filepath);
	//exit();
	open(filepath);	
	ex = getTitle();
	 
	a = exec("stat", "-f%m", filepath);
	print(ex,'\t',nSlices,'\t',a);
	
	
	//run("Z Project...", "projection=[Max Intensity]");
	run("Remove Overlay");
	//run("Flatten");
	run("Flip Horizontally");
	//run("Flip Vertically");
	run("Select All");
	run("Specify...", "width="+(img_size)+" height="+(img_size)+" x=0 y=0");
	run("Copy");
	//exit()
	
	selectWindow("out");
	setPasteMode("Replace");
	
	//print("minX",minX,"minY",minY);
	xco = ((xCoords[k]-minX)/pxsz);
	yco = ((yCoords[k]-minY)/pxsz);
	//print(xco,yco);
	run("Specify...", "width="+(img_size)+" height="+(img_size)+" x="+xco+" y="+yco+"");
	run("Paste");
	//setForegroundColor(255,255,255);
	//run("Draw");
	close("img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+".tif");
	close("MAX_img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+".tif");
	close("MAX_img_stk_x_"+xCoords_val[k]+"y_"+yCoords_val[k]+"-1.tif");
	//exit();
}
setBatchMode("show");
run("Select All");
//run("Flip Horizontally");
rename("out_minX"+minX+"_minY"+minY);
	

	