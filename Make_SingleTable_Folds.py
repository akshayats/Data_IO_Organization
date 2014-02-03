#!/usr/bin/env python3.3
"""
FileName    : Make_SingleTable_Folds.py
Usage       : Make_SingleTable_Folds.py [-h] <input_FILE> <number of fold-instances>

              For Example:
                $ python Make_SingleTable_Folds.py ExampleJsonFile.json 10
              ExampleJsonFile.json -    contains all the data scenes from which (train.json, test.json)
                                        are randomly folded
              10                    -   10 different random ways of folding the data i.e. first split
              in each data tuple 60% names entire data in ExampleJsonFile.json is training data and 40% names of
              entire data in ExampleJsonFile.json is test data (both randomly picked)

              The data is initially cut across people names, and then each of these slices are subjected to the 
              above hard random splitting.

              Once the data is split this way, the training data is varied to exist in the range [10,100]% of
              it's full size.
                

Description :   Script written to read in a data file containing many table top scenes and then fold them 
                randomly pick correct number of people to leave out (from Train Data) to obtain (train, test) data tuples.

"""

import getopt
import json
import sys
import numpy as NP
import datetime
import random
import os
import copy
import math

# DEFINE
def allDefinedLists():
        global PeopleInData
        PeopleInData    =[
                           'Akshaya',
                           'Ali',
                           'Carl',
                           'David',
                           'Florian',
                           'Francisco',
                           'Hossein',
                           'Kaiyu',
                           'Magnus',
                           'Marina',
                           'Michele',
                           'Miro',
                           'Nils',
                           'Oscar',
                           'Petter',
                           'Puren',
                           'Rares',
                           'Rasmus',
                           'Yasemin',
                           'Yuquan'
                         ]
allDefinedLists()

