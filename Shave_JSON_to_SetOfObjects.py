#!/usr/bin/env python3.3
"""
FileName    : Shave_JSON_to_SetOfObjects.py
Usage       : Shave_JSON_to_SetOfObjects.py [-h] <input_FILE> <outpu_FILE>

              For Example:
                $ python Shave_JSON_to_SetOfObjects.py inFile.json inFileMod.json
              inFile.json           -   Contains raw dictionary data from XML files
              inFileMod.json        -   Contains modified dictionary data containing details of only objects 
                                        list of objects "Set1Objects" in this file. Rest is shaved off.
                

Description :   Script written to read in a data file containing many table top scenes and then fold them 
                modify the data file to contain information of interesting objects only.

"""

import getopt
import json
import sys
import copy

# DEFINE
def allDefinedLists():
        global Set1Objects
        Set1Objects              = [
                                    'Mouse',
                                    'Keyboard',
                                    'Monitor',
                                    'Papers',
                                    'Book',
                                    'Notebook',
                                    'Laptop',
                                    'Mobile',
                                    'Mug',
                                    'Glass',
                                    'Flask',
                                    'Bottle',
                                    'Jug'
                                   ]

allDefinedLists()

# -------------------------------------------------------------------------------------
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def help_msg():
    return """
Usage: Shave_JSON_to_SetOfObjects.py [-h] <input_file> <output_file>

input_file scenes to be converted
output_file converted scenes

-h, --help for seeing this msg
"""

# MAIN

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
        # Take Input File Name
        InJsonFileName    = args[0]
        OutJsonFileName   = args[1]
        # Open Data File and Load All Data
        JsonInFileHndl   = open(InJsonFileName)
        Scenes           = json.load(JsonInFileHndl)
        NumOfScenes      = len(Scenes)

        # Shaving Functionality to Retain Only Set1Objects, if Flag is Set
        JsonData_Mod   = list()
        for s in xrange(0, NumOfScenes):
            sCurrDict   = copy.deepcopy(Scenes[s])

            # Remove List of Object Instance Names
            sCurrDict.pop("objects", None)
            # Initialize New List
            sObjectNameList    = list()

            # Get Object Types
            sObjectTypeList    = Scenes[s]["type"]
            for k in sCurrDict.keys():
                if k != "scene_id" and k != "table-type" and k != "user-type" and k != "date" and k != "objects":
                    for obj in sCurrDict[k].keys():
                        objType   = sObjectTypeList[obj]
                        if objType not in Set1Objects:
                            sCurrDict[k].pop(obj, None)
                        else:
                            if obj not in sObjectNameList:
                                sObjectNameList.append(obj)
            # Include Modified Object Name List
            sCurrDict["objects"]   = sObjectNameList
            # Append Modified Scene-Dictionary to List of Scenes
            JsonData_Mod.append(sCurrDict)
            print "Completed scene %d / %d" % ((s+1), NumOfScenes)

        # Save JSON Data Structure as JSON File 
        with open(OutJsonFileName,'w') as out_file:
             out_file.write(json.dumps(JsonData_Mod, out_file, indent=2))
        # Close Openned Files
        JsonInFileHndl.close()        
    except Usage as err:
        print(err.msg)
        print("for help use --help")