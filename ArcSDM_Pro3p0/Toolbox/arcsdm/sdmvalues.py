
""" SDM Values / ArcSDM 5 for ArcGis 
    conversion by Tero Ronkko / Geological survey of Finland 2016
    
    History: 
    27.9.2016 Output cleaned and getMaskSize fixed

A function to append Spatial Data Modeller parameters to Geoprocessor History
    for those SDM tools that have the following values:
    gp: geoprocessor object
    unitCell: unit cell area in sq km
    TrainPts: training sites Points feature class
"""


import traceback, sys
from arcsdm.exceptions import SDMError
import arcpy
import os
import arcgisscripting
    
ToMetric = {
    'square meters to square kilometers' : 0.000001,
    'square feet to square kilometers' : 0.09290304 * 1e-6,
    'square inches to square kilometers' : 0.00064516 * 1e-6,
    'square miles to square kilometers' : 2.589988110647
    }
    


def execute(self, parameters, messages):
    #Obsolete, needs refactoring!
    gp = arcgisscripting.create() 
    TrainingSites =  parameters[0].valueAsText        
    Unitarea = float( parameters[1].value)        
    appendSDMValues(gp,  Unitarea, TrainingSites)
    arcpy.AddMessage("\n" + "="*40);
    arcpy.AddMessage("\n")       
    

# Returns prior probability against mask/training points    
def getPriorProb(TrainPts ,unitCell, mapUnits) :
    size = getMaskSize;
    num_tps = arcpy.GetCount_management(TrainPts)
    #arcpy.AddMessage("%-20s %s"% ('amount:' ,num_tps))
    #arcpy.addmessage("%-20s %s" % ("Unit Cell Area:", "{}km^2, Cells in area: {} ".format(unitCell,num_unit_cells)))
        
    total_area = getMaskSize(mapUnits) # Now the getMaskSize returns it correctly in sqkm   : * cellsize **2 * conversion
      #gp.addMessage("Debug));
    unitCell = float(unitCell)
    total_area = float(total_area);
    num_unit_cells = total_area / unitCell
    num_tps = count = int(num_tps.getOutput(0))
    priorprob = num_tps / num_unit_cells
    return priorprob;
    

    
#Return mask size in sqkm
def getMaskSize (mapUnits):
    try:
        desc = arcpy.Describe(arcpy.env.mask);
        #arcpy.AddMessage( "getMaskSize()");
        if (desc.dataType == "RasterDataset"):
            raise arcpy.ExecuteError("RasterDataset type is not allowed as Mask!");
        if (desc.dataType == "RasterLayer" or desc.dataType == "RasterDataset"):
            #arcpy.AddMessage( " Counting raster size");                       
            maskrows = arcpy.SearchCursor(desc.catalogpath)        
            maskrow = maskrows.next()
            count =  0
            while maskrow:
                count += maskrow.count
                maskrow = maskrows.next()
            cellsize = float( str(arcpy.env.cellSize.replace(",",".")) )             
            count = count * (cellsize * cellsize);
          
        if (desc.dataType == "FeatureLayer" or desc.dataType == "FeatureClass"):
            #arcpy.AddMessage( " Calculating mask size");           
            maskrows = arcpy.SearchCursor(desc.catalogpath)
            shapeName = desc.shapeFieldName                
            maskrow = maskrows.next()
            count =  0
            while maskrow:
                feat = maskrow.getValue(shapeName)
                count += feat.area;
                maskrow = maskrows.next()
           
        mapUnits = mapUnits.lower().strip()
        if not mapUnits.startswith('meter'):
                arcpy.AddError('Incorrect output map units: Check units of study area.')
        conversion = getMapConversion( mapUnits)
        count = count * conversion;
            #Count is now in Sqkm -> So multiply that with 1000m*1000m / cellsize ^2
            #multiplier = (1000 * 1000) / (cellsize * cellsize); #with 500 x 500 expect "4"
            #arcpy.AddMessage("Debug:" + str(multiplier));
            #count = count * multiplier;
        #arcpy.AddMessage("Size: " + str(count));
        return count
    except arcpy.ExecuteError as e:
            
        raise;
    except:
        # get the traceback object
        tb = sys.exc_info()[2]
        #gp.addError("sdmvalues.py excepted:");
        # tbinfo contains the line number that the code failed on and the code from that line
        tbinfo = traceback.format_tb(tb)[0]
        arcpy.AddError ( tbinfo );
        # concatenate information together concerning the error into a message string
        #pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
        #    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        # generate a message string for any geoprocessing tool errors
        if len(arcpy.GetMessages(2)) > 0:
            msgs = "SDM GP ERRORS:\n" + arcpy.GetMessages(2) + "\n"
            arcpy.AddError(msgs)
        #gp.AddError(pymsg)
        raise;
    
    
    
