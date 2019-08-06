/*
 * -----------------------------------------------------------------------------
 *  Copyright (C) 2018 University of Dundee. All rights reserved.
 *
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * ------------------------------------------------------------------------------
 */

/*
 * This Groovy script shows how to analyse an OMERO dataset
 * i.e. a collection of OMERO images.
 * For that example, we use the analyse particles plugin.
 * The generated ROIs are then saved back to OMERO.
 * Use this script in the Scripting Dialog of Fiji (File > New > Script).
 * Select Groovy as language in the Scripting Dialog.
 * Error handling is omitted to ease the reading of the script but this
 * should be added if used in production to make sure the services are closed
 * Information can be found at
 * https://docs.openmicroscopy.org/latest/omero5/developers/Java.html
 */

import java.util.ArrayList


// OMERO Dependencies
import omero.gateway.Gateway
import omero.gateway.LoginCredentials
import omero.gateway.SecurityContext
import omero.gateway.facility.BrowseFacility
import omero.gateway.facility.ROIFacility
import omero.log.SimpleLogger

import org.openmicroscopy.shoola.util.roi.io.ROIReader

import loci.formats.FormatTools
import loci.formats.ImageTools
import loci.common.DataTools

import ij.IJ
import ij.ImagePlus
import ij.ImageStack
import ij.process.ByteProcessor
import ij.process.ShortProcessor
import ij.plugin.frame.RoiManager



// Setup
// =====

// OMERO Server details
HOST = "cbomero.imm.ox.ac.uk"
PORT = 4064

//  parameters to edit
dataset_id = 4253
local_folder_path = "/Users/dwaithe/Documents/collaborators/WaitheD/micro_vision/acquisitions/slide2/data_correct_dim_order/"
USERNAME = "dwaithe"
PASSWORD = 'TR@N$late1thisnow'

def connect_to_omero() {
    "Connect to OMERO"

    credentials = new LoginCredentials()
    credentials.getServer().setHostname(HOST)
    credentials.getServer().setPort(PORT)
    credentials.getUser().setUsername(USERNAME.trim())
    credentials.getUser().setPassword(PASSWORD.trim())
    simpleLogger = new SimpleLogger()
    gateway = new Gateway(simpleLogger)
    gateway.connect(credentials)
    return gateway

}

def get_image_ids(gateway, ctx, dataset_id) {
    "List all image's ids contained in a Dataset"

    browse = gateway.getFacility(BrowseFacility)

    ids = new ArrayList(1)
    ids.add(new Long(dataset_id))
    images = browse.getImagesForDatasets(ctx, ids)

    j = images.iterator()
    image_ids = new ArrayList()
    while (j.hasNext()) {
        image_ids.add(j.next().getId())
    }
    return image_ids
}


def open_image_plus(HOST, USERNAME, PASSWORD, PORT, group_id, image_id) {
    "Open the image using the Bio-Formats Importer"

    StringBuilder options = new StringBuilder()
    options.append("location=[OMERO] open=[omero:server=")
    options.append(HOST)
    options.append("\nuser=")
    options.append(USERNAME.trim())
    options.append("\nport=")
    options.append(PORT)
    options.append("\npass=")
    options.append(PASSWORD.trim())
    options.append("\ngroupID=")
    options.append(group_id)
    options.append("\niid=")
    options.append(image_id)
    options.append("] ")
    options.append("windowless=true view=Hyperstack ")
    IJ.runPlugIn("loci.plugins.LociImporter", options.toString())

}


def save_rois_to_omero(ctx, image_id, imp) {
    " Save ROI's back to OMERO"
    reader = new ROIReader()
    roi_list = reader.readImageJROIFromSources(image_id, imp)
    roi_facility = gateway.getFacility(ROIFacility)
    result = roi_facility.saveROIs(ctx, image_id, exp_id, roi_list)

    roivec = new ArrayList()

    j = result.iterator()
    while (j.hasNext()) {
        roidata = j.next()
        roi_id = roidata.getId()

        i = roidata.getIterator()
        while (i.hasNext()) {
            roi = i.next()
            shape = roi[0]
            t = shape.getZ()
            z = shape.getT()
            c = shape.getC()
            println 'tte'+String.valueOf(z)+String.valueOf(c)+String.valueOf(t)
            shape_id = shape.getId()
            roivec.add([roi_id, shape_id, z, c, t])
        }
    }
    return roivec
}

// Prototype analysis example
gateway = connect_to_omero()
exp = gateway.getLoggedInUser()
group_id = exp.getGroupId()
ctx = new SecurityContext(group_id)
exp_id = exp.getId()

// get all images_ids in an omero dataset
ids = get_image_ids(gateway, ctx, dataset_id)


ids.each() { id ->
    // Open the image
    
    open_image_plus(HOST, USERNAME, PASSWORD, PORT, group_id, String.valueOf(id))
    imp = IJ.getImage()
    imp.show()
    
	title = imp.getTitle()
	imp.changes = false     // Prevent "Save Changes?" dialog
    imp.close()
	file_to_load = local_folder_path+title	
	
	imp2 = IJ.openImage(file_to_load);
	imp2.show()
	
   
	
	IJ.run("To ROI Manager", "");



    rm = RoiManager.getInstance()
    
    // Save the ROIs back to OMERO
    roivec = save_rois_to_omero(ctx, id, imp2)
    // Close the various components
    
    IJ.selectWindow("ROI Manager")
    IJ.run("Close")
    imp.changes = false     // Prevent "Save Changes?" dialog
    imp.close()
    imp2.changes = false
    imp2.close()
}
// Close the connection
gateway.disconnect()
println "processing done"
