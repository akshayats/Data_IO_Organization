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
from os import listdir
from os.path import isfile, join
import os.path, time
import xml.etree.ElementTree as ET
import warnings
import math as M


import numpy as NP
import datetime
import random
import os
import copy


from pprint import pprint

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
Usage: scene_converter.py [-h] <input_file> <output_file>

input_file scenes to be converted
output_file converted scenes

-h, --help for seeing this msg
"""



if __name__ == "__main__":
    argv = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error as msg:
            raise Usage(msg)

        if ('-h','') in opts or ('--help', '') in opts or len(args) is not 3:
            raise Usage(help_msg())

        JsonFileName    = args[0]
        NumOfDataSets   = int(args[1])
        TrainPercent    = int(args[2])

        # Error Handling
        if NumOfDataSets < 1:
            raise Exception('TSA::Wrong required number of data-sets!')
        if TrainPercent < 1 or TrainPercent > 100:
            raise Exception('TSA::Wrong percentage for training data!')
        # Open Data File and Load All Data
        JsonInFileHndl   = open(JsonFileName)
        Scenes           = json.load(JsonInFileHndl)
        NumOfScenes      = len(Scenes)

        # Make Data Output Directory
        try:
            os.makedirs('./data-tuples')
        except OSError:
            pass

        for d in xrange(0, NumOfDataSets):
            print "========================================================================="
            print "                       STARTING DATA-TUPLE-SET # %d                    " % d
            print "========================================================================="
            # Initialise Training and Test Data 
            TrainData   = list()
            TestData    = list()
            Indxs       = list()

            # Ascertain Number of Scenes According to Percentage
            NumOfTrainScenes   = int(round(NumOfScenes*TrainPercent/100))
            # print NumOfTrainScenes
            # print "Test Scenes = %d" % (NumOfScenes - NumOfTrainScenes)

            # Find Indices For Selecting the Training Set, Test Set
            AllSceneIndxs   = xrange(0, NumOfScenes)
            TrainIndxs      = random.sample(AllSceneIndxs, NumOfTrainScenes)
            SetDiff         = set(AllSceneIndxs) - set(TrainIndxs)
            TestIndxs       = list(SetDiff)
            print "Selected scenes for Train Data:"
            print TrainIndxs
            print "Selected scenes for Test Data:"
            print TestIndxs

            # Select Those List Entries Corresponding to Indices
            ScenesNP    = NP.array(Scenes)   # Convert to numpy array
            TrainData   = list(ScenesNP[TrainIndxs])
            TestData    = list(ScenesNP[TestIndxs])

            # Output Raw Data In Files
            TrainFileName     = "./data-tuples/TrainData_" + str(d) + ".json"
            TestFileName      = "./data-tuples/TestData_"  + str(d) + ".json"
            EncTestFileName   = "./data-tuples/TestDataEnc_"  + str(d) + ".json"
            DecKeyFileName    = "./data-tuples/TestDataDec_"  + str(d) + ".json"
            with open(TrainFileName,'w') as out_file:
                 out_file.write(json.dumps(TrainData, out_file, indent=2))

            with open(TestFileName,'w') as out_file:
                 out_file.write(json.dumps(TestData, out_file, indent=2))

            # Encryption of Test Data
            # -------------------------
            # Initialize
            EncTestData      = list()
            DecryptKeyData   = list()
            # Put a Time Stamp 
            EncTestData.append({
                                'creation-time': str(datetime.datetime.now()),
                                'data-set-type': 'Random_Folding',
                                'train-percent': TrainPercent
                                })
            for s in xrange(0, len(TestData)):
                print "------------------------------------------------------"
                print "%d -- Processing scene : " %s +TestData[s]["scene_id"]
                print "------------------------------------------------------"
                # Encryption Process
                # -------------------
                # Get Object Types
                sObjectTypeList   = TestData[s]["type"]
                sNumOfObjects      = len(sObjectTypeList)
                print sObjectTypeList
                print sNumOfObjects
                # Make Encrypt and Decrypt Maps
                sEncryptKey   = dict()
                sDecryptKey   = dict()
                count         = 0
                for o,t in sObjectTypeList.iteritems():
                    CurrObjName                = 'Obj' + str(count)
                    sEncryptKey[o]             = CurrObjName
                    sDecryptKey[CurrObjName]   = str(t)
                    count                     += 1
                print "Encrypt Key is:"
                print sEncryptKey
                print "Decrypt Key is:"
                print sDecryptKey
                # Initialize Current Scene Dictionary for Encryption
                sCurrDict   = copy.deepcopy(TestData[s])
                # Remove Unneeded Fields
                sCurrDict.pop("table-type", None)
                sCurrDict.pop("user-type", None)
                sCurrDict.pop("date", None)
                sCurrDict.pop("objects", None)
                sCurrDict.pop("type", None)

                # Rename Keys According to Encryption Map
                for k in sCurrDict.keys():
                    if k != "scene_id":
                        for obj in sCurrDict[k].keys():
                            ObjectType   = sObjectTypeList[obj]
                            if ObjectType in Set1Objects:
                                OldKey                 = obj
                                NewKey                 = sEncryptKey[obj]
                                sCurrDict[k][NewKey]   = sCurrDict[k].pop(OldKey)
                            else:
                                sCurrDict[k].pop(obj, None)

                # Store Modified Dictionary in Encrypted Test Data Dictionary
                EncTestData.append(sCurrDict)

                # Store Scene Name To Decryption Data Structure
                DecryptKeyData.append({
                                        "scene_id":sCurrDict["scene_id"],
                                        "decrypt-key":sDecryptKey
                                    })

                print "++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print "                                                      "

            # Write Out Encrypted Data to File
            with open(EncTestFileName,'w') as out_file:
                 out_file.write(json.dumps(EncTestData, out_file, indent=2))
            # Write Out Decryption Key to File
            with open(DecKeyFileName,'w') as out_file:
                 out_file.write(json.dumps(DecryptKeyData , out_file, indent=2))
            # Dialogue Output For Completion
            print 'Completed Test Data = %d' % (d+1)
            print "============================================================"
        # Close Openned Files
        JsonInFileHndl.close()
    except Usage as err:
        print(err.msg)
        print("for help use --help")



        # for s in range(0,len(TestData)):
        #         print TestData[s]["scene_id"]
        #         # Encrypt Test Data
        #         ObjectTypeList   = TestData[s]["type"]
        #         NumOfObjects     = len(ObjectTypeList)
        #         # Make Encrypt and Decrypt Maps
        #         EncryptKey   = dict()
        #         DecryptKey   = dict()
        #         count        = 0;
        #         for o, t in ObjectTypeList.iteritems():
        #             CurrEncName               = 'Obj'+str(count)
        #             EncryptKey[o]             = CurrEncName
        #             DecryptKey[CurrEncName]   = str(t)
        #             count                    += 1
        #         # Remove Unneeded Fields
        #         CurrDict   = TestData[s]
        #         CurrDict.pop("table-type", None)
        #         CurrDict.pop("user-type", None)
        #         CurrDict.pop("date", None)
        #         CurrDict.pop("objects", None)
        #         # CurrDict.pop("type", None)
        #         print CurrDict["type"]
        #         # Rename Keys According to Encryption Map
        #         for k in CurrDict.keys():
        #             if k != "scene_id":
        #                 for obj in CurrDict[k].keys():
        #                     ObjectType   = ObjectTypeList[obj]
        #                     if ObjectType in Set1Objects:
        #                         OldKey                = obj
        #                         NewKey                = EncryptKey[obj]
        #                         CurrDict[k][NewKey]   = CurrDict[k].pop(OldKey)
        #                     else:
        #                         CurrDict[k].pop(obj, None)
        #         for k in CurrDict.keys():
        #             print k
        #         # Store Modified Dictionary
        #         EncTestData.append(CurrDict)
        #     with open(EncTestFileName,'w') as out_file:
        #          out_file.write(json.dumps(EncTestData, out_file, indent=2))

        #     print 'Completed Test Data = %d' % (d+1)