def appendSDMValues(gp, unitCell, TrainPts):
    try:
        arcpy.AddMessage("\n" + "="*10 + " arcsdm values  " + "=" *10);
        with open (os.path.join(os.path.dirname(__file__), "arcsdm_version.txt"), "r") as myfile:
            data=myfile.readlines()
        #Print version information
        arcpy.AddMessage("%-20s %s" % ("", data[0]) ); 
        if not gp.workspace:
            gp.adderror('Workspace not set')
            raise arcpy.ExecuteError("Workspace not set!");
        if not (arcpy.Exists(gp.workspace)):
            gp.adderror('Workspace %s not found'%(gp.workspace))
            raise arcpy.ExecuteError('Workspace %s not found'%(gp.workspace));
        desc = arcpy.Describe(gp.workspace)
        gp.addmessage("%-20s %s (%s)" % ("Workspace: ", gp.workspace, desc.workspaceType));
        
        if not gp.scratchworkspace:
            gp.adderror('Scratch workspace mask not set')
        wdesc = arcpy.Describe(gp.scratchworkspace)       
        gp.addmessage("%-20s %s (%s)" % ("Scratch workspace:",  gp.scratchworkspace, wdesc.workspaceType))
        # TODO: These should be moved to common CHECKENV class/function TR
        
        # Tools wont work if type is different from eachother (joins do not work filesystem->geodatabase! TR
        if (wdesc.workspaceType != desc.workspaceType):
            gp.AddError("Workspace and scratch workspace must be of the same type!");
            raise arcpy.ExecuteError("Workspace type mismatch");
        
        mapUnits = getMapUnits()
        mapUnits = mapUnits.lower().strip()
        if not mapUnits.startswith('meter'):
            gp.addError('Incorrect output map units: Check units of study area.')            
        conversion = getMapConversion(mapUnits)                
        #gp.addMessage("Conversion from map units to km^2: " + str(conversion));
        gp.addmessage("%-20s %s" % ( 'Map Units:',  mapUnits))
     
        
        if not gp.mask:
            gp.adderror('Study Area mask not set');
            raise arcpy.ExecuteError ("Mask not set");
        else:
            if not arcpy.Exists(gp.mask):
                gp.addError("Mask " + gp.mask + " not found!");
                raise arcpy.ExecuteError("Mask not found");
            #gp.AddMessage("Mask set");
            desc = gp.describe(gp.mask);
            gp.addMessage( "%-20s %s" %( "Mask:", "\"" + desc.name + "\" and it is " + desc.dataType));           
            gp.addMessage( "%-20s %s" %( "Mask size:", str(getMaskSize(mapUnits))  ));           
            #gp.AddMessage("Masksize: " + str(getMaskSize()));            
        
        if not gp.cellsize:        
            gp.adderror('Study Area cellsize not set')
        if (gp.cellsize == "MAXOF"):
            arcpy.AddWarning("Cellsize should have definitive value?");
            #raise arcpy.ExecuteError("SDMValues: Cellsize must have value");
            
        
        cellsize = arcpy.env.cellSize #float(str(arcpy.env.cellSize).replace(",","."))
        gp.addmessage("%-20s %s" %("Cell Size:", cellsize))
        #gp.addMessage("Debug: " + str(conversion));
        total_area = getMaskSize(mapUnits) # Now the getMaskSize returns it correctly in sqkm   : * cellsize **2 * conversion
        #gp.addMessage("Debug));
        unitCell = float(unitCell)
        num_unit_cells = total_area / unitCell
        num_tps = gp.GetCount_management(TrainPts)
        gp.addmessage("%-20s %s"% ('# Training Sites:' ,num_tps))
        gp.addmessage("%-20s %s" % ("Unit Cell Area:", "{}km^2, Cells in area: {} ".format(unitCell,num_unit_cells)))
        
        priorprob = num_tps / num_unit_cells
        if not (0 < priorprob <= 1.0):
            arcpy.AddError('Incorrect no. of training sites or unit cell area. TrainingPointsResult {}'.format(priorprob))
            raise arcpy.ExecuteError
            #raise SDMError('Incorrect no. of training sites or unit cell area. TrainingPointsResult {}'.format(priorprob))
        gp.addmessage("%-20s %0.6f" % ('Prior Probability:', priorprob))
        #gp.addmessage("Debug priorprob:" + str(getPriorProb(TrainPts, unitCell))) 
        
        gp.addmessage("%-20s %s" % ('Training Set:', gp.describe(TrainPts).catalogpath))
        gp.addmessage("%-20s %s" % ('Study Area Raster:', gp.describe(gp.mask).catalogpath))
        gp.addmessage("%-20s %s" % ( 'Study Area Area:', str(total_area) + "km^2"))
        #gp.addmessage('Map Units to Square Kilometers Conversion: %f'%conversion)
        arcpy.AddMessage(""); # Empty line at end
    except arcpy.ExecuteError as e:
        if not all(e.args):
            arcpy.AddMessage("Calculate weights caught arcpy.ExecuteError: ");
            args = e.args[0];
            args.split('\n')
            arcpy.AddError(args);
        arcpy.AddMessage("-------------- END EXECUTION ---------------");        
        raise;
    except:
        # get the traceback object
        tb = sys.exc_info()[2]
        # tbinfo contains the line number that the code failed on and the code from that line
        tbinfo = traceback.format_tb(tb)[0]
        gp.addError ( tbinfo );
        # concatenate information together concerning the error into a message string
        #pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
        #    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        # generate a message string for any geoprocessing tool errors
        if len(gp.GetMessages(2)) > 0:
            msgs = "SDM GP ERRORS:\n" + gp.GetMessages(2) + "\n"
            gp.AddError(msgs)
        #gp.AddError(pymsg)
        raise;

        