# -------------------------------------------------------------------------------------
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def help_msg():
    return """
Usage: Make_SingleTable_Folds.py [-h] <input_FILE> <number of fold-instances>

input_FILE : Data to be folded in .JSON format
number-of-fold-instances : Number of instances of data foldings required. Different ways the names are picked

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
        JsonFileName         = args[0]
        NumOfFoldInstances   = int(args[1])
        DATA_THROW_DIR       = './single-table-foldings'
        TRAIN_PERCENT        = 60
        TEST_PERCENT         = 100 - TRAIN_PERCENT

        # Error Handling
        if NumOfFoldInstances < 1:
            raise Exception('TSA::Wrong required number of data-sets!')

        # Open Data File and Load All Data
        JsonInFileHndl   = open(JsonFileName)
        Scenes           = json.load(JsonInFileHndl)
        NumOfScenes      = len(Scenes)

        # Make Data Output Directory
        try:
            os.makedirs(DATA_THROW_DIR)
        except OSError:
            pass

        # Total Number of People in Data
        NumOfPeople      = len(PeopleInData)
        AllPeopleIndxs   = xrange(0, NumOfPeople)
        # Total Number of Scenes in Data
        AllSceneIndxs    = xrange(0, NumOfScenes)


        # How Many Names to Loop Over
        for ppl in AllPeopleIndxs:
            CurrName             = PeopleInData[ppl]
            # Dialogue
            print "==========================================================="
            print "       Person = %s" % CurrName
            print "==========================================================="
            CurrDataSplitIndxs   = list()
            # Get All Indices of Curr Name
            for j in AllSceneIndxs:
                CurrSceneID   = Scenes[j]["scene_id"]
                if CurrName in CurrSceneID:
                    CurrDataSplitIndxs.append(j)
            # Get All Data of Current Name
            # Select Those List Entries Corresponding to Indices
            ScenesNP          = NP.array(Scenes)   # Convert to numpy array
            CurrDataSplit     = list(ScenesNP[CurrDataSplitIndxs])
            CurrNumOfScenes   = len(CurrDataSplit)
            # Ascertain Number of Scenes According to Percentage
            NumInTrainSplit   = int(round(CurrNumOfScenes*TRAIN_PERCENT/100))

            # Split into Train and Test Splits
            for d in xrange(0, NumOfFoldInstances):
                print "-------------------------------------------------------------------------"
                print "           STARTING DATA-TUPLE-SET # %d                    " % d
                print "-------------------------------------------------------------------------"
                # Initialise Training and Test Data 
                TrainData   = list()
                TestData    = list()
                Indxs       = list()
                # Find Indices For Selecting the Training Set, Test Set
                CurrSceneIndxs    = xrange(0, CurrNumOfScenes)
                TrainIndxs        = random.sample(CurrSceneIndxs, NumInTrainSplit)
                TrainSceneIndxs   = xrange(0, NumInTrainSplit)
                SetDiff           = set(CurrSceneIndxs) - set(TrainIndxs)
                TestIndxs         = list(SetDiff)
                # Select Those List Entries Corresponding to Indices
                ScenesNP    = NP.array(CurrDataSplit)   # Convert to numpy array
                TrainPool   = list(ScenesNP[TrainIndxs])
                TestData    = list(ScenesNP[TestIndxs])# Encryption of Test Data
                # Encryption of Test Data
                # -------------------------
                # Initialize
                EncTestData      = list()
                DecryptKeyData   = list()
                for s in xrange(0, len(TestData)):
                    # Dialogue
                    # print "------------------------------------------------------"
                    # print "%d -- Processing scene : " %s +TestData[s]["scene_id"]
                    # print "------------------------------------------------------"
                    # Encryption Process
                    # -------------------
                    # Get Object Types
                    sObjectTypeList    = TestData[s]["type"]
                    sNumOfObjects      = len(sObjectTypeList)
                    # Dialogue
                    # print sObjectTypeList
                    # print sNumOfObjects
                    # Make Encrypt and Decrypt Maps
                    sEncryptKey   = dict()
                    sDecryptKey   = dict()
                    count         = 0
                    for o,t in sObjectTypeList.iteritems():
                        CurrObjName                = 'Obj' + str(count)
                        sEncryptKey[o]             = CurrObjName
                        sDecryptKey[CurrObjName]   = str(t)
                        count                     += 1
                    # Dialogue
                    # print "Encrypt Key is:"
                    # print sEncryptKey
                    # print "Decrypt Key is:"
                    # print sDecryptKey
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
                                ObjectType             = sObjectTypeList[obj]
                                OldKey                 = obj
                                NewKey                 = sEncryptKey[obj]
                                sCurrDict[k][NewKey]   = sCurrDict[k].pop(OldKey)

                    # Store Modified Dictionary in Encrypted Test Data Dictionary
                    EncTestData.append(sCurrDict)

                    # Store Scene Name To Decryption Data Structure
                    DecryptKeyData.append({
                                            "scene_id":sCurrDict["scene_id"],
                                            "decrypt-key":sDecryptKey
                                        })
                # Make Training Percent [10,20,...,100]% of TRAIN_PERCENT Input Original Data
                for tp in range(10, 110, 10):
                    TrainPercent   = tp
                    # Output Raw Data In Files
                    TrainFileName     = DATA_THROW_DIR +  "/TrainData_" + CurrName + "_" + str(TrainPercent) + "p_" + str(d) + ".json"
                    TestFileName      = DATA_THROW_DIR +  "/TestData_"  +  CurrName + "_" + str(TrainPercent) + "p_" + str(d) + ".json"
                    EncTestFileName   = DATA_THROW_DIR +  "/TestDataEnc_"  +  CurrName + "_" + str(TrainPercent) + "p_" + str(d) + ".json"
                    DecKeyFileName    = DATA_THROW_DIR +  "/TestDataDec_"  +  CurrName + "_" + str(TrainPercent) + "p_" + str(d) + ".json"
                    # Ascertain Number of Scenes According to Percentage
                    NumOfTrainSamples   = int(round(NumInTrainSplit*tp/100))
                    # Find Indices For Selecting the Training Set
                    TrainIndxs          = random.sample(TrainSceneIndxs, NumOfTrainSamples)
                    # Select Those List Entries Corresponding to Indices
                    TrainScenesNP       = NP.array(TrainPool)   # Convert to numpy array
                    TrainData           = list(TrainScenesNP[TrainIndxs])

                    # Append Folding Metadata to Data
                    # ------------------------------------------------------
                    CurrTime   = str(datetime.datetime.now())
                    TrainData.append({  
                                        'train-split': TRAIN_PERCENT,
                                        'creation-time': CurrTime,
                                        'data-set-type': 'Single-Table Folding',
                                        'train-percent': TrainPercent
                                        })
                    TestData.append({
                                        'train-split': TRAIN_PERCENT,
                                        'creation-time': CurrTime,
                                        'data-set-type': 'Single-Table Folding',
                                        'train-percent': TrainPercent
                                        })
                    EncTestData.append({
                                        'train-split': TRAIN_PERCENT,
                                        'creation-time': CurrTime,
                                        'data-set-type': 'Single-Table Folding',
                                        'train-percent': TrainPercent
                                        })
                    DecryptKeyData.append({
                                        'train-split': TRAIN_PERCENT,
                                        'creation-time': CurrTime,
                                        'data-set-type': 'Single-Table Folding',
                                        'train-percent': TrainPercent
                                        })
                    # ------------------------------------------------------

                    # Write Into Training Data File
                    with open(TrainFileName,'w') as out_file:
                         out_file.write(json.dumps(TrainData, out_file, indent=2))
                    # Write Into Test Data File
                    with open(TestFileName,'w') as out_file:
                         out_file.write(json.dumps(TestData, out_file, indent=2))
                    # Write Out Encrypted Test Data to File
                    with open(EncTestFileName,'w') as out_file:
                        out_file.write(json.dumps(EncTestData, out_file, indent=2))
                    # Write Out Decryption Key of Test Data to File
                    with open(DecKeyFileName,'w') as out_file:
                        out_file.write(json.dumps(DecryptKeyData , out_file, indent=2))
                    # Dialogue
                    print "Data Written for Train Percent = %d %%" % tp
                # Dialogue            
                print "++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print "                                                      "
                print 'COMPLETED DATA-TUPLE SET = %d' % d
                print "------------------------------------------------------"
        # Close Openned Files
        JsonInFileHndl.close()
    except Usage as err:
        print(err.msg)
        print("for help use --help")