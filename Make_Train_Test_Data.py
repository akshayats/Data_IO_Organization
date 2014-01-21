#!/usr/bin/env python3.3
"""
FileName    : make_json_from_xmls.py
Usage       : make_json_from_xmls.py [-h] <input_FOLDER> <output_file>
              
              input_FOLDER contains all the XML files that need to be considered for conversion
              output_file is the name of the output JSON file
              example:
                $ python make_json_from_xmls.py /home/path/to/XmlFolder /home/ExampleJsonFile.json 

Description : Script written to read in many filename.xml files contained in a single foleder. The 
			  object data contained in all the XML files are collected and reformatted. The 
			  reformatted data is then collectively written into one JSON file.
"""

import errno
import getopt
import json
import sys
import os
from os import listdir
from os.path import isfile, join
import os.path, time
import xml.etree.ElementTree as ET
import warnings
import numpy as NP
import math as M

# DEFINE
def allDefinedLists():
        global AllPossibleObjectTypes
        AllPossibleObjectTypes   = ['Mouse',
                                    'Keyboard',
                                    'Monitor',
                                    'Headphones',
                                    'Laptop',

                                    'Pen',
                                    'Pencil',
                                    'Book',
                                    'Papers',
                                    'PenStand',
                                    'Marker',
                                    'Highlighter',
                                    'Rubber',
                                    'Notebook',
                                    'Folder',

                                    'Lamp',
                                    'Telephone',
                                    'Mobile',
                                    'Keys',
                                    'SoftFish',
                                    
                                    'Glass',
                                    'Mug',
                                    'Jug',
                                    'Flask',
                                    'Bottle',
                                    ]
        global StudentList
        StudentList              = [
                                    'Akshaya',
                                    'Ali',
                                    'Francisco',
                                    'Hossein',
                                    'Kaiyu',
                                    'Magnus',
                                    'Michele',
                                    'Miro',
                                    'Nils',
                                    'Puren',
                                    'Rares',
                                    'Rasmus',
                                    'Yuquan'
                                   ]
        global ResearcherList
        ResearcherList           = [
                                    'David',
                                    'Florian',
                                    'Marina',
                                    'Oscar',
                                    'Petter',
                                    'Yasemin',
                                   ]
        global ProfessorList
        ProfessorList            = [
                                    'Carl',
                                    'Hedvig',
                                    'Petter',
                                   ]

allDefinedLists()