def getMapConversion(mapUnits):
    pluralMapUnits = {'meter':'meters', 'foot':'feet', 'inch':'inches', 'mile':'miles'}
    conversion = ToMetric["square %s to square kilometers"%pluralMapUnits[mapUnits]]
    return conversion    

def getMapUnits(silent=False): 
    """ Get document map units from g.outputcoordinatesystem """
    try:
        #Get spatial reference of geoprocessor
        ocs = arcpy.env.outputCoordinateSystem
        if not ocs:
            #arcpy.AddError('Output Coordinate System not set')
            if (not silent):
                arcpy.AddWarning("Output coordinate system not set - defaulting mapunit to meter");
            #raise arcpy.ExecuteError('SDMValues: Output Coordinate System not set');
            return "meter";
        #else:
        #arcpy.AddMessage("Outputcoordinate system ok");
        ##Replace apostrophes with quotations
        #ocs = ocs.replace("'",'"')
        ##Open scratch file for output
        #prjfile = arcpy.createuniquename('coordsys', gp.scratchFolder) + '.prj'
        ##Write spatial reference string to scratch file
        #fdout = open(prjfile,'w')
        #fdout.write(ocs)
        #fdout.write('\n')
        #fdout.close()
        ##Create spatial reference object
        #spatref = gp.createobject('spatialreference')
        #Populate it by parsing of scratch file
        #spatref.createfromfile(prjfile)
        #Return map units value
        #spatial_ref = arcpy.Describe(dataset).spatialReference
        if ocs.type == 'Projected':
            #arcpy.AddMessage("Projected system");
            return ocs.linearUnitName
            
        elif ocs.type == 'Geographic':
            #arcpy.AddMessage("Geographics system");
            return ocs.angularUnitName
        else:
            return None        
    except arcpy.ExecuteError as error:
        if not all(error.args):
            arcpy.AddMessage("SDMValues  caught arcpy.ExecuteError: ");
            args = e.args[0];
            args.split('\n')
            arcpy.AddError(args);
        #arcpy.AddMessage("-------------- END EXECUTION ---------------");        
        raise;
        #gp.AddMessage("Debug SDMVAlues exception");
    except:
        tb = sys.exc_info()[2]
        errors = traceback.format_exc()
        arcpy.AddError(errors)

        
      
