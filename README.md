<img src="https://github.com/KenexDev/ArcSDM_Pro/blob/master/CDPhoto.jpg">

### Workflows for using ArcSDM in ArcGIS Pro
=======

## Notes:

So far this has only been tested on ArcGIS Pro 2.6

Logistic Regression hasn’t been fixed.

## Weights of Evidence

# Grand WofE has not been fixed and will not be fixed. Please use Calculate Weights and Calculate Response separately!

# All files must be stored inside a file geodatabase to run Calculate Weights (i.e. geodb1.gdb)

- Study area raster

- Training points

- All your derivative maps

# Initial environment settings:

# Current and scratch workspaces must be set to the working geodatabase

# Mask and snap raster should be set to the study area raster within the geodatabase

# Type the cell size and make sure your study area is on Unique values symbology to avoid getting a mask size error

# Calculate weights

- Save your weights tables inside the geodatabase

# Reclassify your derivative maps to binary and save inside a new file geodatabase (i.e. geodb2.gdb)

- Re-import the study area raster and training points to the new geodatabase

- Change environment settings so that the current and scratch workspaces are set to the new geodatabase and update the mask/snap raster to be the study area in the new geodatabase

- Recalculate weights tables for predictive maps

# Create a new file geodatabase to run Calculate Response (i.e. geodb3.gdb)

- Import the maps and weights tables for the maps you want to go into your mineral potential map

- Re-import the study area raster and training points to the new file geodatabase

- Again, change the current and scratch workspaces to the new file geodatabase and update the mask/snap raster to be the study area in the new geodatabase

- All your output pprb, conf, tstd, etc. files should go to the new geodatabase

# NOTE: You are just changing the location of where the files output to when you modify the environment settings. It is fundamentally the same settings – your study area remains the same. You could do all of this within a single geodatabase, but they get incredibly large very quickly because this is now where all the temp files end up, and it is easier to just make a new geodatabase at each processing stage.

# Run area-frequency and conditional independence tests from this last geodatabase you created, noting that your output files should go to the geodatabase.

# To run the area-frequency tool, it may be necessary to change the snap raster in the environment settings from your study area to the pprb map that you are analysing.

## Neural Networks

# All files must be stored inside a file geodatabase to run Neural Networks Input Files (i.e. NNgeodb.gdb)

- Study area raster

- Training points (both deposit and non-deposit training points required in separate files)

- The unique conditions grid for the maps you want to go into your neural network (make this using the Combine tool in spatial analyst)

# Environment settings:

- Current and scratch workspaces must be set to the working geodatabase

- Mask and snap raster should be set to the study area raster within the geodatabase

<img src="https://github.com/KenexDev/ArcSDM_Pro/blob/master/NN_input.png">

# Even if you set the train file output and class file output to be .dta files outside of the geodatabase, because the Pro environment settings are set to have the current and scratch workspace go to the geodatabase, it will output the files there by default. The tool won’t run if workspaces aren’t set to a geodatabase though…

- NOTE: ArcGIS doesn’t recognise .dta files, but this is required for the Neural Networks executable to run. It will look like the files don’t exist within the geodatabase if you try to look at it in ArcGIS or Catalog. You have to find the geodatabase file in Windows explorer (it will just look like a folder called NNgeodb.gdb or something) in explorer. Go into the folder, find the train.dta and class.dta files, and copy them to somewhere more appropriate.

# Find the GeoXplore executable within the ArcSDM folder that you are using on your local drive.

# Run your NN of choice (see Arianne for instructions if you need help)

# This will eventually give you a .rbn file at the end, which you need to import into Excel as a text file (comma delimited). Add a row at the top of the file, the first column is the UC value, second is an ID field, 3rd is the prospectivity value. Add these field names (UC, ID, Prospectivity).

# Save the file as an xslx file and import it into ArcGIS Pro.

# Join the UC value field in the UC raster to the UC field in the spreadsheet you just imported. Change the symbology to colour the raster by the prospectivity value.

# Done.