#------------------------------------------------------------------------------
class BBox():
    def __init__(self, length, width, height, x, y, z, pitch, roll, yaw):
        # Raw Bounding Box at (0,0,0) of Table and No Rotations of Appropraite Size
        self.RawBBox    = [
                        [0,        0, 0],              # Lower Left
                        [0+length, 0, 0],              # Lower Right
                        [0+length, 0, 0+height],       # Upper Right
                        [0,        0, 0+height],       # Upper Left
                        [0,        0+width, 0],        # Lower Left
                        [0+length, 0+width, 0],        # Lower Right
                        [0+length, 0+width, 0+height], # Upper Right
                        [0,        0+width, 0+height] # Upper Left
                       ]
        self.RawBBox   = NP.matrix(self.RawBBox)

        # Convert to Radians
        self.P        = float(pitch)*M.pi/180
        self.R        = float(roll)*M.pi/180
        self.Y        = float(yaw)*M.pi/180
        # Rotation Matrix for Brian-Tait Angles
        self.RotMat   = [
                         [M.cos(self.Y)*M.cos(self.P),   M.cos(self.Y)*M.sin(self.P)*M.sin(self.R)-M.sin(self.Y)*M.cos(self.R),   M.sin(self.Y)*M.sin(self.R)+M.cos(self.Y)*M.sin(self.P)*M.cos(self.R)],
                         [M.sin(self.Y)*M.cos(self.P),   M.cos(self.Y)*M.cos(self.R)+M.sin(self.Y)*M.sin(self.P)*M.sin(self.R),   M.sin(self.Y)*M.sin(self.P)*M.cos(self.R)-M.cos(self.Y)*M.sin(self.R)],
                         [-M.sin(self.P),                M.cos(self.P)*M.sin(self.R),                                             M.cos(self.P)*M.cos(self.R)                                          ]
                        ]
        self.RotMat   = NP.matrix(self.RotMat)
        # Affine Transform Matrix
        OriginShift   = [[x], [y], [z]]
        self.AffMat   = NP.hstack([self.RotMat, OriginShift])
        AffineMaker   = [0,0,0,1]
        self.AffMat   = NP.vstack([self.AffMat, AffineMaker])

        # Make Affine Transformation & Get Affine Transformed Bounding Box
        TempBBox           = NP.vstack((self.RawBBox.T, NP.ones((1, self.RawBBox.shape[0]))))
        TempMat            = self.AffMat*TempBBox
        self.BoundingBox   = TempMat[0:3,:].T

        # Find Front Face
        self.FrontFace   = self.BoundingBox[0:4, :]

        # Make Quaternion out of Brian-Tait (Euler) Angles
        # psi = gamma = yaw
        # theta = alpha = pitch
        # phi = beta = roll
        # Wikilink: http://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        # w   = Quaternion(1);
        # x   = Quaternion(2);
        # y   = Quaternion(3);
        # z   = Quaternion(4);
        # Rotate Using Following Matrix:
        # QuatRotationMat   = [ 1-2*y^2-2*z^2, 2*x*y-2*w*z, 2*x*z+2*w*y;
        #                       2*x*y+2*w*z,   1-2*x^2-2*z^2, 2*y*z-2*w*x;
        #                       2*x*z-2*w*y,   2*y*z+2*w*x,   1-2*x^2-2*y^2];
        # RotatedVertices(3xN)   = QuatRotationMat(3x3)*OriginalVertices(3xN)

        sp   = M.sin(self.P/2)
        cp   = M.cos(self.P/2)
        sr   = M.sin(self.R/2)
        cr   = M.cos(self.R/2)
        sy   = M.sin(self.Y/2)
        cy   = M.cos(self.Y/2)

        self.Quaternion   = [
                                cr*cp*cy + sr*sp*sy,
                                sr*cp*cy - cr*sp*sy,
                                cr*sp*cy + sr*cp*sy,
                                cr*cp*sy - sr*sp*cy
                            ]

        # Find Geometrical Center of Bounding Box
        ColSums       = self.BoundingBox.sum(axis = 0)
        self.Center   = ColSums/8

#------------------------------------------------------------------------------

