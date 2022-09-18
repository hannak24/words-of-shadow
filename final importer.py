
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import Rhino
import scriptcontext


HOUR = 12
MINUTES = 30
MONTH=1
DAY=1
YEAR=2022


def SetDateTime(YEAR,MONTH,DAY,HOURS,MINUTES):
    from datetime import datetime
    date = datetime(YEAR, MONTH, DAY, HOURS, MINUTES)
    
    print "DATE "+str(YEAR)+","+str(MONTH)+","+str(DAY)+" TIME: "+str(HOURS)+","+str(MINUTES)
    
    RhinoSun = Rhino.RhinoDoc.ActiveDoc.Lights.Sun
    RhinoSun.Enabled = 1
    RhinoSun.SkylightOn = 0
    RhinoSun.Intensity = 0.6
    RhinoSun.North = 180.0
    latitude = 32.045
    longitude = 34.77
    Rhino.Render.Sun.SetPosition(RhinoSun, date, latitude, longitude)


def adjustDisplayMode(mode):
    views = rs.ViewNames() 
    modes=rs.ViewDisplayModes()
    if (mode == "Rendered"):
        viewtype="Rendered"
    else:
        viewtype="Raytraced"
    rs.EnableRedraw(True)
    if viewtype in modes: 
       for view in views: 
            rs.ViewDisplayMode(view, viewtype)

def adjustCameraLoc():
    view = scriptcontext.doc.Views.ActiveView
    #location = rs.CreatePoint(833.807,897.261,462.84)
    location = rs.CreatePoint(1462.567,1573.871,811.86)
    lookat = rs.CreatePoint(-0.0,0.0,0.0)
    vp = view.ActiveViewport
    # save the current viewport projection
    vp.PushViewProjection()
    vp.CameraUp = Rhino.Geometry.Vector3d.ZAxis
    vp.SetCameraLocation(location, False)
    vp.SetCameraDirection(lookat - location, True)
    view.Redraw()
    return Rhino.Commands.Result.Success

def cancleGroundPlane():
    groundPlane =  Rhino.RhinoDoc.ActiveDoc.GroundPlane
    groundPlane.Enabled = 0
    return Rhino.Commands.Result.Success

def OBJImportSettings():
    e_str = " _ImportObjGroupsAs=_ObjectNames "
    e_str+= "_IgnoreTextures=_No "
    e_str+= "_MapYtoZ=_No "
    e_str+= "_MorphTargetOnly=_No "
    e_str+= "_ReverseGroupOrder=_No "
    e_str+= "_Split32BitTextures=_No"
    return e_str

def split(word):
    return [char for char in word]

def BatchConvertTo3dm():
    word = rs.GetString("Enter the word: ")
    word = word.upper()
    letters = split(word)
    print(letters)
    #Get folders
    folder = rs.BrowseForFolder(message="Select folder to process")
    if not folder: return
    found = False ; counter=0 ; ext="3dm"
    rs.EnableRedraw(False)
    sett=OBJImportSettings()
    #Find Rhino files in the folder
    i=0
    location = (0,0,0)
    for letter in letters:
        for filename in os.listdir(folder):
            filenameNoExt = filename.split('.')[0]
            if filename.endswith(ext)and filenameNoExt == letter:
                print(filename)
                found = True
                fullpath=os.path.join(folder,filename).lower()
                rs.EnableRedraw(False)
                moveLetterToPoint(fullpath, rs.CreatePoint(location),sett)
                if rs.LastCommandResult()==0: counter+=1
        i+=1
        location = list(location)
        location[1] = location[1] + 50
        location = tuple(location)
        rs.EnableRedraw(True)
    if not found:
        msg="No .{} files found in selected folder!".format(ext)
    else:
        msg="Successfully imported {} .{} files.".format(counter,ext)
    rs.MessageBox(msg)
    
    

def moveLetterToPoint(path, location,sett):
    # Get the starting object runtime serial number
    start_sn = Rhino.DocObjects.RhinoObject.NextRuntimeSerialNumber
    # Script the Import command
    comm_str="_-Import "+chr(34)+path+chr(34)+sett+" _Enter"
    rs.Command (comm_str, False)
    if rs.LastCommandResult()==0: print("success!")
    # Get the ending object runtime serial number
    end_sn = Rhino.DocObjects.RhinoObject.NextRuntimeSerialNumber
    print(end_sn)
    # If the scripted command completed successfully and new objects were
    # added to the document, end_sn will be greater than start_sn. So all
    # that's left to do is find the newly added objects.
    rh_objects = []
    for sn in range(start_sn, end_sn):
        rh_obj = sc.doc.Objects.Find(sn)
        if rh_obj:
          rh_objects.append(rh_obj)
  # Move the newly added objects (example)
    print("location: ", location)
    dir = Rhino.Geometry.Vector3d(location)
    xform = Rhino.Geometry.Transform.Translation(dir)
    for rh_obj in rh_objects:
        sc.doc.Objects.Transform(rh_obj, xform, True)
    # Done!
    sc.doc.Views.Redraw()

cancleGroundPlane()


SetDateTime(YEAR,MONTH,DAY,HOUR,MINUTES)
BatchConvertTo3dm()
adjustCameraLoc()
adjustDisplayMode("Rendered")
adjustDisplayMode("Raytraced")
adjustDisplayMode("Rendered")


