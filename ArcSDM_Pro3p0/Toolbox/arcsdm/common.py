# -*- coding: utf-8 -*-
import sys, os, traceback
import arcpy
import arcsdm.config as cfg
from arcsdm.exceptions import SDMError

PY2 = sys.version_info[0] == 2
PY34 = sys.version_info[0:2] >= (3, 4)

if PY2:
    from imp import reload;
if PY34:
    import importlib

def reload_arcsdm_modules(messages):
    arcsdm_modules = [m.__name__ for m in sys.modules.values() if m and m.__name__.startswith(__package__)]
    for m in arcsdm_modules:
        try:
            reload_module(sys.modules[m])
        except Exception as e:
            messages.AddMessage("Failed to reload module %s. Reason:%s" %(m, e.message))
    messages.AddMessage("Reloaded %s modules" % __package__)

def reload_module(name):
    if PY2:
        reload(name)
    if PY34:
        importlib.reload(name)

def execute_tool(func, self, parameters, messages):
    if cfg.RELOAD_MODULES:
        # reload arcsdm.* modules
        reload_arcsdm_modules(messages)
        # update func ref to use reloaded code
        func.__code__ = getattr(sys.modules[func.__module__],  func.__name__).__code__
    if cfg.USE_PTVS_DEBUGGER:
        messages.AddMessage("Waiting for debugger..")
        try:
            from arcsdm.debug_ptvs import wait_for_debugger
            wait_for_debugger()
        except:
            messages.AddMessage("Failed to import debug_ptvs. Is ptvsd package installed?")
    try:
        # run the tool
        func(self, parameters, messages)
    except:
        tb = sys.exc_info()[2]
        errors = "Unhandled exception caught\n" + traceback.format_exc()
        arcpy.AddError(errors)         

def addToDisplay(layer, name, position):
    result = arcpy.MakeRasterLayer_management(layer, name)
    lyr = result.getOutput(0)
    product = arcpy.GetInstallInfo()['ProductName']
    if "Desktop" in product:
        mxd = arcpy.mapping.MapDocument("CURRENT")
        dataframe = arcpy.mapping.ListDataFrames(mxd)[0]
        arcpy.mapping.AddLayer(dataframe, lyr, position)
    elif "Pro" in product:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        m = aprx.listMaps("Map")[0] 
        m.addLayer(lyr, position)