# Helper Classes
class XmlData():
    """ XML Data of a single scene from a single XML-file with getter functions
"""
    def __init__(self, XmlFileRoot, CurrXmlFileName):
        self.XmlFileRoot   = XmlFileRoot
        
        # Filename Handling
        # FullFileName     = self.XmlFileRoot[1].text 
        # Above^ commented out to avoid inconsistencies in naming. This is caused by the "annotatedFrom"
        # field in the XML file which contains the address and file name of the PCD file used when annotating.
        # i.e. Local path name of annotator. e.g. Akhil/home/strands/set1objs/Akshaya_Mor.xml
        FullFileName     = CurrXmlFileName
        WoExt            = os.path.splitext(FullFileName)[0]
        SplitWoExt       = WoExt.split("/", 200) # There Cannot be More Than 200 Directories
        FileName         = SplitWoExt[-1] # Take Last Part of Full Path - Stripped of Extension Name
        SplitFileName    = FileName.split("_seg",20) # 20 is Another Large Number
        self.SceneName   = SplitFileName[0]

        # Find Out Type of User
        self.SplitSceneName   = self.SceneName.split("_",20)
        UserName              = self.SplitSceneName[0]
        if UserName in StudentList:
            self.UserType   = "_Student_"
        elif UserName in ProfessorList:
            self.UserType   = "_Professor_"
        elif UserName in ResearcherList:
            self.UserType   = "_Researcher_"
        else:
            self.UserType   = "_Unknown_"

        # Find Number of Objects
        NumOfObjects             = int(self.XmlFileRoot[3][0].text)
        # Initialize Containers
        self.AllObjectTypes      = dict() # Container for Object-Type Strings
        self.AllObjectsInScene   = list() # Container for (Object,Object-Type) String Tuples
        self.AllBoundingBoxes    = dict() # Container for Bounding Box 8 Vertices - Arrays
        self.AllFrontFaces       = dict() # Container for Bounding Box Front Faces 4 Vertices - Arrays
        self.AllQuaternions      = dict() # Container for BBox Orientations = Quaternions 
        self.AllCenters          = dict() # Container for BBox Geometrical Center Points 
        # Loop Over All Objects
        for ObjNum in range(1, NumOfObjects+1):   # 0th Entry is Number Of Objects

            # ACCESSING OBJECT NAME DETAILS
            # ------------------------------
            CurrObjName         = self.XmlFileRoot[3][ObjNum][0].text
            # Remove Upper Case
            CurrObjName_lc      = CurrObjName.lower();
            # Remove Underscores From Multiple Instances
            CurrObjName_split   = CurrObjName.split("_",10)
            CurrObjType         = CurrObjName_split[0]
            # Check If New Type Of Object - Give Warnings
            if not CurrObjType in AllPossibleObjectTypes:
                print "TSA: New object type found! -   " + CurrObjType

            # ACCESSING OBJECT DIMENSION DETAILS
            # ----------------------------------
            # Get Box Dimensions
            CurrObjLength       = float(self.XmlFileRoot[3][ObjNum][3][0].text)
            CurrObjWidth        = float(self.XmlFileRoot[3][ObjNum][3][1].text)
            CurrObjHeight       = float(self.XmlFileRoot[3][ObjNum][3][2].text)
            # Get Box Origin Position wrt Table Origin
            CurrObj_X           = float(self.XmlFileRoot[3][ObjNum][2][0].text)
            CurrObj_Y           = float(self.XmlFileRoot[3][ObjNum][2][1].text)
            CurrObj_Z           = float(self.XmlFileRoot[3][ObjNum][2][2].text)
            # Get Box Orientations
            CurrObj_Pitch       = float(self.XmlFileRoot[3][ObjNum][2][3].text)
            CurrObj_Roll        = float(self.XmlFileRoot[3][ObjNum][2][4].text)
            CurrObj_Yaw         = float(self.XmlFileRoot[3][ObjNum][2][5].text)

            # MAKE BOUNDING BOX CLASS-OBJECT
            # ------------------------------
            # Make a Raw Bounding Box at Origin of Table and No Orientations
            CurrObjBBox         = BBox(CurrObjLength,CurrObjWidth, CurrObjHeight, CurrObj_X, CurrObj_Y, CurrObj_Z, CurrObj_Pitch, CurrObj_Roll, CurrObj_Yaw)
            # APPEND AND STORE DATA TO BE ACCESSED
            # ------------------------------------
            # Add Entries to Dictionaries
            self.AllObjectTypes[CurrObjName_lc]     = CurrObjType
            self.AllQuaternions[CurrObjName_lc]     = CurrObjBBox.Quaternion
            # Add Object to Dictionary After Converting to a List Data Container
            self.AllBoundingBoxes[CurrObjName_lc]   = CurrObjBBox.BoundingBox.tolist()
            self.AllFrontFaces[CurrObjName_lc]      = CurrObjBBox.FrontFace.tolist()
            TempArray                               = CurrObjBBox.Center.tolist() # To Remove 2D Array from a.sum() Result
            self.AllCenters[CurrObjName_lc]         = TempArray[0]

            # Add Entries to Lists
            self.AllObjectsInScene.append(CurrObjName_lc)

    def get_userType(self):
        return self.UserType

    def get_sceneName(self):
    	return self.SceneName

    def get_objectTypes(self):
        return self.AllObjectTypes

    def get_objectsInScene(self):
        return self.AllObjectsInScene

    def get_bboxVertices(self):
        return self.AllBoundingBoxes

    def get_quaternions(self):
        return self.AllQuaternions

    def get_bboxCenters(self):
        return self.AllCenters

    def get_splitSceneName(self):
        return self.SplitSceneName

    def get_bboxFrontFaceVertices(self):
        return self.AllFrontFaces
# -------------------------------------------------------------------------------------
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def help_msg():
    return """
Usage: scene_converter.py [-h] <input_file> <output_file>

input_file scenes to be converted
output_file converted scenes

-h, --help for seeing this msg
"""

morse = None

