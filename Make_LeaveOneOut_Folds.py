#!/usr/bin/env python3.3
"""
FileName    : Make_LeaveOneOut_Folds.py
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
Usage: Make_Train_Test_Data.py [-h] <input_FILE> <number of data-tuples> <training data fold percent>

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

        JsonFileName     = args[0]
        NumOfDataSets    = int(args[1])
        TrainPercent     = int(args[2])
        DATA_THROW_DIR   = './data-tuples-loo'

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
            os.makedirs(DATA_THROW_DIR)
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
            NumOfTrainScenes   = int(round(float(NumOfScenes)*float(TrainPercent)/100))

            # print NumOfTrainScenes
            # print "Test Scenes = %d" % (NumOfScenes - NumOfTrainScenes)

            # Leaving Out People
            # -------------------------------------------
            # Calculate Number Of Names To Leave Out
            NumOfPeople      = len(PeopleInData)
            NumToLeaveOut    = NumOfPeople - int(TrainPercent / 5)
            # Which Names to Leave Out?
            AllPeopleIndxs   = xrange(0, NumOfPeople)
            PeopleIndxs      = random.sample(AllPeopleIndxs, NumToLeaveOut)
            PeopleNP         = NP.array(PeopleInData)   # Convert to numpy array
            TestPeople       = list(PeopleNP[PeopleIndxs])
            print "People left out of Training Data: %s" % TestPeople

            # Find Array of All Indices For Selecting the Training Set, Test Set
            AllSceneIndxs   = xrange(0, NumOfScenes)
            
            # Find Indices Of Dictionary With These Names = Test Data
            TestIndxs   = list()
            for j in AllSceneIndxs:
                CurrSceneID   = Scenes[j]['scene_id']
                for c in xrange(0, NumToLeaveOut):
                    if TestPeople[c] in CurrSceneID:
                        TestIndxs.append(j)

            # Find Indices of Dictionary Without These Names = Training Data                        
            SetDiff               = set(AllSceneIndxs) - set(TestIndxs)
            TrainIndxs            = list(SetDiff)
            DelivrdTrainPercent   = float(len(TrainIndxs)) / float(NumOfScenes)*100

            # ---------------------------------------------
            # Dialogue
            print "Selected scenes for Train Data:"
            print TrainIndxs
            print "Selected scenes for Test Data:"
            print TestIndxs
            # Select Those List Entries Corresponding to Indices
            ScenesNP    = NP.array(Scenes)   # Convert to numpy array
            TrainData   = list(ScenesNP[TrainIndxs])
            TestData    = list(ScenesNP[TestIndxs])

            # Output Raw Data In Files
            TrainFileName     = DATA_THROW_DIR + "/TrainData_" + str(TrainPercent) + "p_" + str(d) + ".json"
            TestFileName      = DATA_THROW_DIR + "/TestData_"  + str(TrainPercent) + "p_" + str(d) + ".json"
            EncTestFileName   = DATA_THROW_DIR + "/TestDataEnc_"  + str(TrainPercent) + "p_" + str(d) + ".json"
            DecKeyFileName    = DATA_THROW_DIR + "/TestDataDec_"  + str(TrainPercent) + "p_" + str(d) + ".json"

            # Append Folding Metadata To Data
            CurrTime   = str(datetime.datetime.now())
            
            TrainData.append({
                                'creation-time': CurrTime,
                                'data-set-type': 'Leave-One-Out Folding',
                                'train_percent': DelivrdTrainPercent,
                                'people-left-out': TestPeople
                })

            TestData.append({
                                'creation-time': CurrTime,
                                'data-set-type': 'Leave-One-Out Folding',
                                'train_percent': DelivrdTrainPercent,
                                'people-left-out': TestPeople
                })
            # Write Out Raw Train and Test Data Files
            with open(TrainFileName,'w') as out_file:
                 out_file.write(json.dumps(TrainData, out_file, indent=2))

            with open(TestFileName,'w') as out_file:
                 out_file.write(json.dumps(TestData, out_file, indent=2))

            # Encryption of Test Data
            # -------------------------
            # Initialize
            EncTestData      = list()
            DecryptKeyData   = list()
            for s in xrange(0, len(TestData)-1):
                # Dialogue
                print "------------------------------------------------------"
                print "%d -- Processing scene : " %s +TestData[s]["scene_id"]
                print "------------------------------------------------------"
                # Encryption Process
                # -------------------
                # Get Object Types
                sObjectTypeList    = TestData[s]["type"]
                sNumOfObjects      = len(sObjectTypeList)
                # Dialogue
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
                # Dialogue
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
                            # else:
                            #     sCurrDict[k].pop(obj, None)

                # Store Modified Dictionary in Encrypted Test Data Dictionary
                EncTestData.append(sCurrDict)

                # Store Scene Name To Decryption Data Structure
                DecryptKeyData.append({
                                        "scene_id":sCurrDict["scene_id"],
                                        "decrypt-key":sDecryptKey
                                    })

                print "++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print "                                                      "

            # Put Data Creation Metadata
            EncTestData.append({
                                'creation-time': CurrTime,
                                'data-set-type': 'Leave-One-Out Folding',
                                'train_percent': DelivrdTrainPercent,
                                'people-left-out': TestPeople
                                })

            # Put Data Creation Metadata
            DecryptKeyData.append({
                                'creation-time': CurrTime,
                                'data-set-type': 'Leave-One-Out Folding',
                                'train_percent': DelivrdTrainPercent,
                                'people-left-out': TestPeople
                                })

            # Write Out Encrypted Data to File
            with open(EncTestFileName,'w') as out_file:
                 out_file.write(json.dumps(EncTestData, out_file, indent=2))
            # Write Out Decryption Key to File
            with open(DecKeyFileName,'w') as out_file:
                 out_file.write(json.dumps(DecryptKeyData , out_file, indent=2))
            # Dialogue
            print 'Completed Test Data = %d' % (d+1)
            print "============================================================"
        # Close Openned Files
        JsonInFileHndl.close()
    except Usage as err:
        print(err.msg)
        print("for help use --help")