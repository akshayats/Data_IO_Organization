#!/usr/bin/env python3.3
"""
FileName    : Make_Train_Test_Data.py
Usage       : Make_Train_Test_Data.py [-h] <input_FILE> <number of data-tuples> <training data fold percent>

              For Example:
                $ python Make_Train_Test_Data.py python Make_Train_Test_Data.py ExampleJsonFile.json 10 90 
              ExampleJsonFile.json -    contains all the data scenes from which (train.json, test.json)
                                        are randomly folded
              10                    -   10 data tuple instances need to be generated
              90                    -   in each data tuple 90 % of entire data in ExampleJsonFile.json is training data 
                                        and 10% of entire data in ExampleJsonFile.json is test data (both randomly picked)
                

Description :   Script written to read in a data file containing many table top scenes and then fold them 
                randomly to obtain (train, test) data tuples.

NOTE:           There is a provision to consider only for Set1Objects or Set1Objects+Set2Objects
"""

import getopt
import json
import sys
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

        if ('-h','') in opts or ('--help', '') in opts or len(args) is not 3:
            raise Usage(help_msg())
        #############################
        # Set This Flag to 1 to Consider only Set1Objects
        SET1OBJFLAG     = 1
        #############################
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
            TrainFileName     = "./data-tuples/TrainData_" + str(TrainPercent) + "p_" + str(d) + ".json"
            TestFileName      = "./data-tuples/TestData_"  + str(TrainPercent) + "p_" + str(d) + ".json"
            EncTestFileName   = "./data-tuples/TestDataEnc_"  + str(TrainPercent) + "p_" + str(d) + ".json"
            DecKeyFileName    = "./data-tuples/TestDataDec_"  + str(TrainPercent) + "p_" + str(d) + ".json"
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