if __name__ == "__main__":
    argv = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error as msg:
            raise Usage(msg)

        if ('-h','') in opts or ('--help', '') in opts or len(args) is not 2:
            raise Usage(help_msg())

        XmlFolderPath        = args[0]
        JsonOutputFileName   = args[1]

        # Error Checking in Input Arguments

        # Input Arguments Handling
        # JsonOutputFileName   = "JsonTrialWrite.json"
        # XmlFolderPath        = "/home/akshaya/technical/tinker-box/database/211013/pcd-files-downsampled"

        # Read in & Store All File Names of Target XML Files
        AllFileNames    = [ f for f in listdir(XmlFolderPath) if isfile(join(XmlFolderPath,f)) ]
        # pprint(AllFileNames)

        # Make Sure to Select Only XML Files From All Files In Folder
        XmlFileNames   = list();
        for CurrFile in AllFileNames:
            if (".xml" in CurrFile):
                XmlFileNames.append(CurrFile)
        # pprint(XmlFileNames)
        # Exception: No XML Files in Folder
        if len(XmlFileNames) == 0:
            sys.exit("Error_TSA: No XML files found in current folder! Exiting.")

        # Initialize a JSON Data Structure
        JsonData   = list();

        # Loop Over All Target XML Files
        WithFolderName   = list();
        for CurrXmlFile in XmlFileNames:
        	# Initialize the Dictionaries
            pos    = dict()
            ori    = dict()
            bbox   = dict()
            objT   = dict()
            # Make Actual Filename To Open
            InFile        = XmlFolderPath + '/' + CurrXmlFile
            # Open Current XML File And Load Data
            XmlFileTree     = ET.parse(InFile)
            XmlFileRoot     = XmlFileTree.getroot()

            # Get All Scene Details of Currently Opened File
            CurrXmlData            = XmlData(XmlFileRoot, CurrXmlFile)
            CurrTableType          = "_OfficeTable_"
            CurrUserType           = CurrXmlData.get_userType()
            CurrSceneName          = CurrXmlData.get_sceneName() 
            CurrSceneObjTypes      = CurrXmlData.get_objectTypes()
            CurrSceneObjNames      = CurrXmlData.get_objectsInScene()
            CurrSceneBBoxes        = CurrXmlData.get_bboxVertices()
            CurrSceneFFaces        = CurrXmlData.get_bboxFrontFaceVertices()
            CurrSceneQuaternions   = CurrXmlData.get_quaternions()
            CurrSceneBBoxCenters   = CurrXmlData.get_bboxCenters()
            
            # Get Time Stamp For File
            CurrSplitSceneName     = CurrXmlData.get_splitSceneName()
            # Date
            yyyy   = int(CurrSplitSceneName[-2][0:2])+2000 # Assuming In This Millenium :D
            mm     = CurrSplitSceneName[-2][2:4]
            dd     = CurrSplitSceneName[-2][-2:]
            # Time
            if CurrSplitSceneName[-1] == 'Mor':
                StartTime   = "09:00"
            elif CurrSplitSceneName[-1] == 'Aft':
                StartTime   = "14:00"
            elif CurrSplitSceneName[-1] == 'Eve':
                StartTime   = "18:00"
            CurrSceneTime   = str(yyyy) + ":" + mm + ":" + dd +":" + StartTime
            
            # Redistribute Contents of XML File Into JSON Data Structure
            JsonData.append({
                             'scene_id' : CurrSceneName,
                             'type': CurrSceneObjTypes,
                             'objects': CurrSceneObjNames,
                             'bbox': CurrSceneBBoxes,
                             'orientation': CurrSceneQuaternions,
                             'position': CurrSceneBBoxCenters,
                             'table-type':CurrTableType,
                             'user-type': CurrUserType,
                             'date': CurrSceneTime,
                             'front-faces': CurrSceneFFaces
                            })

        # End Loop Over XML Files

        # Save JSON Data Structure as JSON File 
        with open(JsonOutputFileName,'w') as out_file:
             out_file.write(json.dumps(JsonData, out_file, indent=2))

        print "Done. Converted", len(JsonData), "scenes."
    
    except Usage as err:
        print(err.msg)
        print("for help use --help")