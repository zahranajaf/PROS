#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import math

import louvain
import networkx as nx
import igraph as ig
import random
import operator
import json
import numpy as np
import Similaritymeasurment
import louvain_ext

# APP and SERVICES
TOTALNUMBEROFAPPS = 2
func_APPGENERATION = "nx.gn_graph(random.randint(2,7))"
func_SERVICEINSTR = "random.randint(1000,5000)"  # INSTR --> taking into account node speed this gives us between 200 and 600 MS
func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES and taking into account net bandwidth it gives us between 20 and 60 MS
func_SERVICERAM = "random.randint(1,3)"  # MB of RAM consumed by the service, taking into account noderesources and appgeneration we have to fit approx 1 app per node or about 10 services
func_STORAGE = "random.randint(1,3)"
APPDEADLINE=[500, 2500]
# USERS and IoT DEVICES
func_REQUESTPROB = "random.random()/4"
func_USERREQRAT = "random.randint(10,100)"  # MS
pathSimple = "./r1_PSO_20app_100R/100-1000requests/"


# **********************************************************************************************

# Functions for statistics of multilayer_community_detection

# **********************************************************************************************
# (deadline,shortestdistance):occurrences
statisticsDistanceDeadline = {}
cpu_usage = 0.0
# (service,deadline):occurrences
statisticsServiceInstances = {}

# distance:numberOfuserThatRequest
statisticsDistancesRequest = {}

# nodeid:numberOfuserThatRequest
statisticsNodesRequest = {}

# (nodeid,serviceId):ocurrences
statisticsNodesServices = {}

# (centrality,resources):occurrences
statisticsCentralityResources = {}


def calculateNodeUsage(service2DevicePlacementMatrix, nodeRAM, nodeSTORAGE, CPUCore, nodeBussyResources, nodeBussyStorage,nodeBussyCore):
    nodeResUse = list()
    nodeStorUse = list()
    nodeCoreUse = list()
    nodeNumServ = list()
    num_node_usage = 0
    Resource_usage = 0
    for i in service2DevicePlacementMatrix[0]:
        nodeResUse.append(0.0)
        nodeStorUse.append(0.0)
        nodeCoreUse.append(0.0)
        nodeNumServ.append(0)

    for idServ in range(0, len(service2DevicePlacementMatrix)):
        for idDev in range(0, len(service2DevicePlacementMatrix[idServ])):
            if service2DevicePlacementMatrix[idServ][idDev] == 1:
                nodeNumServ[idDev] = nodeNumServ[idDev] + 1
    for idDev in range(0, len(service2DevicePlacementMatrix[0])):
        nodeResUse[idDev] = nodeBussyResources[idDev] / nodeRAM[idDev]
        Resource_usage = Resource_usage + nodeBussyResources[idDev]
        nodeStorUse[idDev] = nodeBussyStorage[idDev] / nodeSTORAGE[idDev]
        nodeCoreUse[idDev] = nodeBussyCore[idDev] / CPUCore[idDev]
        if (nodeResUse[idDev] != 0):
            num_node_usage = num_node_usage + 1
        # nodeResUse[idDev] = nodeBussyResources[idDev]
    nodeResUse = sorted(nodeResUse)
    nodeStorUse = sorted(nodeStorUse)
    nodeCoreUse = sorted(nodeCoreUse)
    nodeNumServ = sorted(nodeNumServ)
    #print("This is the number of devices used in multi_layer partiotioning:", num_node_usage)
    return nodeResUse, nodeNumServ, nodeStorUse, nodeCoreUse


def writeStatisticsAllocation(G,appsDeadlines, tempServiceAlloc, clientId, appId):

    for talloc_ in tempServiceAlloc.items():

        dist_ = nx.shortest_path_length(G, source=clientId, target=talloc_[1], weight="weight")

        mykey_ = dist_
        if mykey_ in statisticsDistancesRequest:
            statisticsDistancesRequest[mykey_] = statisticsDistancesRequest[mykey_] + 1
        else:
            statisticsDistancesRequest[mykey_] = 1

        mykey_ = talloc_[1]
        if mykey_ in statisticsNodesRequest:
            statisticsNodesRequest[mykey_] = statisticsNodesRequest[mykey_] + 1
        else:
            statisticsNodesRequest[mykey_] = 1

        mykey_ = (talloc_[1], talloc_[0])
        if mykey_ in statisticsNodesServices:
            statisticsNodesServices[mykey_] = statisticsNodesServices[mykey_] + 1
        else:
            statisticsNodesServices[mykey_] = 1

        mykey_ = (appsDeadlines[appId], dist_)
        if mykey_ in statisticsDistanceDeadline:
            statisticsDistanceDeadline[mykey_] = statisticsDistanceDeadline[mykey_] + 1
        else:
            statisticsDistanceDeadline[mykey_] = 1

        mykey_ = (talloc_[0], appsDeadlines[appId])
        if mykey_ in statisticsServiceInstances:
            statisticsServiceInstances[mykey_] = statisticsServiceInstances[mykey_] + 1
        else:
            statisticsServiceInstances[mykey_] = 1
statisticsCentralityResources = {}


def writeStatisticsDevices(G,devices,nodeBussyResources, centralityValuesNoOrdered, service2DevicePlacementMatrix):
    for devId in G.nodes:
        mypercentageResources_ = float(nodeBussyResources[devId]) / float(devices[devId]['RAM'])
        mycentralityValues_ = centralityValuesNoOrdered[devId]
        mykey_ = (mycentralityValues_, mypercentageResources_)
        if mykey_ in statisticsCentralityResources:
            statisticsCentralityResources[mykey_] = statisticsCentralityResources[mykey_] + 1
        else:
            statisticsCentralityResources[mykey_] = 1


statisticsResources = {}


def writeStatisticsDevices1(service2DevicePlacementMatrix,G,nodeBussyResources,nodeRAM):
    for devId in G.nodes:
        mypercentageResources_ = float(nodeBussyResources[devId]) / float(nodeRAM[devId])
        deviceId = devId
        mykey_ = (deviceId, mypercentageResources_)
        if mykey_ in statisticsResources:
            statisticsResources[mykey_] = statisticsResources[mykey_] + 1
        else:
            statisticsResources[mykey_] = 1

# ****************************************************************************************************
# Generating application
# ****************************************************************************************************

def Generating_application(tt):
    numberOfServices = 0
    App1 = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 5), (2, 3), (2, 5), (2, 6), (2, 7)],
            [(0, 1), (1, 2), (1, 3), (1, 4), (2, 5), (3, 4), (3, 5), (4, 5), (5, 6)]
            ]

    """ Serviceset = [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14, 15], [16, 17, 18, 19, 20, 21, 22, 23],
                  [24, 25, 26, 27, 28, 29, 30, 31], [32, 33, 34, 35, 36, 37, 38, 39], [40, 41, 42, 43, 44, 45, 46,47],
                  [48,49,50,51,52,53,54,55],[56,57,58,59,60,61,62,63],[64,65,66,67,68,69,70,71], [72,73,74,75,76,77,78,79],
                  [80,81,82,83,84,85,86], [87,88,89,90,91,92,93], [94,95,96,97,98,99,100], [101,102,103,104,105,106,107],
                  [108,109,110,111,112,113,114],[115,116,117,118,119,120,121],[122,123,124,125,126,127,128],
                  [129,130,131,132,133,134,135],[136,137,138,139,140,141,142],[143,144,145,146,147,148,149]]"""
    sum = 0
    service = []
    Serviceset = []
    k=0
    for i in range(len(App1)):
        service = []
        if (k<1):
            for j in range(0, 8):
                service.append(sum)
                sum = sum + 1
        else:
            for j in range(0, 7):
                service.append(sum)
                sum = sum + 1
        Serviceset.append(service)
        k+=1


    """APP1_info = [{'id': 0, 'name': "Web-UI", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM': 2, 'MES_size': 0.5},
                 {'id': 1, 'name': "Login", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 2, 'name': "Orders", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 3, 'name': "Shopping-cart", 'cpu': {'core_num': 4}, 'inst(MI)': 400, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 0.5},
                 {'id': 4, 'name': "Catalogue", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 5, 'name': "Accounts", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 6, 'name': "Payment", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 7, 'name': "Shipping", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 0, 'name': "Web-UI", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM': 2, 'MES_size': 0.5},
                 {'id': 1, 'name': "Login", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 2, 'name': "Orders", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 3, 'name': "Shopping-cart", 'cpu': {'core_num': 4}, 'inst(MI)': 400, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 0.5},
                 {'id': 4, 'name': "Catalogue", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 5, 'name': "Accounts", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 6, 'name': "Payment", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 7, 'name': "Shipping", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 0, 'name': "Web-UI", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM': 2, 'MES_size': 0.5},
                 {'id': 1, 'name': "Login", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 2, 'name': "Orders", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 3, 'name': "Shopping-cart", 'cpu': {'core_num': 4}, 'inst(MI)': 400, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 0.5},
                 {'id': 4, 'name': "Catalogue", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 5, 'name': "Accounts", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 6, 'name': "Payment", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 7, 'name': "Shipping", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 0, 'name': "Web-UI", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 1, 'name': "Login", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 2, 'name': "Orders", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 3, 'name': "Shopping-cart", 'cpu': {'core_num': 4}, 'inst(MI)': 400, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 0.5},
                 {'id': 4, 'name': "Catalogue", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 5, 'name': "Accounts", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 6, 'name': "Payment", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 7, 'name': "Shipping", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 0, 'name': "Web-UI", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 1, 'name': "Login", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 2, 'name': "Orders", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 0.5},
                 {'id': 3, 'name': "Shopping-cart", 'cpu': {'core_num': 4}, 'inst(MI)': 400, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 0.5},
                 {'id': 4, 'name': "Catalogue", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 5, 'name': "Accounts", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 6, 'name': "Payment", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},
                 {'id': 7, 'name': "Shipping", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 0.5},

                 {'id': 0, 'name': "Encode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 2.5},
                 {'id': 1, 'name': "Frame", 'cpu': {'core_num': 4}, 'inst(MI)': 13500, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 2, 'name': "Low-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 3, 'name': "High-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 4, 'name': "High-accuracy-inference", 'cpu': {'core_num': 4}, 'inst(MI)': 3500, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 5, 'name': "Transcode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 6, 'name': "Package", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 0, 'name': "Encode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 2.5},
                 {'id': 1, 'name': "Frame", 'cpu': {'core_num': 4}, 'inst(MI)': 13500, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 2, 'name': "Low-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 3, 'name': "High-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 4, 'name': "High-accuracy-inference", 'cpu': {'core_num': 4}, 'inst(MI)': 3500, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 5, 'name': "Transcode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 6, 'name': "Package", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 0, 'name': "Encode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 2.5},
                 {'id': 1, 'name': "Frame", 'cpu': {'core_num': 4}, 'inst(MI)': 13500, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 2, 'name': "Low-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 3, 'name': "High-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 4, 'name': "High-accuracy-inference", 'cpu': {'core_num': 4}, 'inst(MI)': 3500, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 5, 'name': "Transcode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 6, 'name': "Package", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 0, 'name': "Encode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 2.5},
                 {'id': 1, 'name': "Frame", 'cpu': {'core_num': 4}, 'inst(MI)': 13500, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 2, 'name': "Low-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 3, 'name': "High-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 4, 'name': "High-accuracy-inference", 'cpu': {'core_num': 4}, 'inst(MI)': 3500, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 5, 'name': "Transcode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 6, 'name': "Package", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 0, 'name': "Encode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 2,
                  'RAM':2, 'MES_size': 2.5},
                 {'id': 1, 'name': "Frame", 'cpu': {'core_num': 4}, 'inst(MI)': 13500, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5},
                 {'id': 2, 'name': "Low-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 3, 'name': "High-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 4, 'name': "High-accuracy-inference", 'cpu': {'core_num': 4}, 'inst(MI)': 3500, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 5, 'name': "Transcode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0,
                  'storage': 1, 'RAM':1, 'MES_size': 5.5},
                 {'id': 6, 'name': "Package", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 0, 'storage': 1,
                  'RAM':1, 'MES_size': 5.5}
                 ]
"""
    APP1_info = [{'id': 0, 'name': "Web-UI", 'cpu': {'core_num': 4}, 'inst(MI)': 7610, 'deadline': 70, 'Avg-time': 0.046,
                  'requiredcpu': 7610, 'storage': 1,
                  'RAM': 2, 'MES_size': 0.5},
                 {'id': 1, 'name': "Login", 'cpu': {'core_num': 4}, 'inst(MI)': 7610, 'deadline': 50, 'Avg-time': 0.046,
                  'requiredcpu': 7610, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 2, 'name': "Orders", 'cpu': {'core_num': 4}, 'inst(MI)': 350, 'deadline': 50, 'Avg-time': 0.046,
                  'requiredcpu': 7610, 'storage': 2,
                  'RAM': 2, 'MES_size': 0.5},
                 {'id': 3, 'name': "Shopping-cart", 'cpu': {'core_num': 4}, 'inst(MI)': 100, 'deadline': 0,
                  'Avg-time': 0.052, 'requiredcpu': 7700,
                  'storage': 1, 'RAM': 1, 'MES_size': 0.5},
                 {'id': 4, 'name': "Catalogue", 'cpu': {'core_num': 4}, 'inst(MI)': 50, 'deadline': 0,
                  'Avg-time': 0.046, 'requiredcpu': 7610, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 5, 'name': "Accounts", 'cpu': {'core_num': 4}, 'inst(MI)': 50, 'deadline': 0,
                  'Avg-time': 0.046, 'requiredcpu': 7610, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 6, 'name': "Payment", 'cpu': {'core_num': 4}, 'inst(MI)': 100, 'deadline': 0, 'Avg-time': 0.046,
                  'requiredcpu': 7610, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},
                 {'id': 7, 'name': "Shipping", 'cpu': {'core_num': 4}, 'inst(MI)': 50, 'deadline': 0,
                  'Avg-time': 0.046, 'requiredcpu': 7610, 'storage': 1,
                  'RAM': 1, 'MES_size': 0.5},


                 {'id': 0, 'name': "Encode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 700, 'Avg-time': 0.34,
                  'requiredcpu': 17700, 'storage': 2,
                  'RAM': 2, 'MES_size': 2.5},
                 {'id': 1, 'name': "Frame", 'cpu': {'core_num': 4}, 'inst(MI)': 13500, 'deadline': 300, 'Avg-time': 0.57,
                  'requiredcpu': 24000, 'storage': 1,
                  'RAM': 1, 'MES_size': 5.5},
                 {'id': 2, 'name': "Low-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'Avg-time': 5000, 'requiredcpu': 7610,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 3, 'name': "High-accuracy-train", 'cpu': {'core_num': 4}, 'inst(MI)': 0, 'deadline': 0,
                  'Avg-time': 5000, 'requiredcpu': 7610,
                  'storage': 2, 'RAM': 4, 'MES_size': 5.5},
                 {'id': 4, 'name': "High-accuracy-inference", 'cpu': {'core_num': 4}, 'inst(MI)': 3500, 'deadline': 500,
                  'Avg-time': 0.3, 'requiredcpu': 12000,
                  'storage': 1, 'RAM': 1, 'MES_size': 5.5},
                 {'id': 5, 'name': "Transcode", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 700,
                  'Avg-time': 0.34, 'requiredcpu': 17700,
                  'storage': 1, 'RAM': 1, 'MES_size': 5.5},
                 {'id': 6, 'name': "Package", 'cpu': {'core_num': 4}, 'inst(MI)': 6000, 'deadline': 300, 'storage': 1,
                  'Avg-time': 0.34, 'requiredcpu': 17700,
                  'RAM': 1, 'MES_size': 5.5}]
    apps = list()
    appsDeadlines = {}
    appsResources = list()
    appsReqcpu = list()
    appstorage = list()
    appsSourceService = list()
    appsSourceMessage = list()
    appsTotalMIPS = list()
    mapService2App = list()
    mapServiceId2ServiceName = list()
    appsSourceMessage1 = list()
    mapService2App1 = list()
    mapServiceId2ServiceName1 = list()
    appsCommunities = list()
    service_name = list()
    service_inst = list()
    appJson = list()
    appJson1 = list()
    servicesResources = {}
    servicesStorage = {}
    servicesreqcpu = {}
    serviceTotalMIPS = {}
    service_in = {}
    service_out = {}
    APP11=[]
    for i in range(TOTALNUMBEROFAPPS):
        myApp = {}
        mylabels = {}

        APP = nx.DiGraph()
        #print(App1[i])
        APP.add_edges_from(App1[i])
        APP11.append(APP)
        for n in range(0, len(APP.nodes)):
            mylabels[n] = str(n)
        edgeList_ = list()
        for m in APP.edges:
            edgeList_.append(m)
        """"for m in edgeList_:
            APP.remove_edge(m[0], m[1])
            APP.add_edge(m[1], m[0])"""


        mapping = dict(zip(APP.nodes(), range(numberOfServices, numberOfServices + len(APP.nodes))))
        APP = nx.relabel_nodes(APP, mapping)


        numberOfServices = numberOfServices + len(APP.nodes)
        apps.append(APP)
        for j in APP.nodes:
            servicesResources[j] = APP1_info[j]['RAM']
            servicesStorage[j] = APP1_info[j]['storage']
            servicesreqcpu[j] = APP1_info[j]['requiredcpu']
            serviceTotalMIPS[j] = 0.0
            service_in[j] = 0.0
            service_out[j] = 0.0
        appsReqcpu.append(servicesreqcpu)
        appsResources.append(servicesResources)
        appstorage.append(servicesStorage)

        topologicorder_ = list(nx.topological_sort(APP))
        source = topologicorder_[0]
        source=Serviceset[i][0]

        #appsCommunities.append(transitiveClosureCalculation(source, APP))
        #transitiveClosureCalculation(source, APP)

        appsSourceService.append(source)
        #print("source", appsSourceService)
        appsDeadlines[i] = APPDEADLINE[i]
        myApp['id'] = i
        myApp['name'] = str(i)
        myApp['deadline'] = appsDeadlines[i]

        myApp['module'] = list()

        edgeNumber = 0
        myApp['message'] = list()

        myApp['transmission'] = list()

        totalMIPS = 0
        SERVICEINSTR1 = []
        SERVICEMESSAGESIZE1 = []

        for n in APP.nodes:

            mapService2App.append(str(i))
            mapServiceId2ServiceName.append(str(i) + '_' + str(n))
            myNode = {}
            myNode['id'] = n
            myNode['name'] = str(i) + '_' + str(n)
            myNode['RAM'] = servicesResources[n]
            myNode['storage'] = servicesStorage[n]
            myNode['type'] = 'MODULE'
            myNode['INST'] = APP1_info[n]['inst(MI)']
            myNode['requiredcpu'] = APP1_info[n]['requiredcpu']


            if source == n:
                myEdge = {}
                myEdge['id'] = edgeNumber
                edgeNumber = edgeNumber + 1
                myEdge['name'] = "M.USER.APP." + str(i)
                myEdge['s'] = "None"
                myEdge['d'] = str(i) + '_' + str(n)


                #myEdge['reqcpu'] = APP1_info[n]['requiredcpu']
                myEdge['instructions'] = APP1_info[n]['inst(MI)']
                SERVICEINSTR1.append(myEdge['instructions'])
                myEdge['instructions'] = myNode['INST']
                totalMIPS = totalMIPS + myEdge['instructions']
                myEdge['bytes'] = APP1_info[n]['MES_size']
                SERVICEMESSAGESIZE1.append(myEdge['bytes'])
                myApp['message'].append(myEdge)
                appsSourceMessage.append(myEdge)

                for o in APP.edges:
                    if o[0] == source:
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(source)
                        myTransmission['message_in'] = "M.USER.APP." + str(i)
                        myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                        myApp['transmission'].append(myTransmission)

            myApp['module'].append(myNode)

        for n in APP.edges:
            myEdge = {}
            myEdge['id'] = edgeNumber
            edgeNumber = edgeNumber + 1
            myEdge['name'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
            myEdge['s'] = str(i) + '_' + str(n[0])
            myEdge['d'] = str(i) + '_' + str(n[1])

            #myEdge['reqcpu'] = APP1_info[n]['requiredcpu']
            myEdge['instructions'] = APP1_info[n[0]]['inst(MI)']
            SERVICEINSTR1.append(myEdge['instructions'])
            totalMIPS = totalMIPS + myEdge['instructions']
            myEdge['bytes'] = APP1_info[n[0]]['MES_size']
            SERVICEMESSAGESIZE1.append(myEdge['bytes'])
            myApp['message'].append(myEdge)
            destNode = n[1]
            for o in APP.edges:
                if o[0] == destNode:
                    myTransmission = {}
                    myTransmission['module'] = str(i) + '_' + str(n[1])
                    myTransmission['message_in'] = str(i) + '_(' + str(n[0]) + "-" + str(n[1]) + ")"
                    myTransmission['message_out'] = str(i) + '_(' + str(o[0]) + "-" + str(o[1]) + ")"
                    myApp['transmission'].append(myTransmission)

        for n in APP.nodes:
            outgoingEdges = False
            for m in APP.edges:
                if m[0] == n:
                    outgoingEdges = True
                    break
            if not outgoingEdges:
                for m in APP.edges:
                    if m[1] == n:
                        myTransmission = {}
                        myTransmission['module'] = str(i) + '_' + str(n)
                        myTransmission['message_in'] = str(i) + '_(' + str(m[0]) + "-" + str(m[1]) + ")"
                        myApp['transmission'].append(myTransmission)
        appsTotalMIPS.append(totalMIPS)
        myApp['appsTotalMIPS'] = totalMIPS

        messages = myApp['message']
        modules = myApp['module']
        for n in range(len(messages)):
            service_name.append(messages[n]['d'])
            service_inst.append(messages[n]['instructions'])
        for j in range(len(modules)):
            for n in range(len(service_name)):
                if service_name[n] == modules[j]['name']:
                    modules[j]['INST'] = modules[j]['INST'] + service_inst[n]
            myApp['module'][j]['INST'] = modules[j]['INST']

        appJson.append(myApp)


        app_file = "appDefinition" + str(tt) + ".json"
        file = open(app_file, "w")
        file.write(json.dumps(appJson))
        file.close()



    return numberOfServices, Serviceset, appsDeadlines, appsSourceMessage, mapService2App, mapServiceId2ServiceName


def weightNetwork(appsSourceMessage,appId, G):
    size = float(appsSourceMessage[appId]['bytes'])
    for e in G.edges:
        G[e[0]][e[1]]['weight'] = float(G[e[0]][e[1]]['PR']) + (size / float(G[e[0]][e[1]]['BW']))


def comm_attribute1(Fog_resources, partitions, network_size):
    cpu_core = []
    cpu_cache = []
    cpu_speed = []
    storage = []
    RAM = []
    flag = []
    community_info = []


    for nodes in range(network_size):
        flag.append('false')


    for i in range(len(partitions)):
        for j in range(len(partitions[i])):
            sum_cpu_core = 0
            sum_cpu_cache = 0
            sum_cpu_speed = 0
            sum_storage = 0
            sum_ram = 0
            comm_node = 0
            comm_member = []

            for nodes in range(network_size):
                flag[nodes] = 'false'
            for k in range(len(partitions[i][j])):
                #print(partitions[i][j][k])
                d = partitions[i][j][k] % network_size
                #print(partitions[i][j][k])
                if (flag[d] == 'false'):
                    comm_node = comm_node + 1
                    comm_member.append(d)
                    print(Fog_resources)
                    sum_cpu_core = Fog_resources[d]['cpu']['core_num'] + sum_cpu_core
                    sum_cpu_cache = Fog_resources[d]['cpu']['cache'] + sum_cpu_cache
                    sum_cpu_speed = Fog_resources[d]['cpu']['speed'] + sum_cpu_speed
                    sum_storage = Fog_resources[d]['storage'] + sum_storage
                    sum_ram = Fog_resources[d]['RAM'] + sum_ram
                    flag[d] = 'true'

            cpu_core.append(sum_cpu_core / comm_node)
            cpu_cache.append(sum_cpu_cache / comm_node)
            cpu_speed.append(sum_cpu_speed / comm_node)
            storage.append(sum_storage / comm_node)
            RAM.append(sum_ram / comm_node)
            community_info.append({'Id': j, 'member': comm_member,
                                   'cpu': {'core_num': cpu_core[j], 'cache': cpu_cache[j], 'speed': cpu_speed[j]},
                                   'RAM': RAM[j], 'storage': storage[j]})

    return community_info


# ****************************************************************************************************

# Second-level #Placement (services to devices) using communities

# ****************************************************************************************************
def nettime(G,Fog_community):
    clientId= 60
    print("calculating the nettime")
    delay=[]
    sorted_list=[]

    for j in range(len(Fog_community)):

            device_id = Fog_community[j]['member']
            netTime = {}
            for devId in device_id:
                if nx.has_path(G, source=clientId, target=devId) == True:
                        netTime[devId] = nx.shortest_path_length(G, source=clientId, target=devId,
                                                                 weight="weight")  # network time between client and device
                else:

                    netTime[devId] = 10000000000

            sorted_ = sorted(netTime.items(), key=operator.itemgetter(1))
            sorted_list.append(sorted_)
            #sortedList = list()

            """for i in sorted_:
                sortedList.append(i[1])"""
            sortedList = sorted_[0][1]
            delay.append(1 / (1 + sortedList))
    return delay, sorted_list

def sim_com_module(G, Fog_community, delay ,requiredcpu, requiredRAM, requiredStrorage, pre_device, A, clientId):
    sim = []
    #print("calculating the similarity")
    #Delays of community for specific client which is an array
    """if clientId<750:
        delay=Delay[0]
    elif clientId > 749 and clientId <800:
        delay=Delay[1]
    elif clientId > 799 and clientId <850:
        delay=Delay[2]"""

    for j in range(len(Fog_community)):
        simRAM = Similaritymeasurment.Euclidean_similarity(
            [requiredRAM], [Fog_community[j]['RAM']])
        simCPU = Similaritymeasurment.Euclidean_similarity(
            [requiredcpu], [Fog_community[j]['cpu']['speed']])
        simStorage = Similaritymeasurment.Euclidean_similarity(
            [requiredStrorage] , [Fog_community[j]['storage']])
        sim.append(simRAM + simCPU + simStorage)
        sim[j] = A * sim[j] + (1 / math.sqrt(A)) * delay[j]

    return sim


def check_res(requiredcpu, requiredStrorage, requiredRAM, available_Storage, available_RAM, available_CPUCore):
    allocating = False
    if (available_RAM >= requiredRAM):
        if (available_Storage >= requiredStrorage):
            if (available_CPUCore >= 1):
                allocating = True

    return allocating


def map_com_NF(G, comm,sortnettime,comm_id, requiredcpu, requiredRAM, requiredStrorage, clientId, available_Storage, available_RAM,
            available_CPUCore):
    mapped = -1

    sortedList = list()
    sorted_ = sortnettime[comm_id]
    for i in sorted_:
        sortedList.append(i[0])

    for i in sortedList:
            device_id = i
            allocat = check_res(requiredcpu, requiredStrorage, requiredRAM, available_Storage[device_id],
                                available_RAM[device_id], available_CPUCore[device_id])
            if (allocat):

                mapped = device_id
                break

    return mapped

def map_com(G, comm,sortnettime,comm_id,topo_mem, SLAPar_info, requiredcpu, requiredRAM, requiredStrorage, clientId, available_Storage, available_RAM,
            available_CPUCore):
    mapped = -1


    sortedList = list()
    sorted_ = sortnettime[comm_id]
    for i in sorted_:
        sortedList.append(i[0])
    for i in sortedList:
        topo_id = topo_mem[i]
        for SP in range(len(SLAPar_info[topo_id])):
               if SLAPar_info[topo_id][SP]['SLAValue']> 0.6:
                mem=SLAPar_info[topo_id][SP]['member']
                netTime = {}
                for devId in mem:
                    if nx.has_path(G, source=clientId, target=devId) == True:
                        netTime[devId] = nx.shortest_path_length(G, source=clientId, target=devId,
                                                                 weight="weight")  # network time between client and device
                    else:
                        netTime[devId] = -1
                        print("There is no path from device ", devId, "to device", clientId)
                sortedmem = sorted(netTime.items(), key=operator.itemgetter(1))
                sortedmemList=list()
                for i in sortedmem:
                    sortedmemList.append(i[0])
                for i in sortedmemList:
                        device_id = i
                        if netTime[i] != -1:
                            allocat = check_res(requiredcpu, requiredStrorage, requiredRAM, available_Storage[device_id],
                                                available_RAM[device_id], available_CPUCore[device_id])
                            if (allocat):
                                mapped = device_id
                                return mapped

    return mapped
def map_com_SOTA(G, comm,sortnettime,comm_id,topo_mem, SLA_info, requiredcpu, requiredRAM, requiredStrorage, clientId, available_Storage, available_RAM,
            available_CPUCore):
    mapped = -1


    sortedList = list()
    sorted_ = sortnettime[comm_id]
    for i in sorted_:
        sortedList.append(i[0])
    id=[]
    for device_id in sortedList:

        for d in range(len(SLA_info)):
            id.append(SLA_info[d]['id'])
        if device_id in id:
            allocat = check_res(requiredcpu, requiredStrorage, requiredRAM, available_Storage[device_id],
                                available_RAM[device_id], available_CPUCore[device_id])
            if (allocat):
                mapped = device_id
                return mapped
    return mapped


def comm_update(device_id,Fog_resources, community):
    updated_mem = []
    updated_info = []
    node_num = len(community['member'])
    com_mem = community['member']
    for i in range(len(community['member'])):
        if (com_mem[i] != device_id):
            updated_mem.append(com_mem[i])

    sum_cpu_core = community['cpu']['core_num'] * node_num
    sum_cpu_cache = community['cpu']['cache'] * node_num
    sum_cpu_speed = community['cpu']['speed'] * node_num
    sum_up_bw = community['network']['up_Bw'] * node_num
    sum_down_bw = community['network']['down_Bw'] * node_num
    sum_storage = community['storage'] * node_num
    sum_ram = community['RAM'] * node_num

    cpu_core = (sum_cpu_core - Fog_resources[device_id]['cpu']['core_num']) / (node_num - 1)
    cpu_cache = (sum_cpu_cache - Fog_resources[device_id]['cpu']['cache']) / (node_num - 1)
    cpu_speed = (sum_cpu_speed - Fog_resources[device_id]['cpu']['speed']) / (node_num - 1)
    up_bw = (sum_up_bw - Fog_resources[device_id]['network']['up_Bw']) / (node_num - 1)
    down_bw = (sum_down_bw - Fog_resources[device_id]['network']['down_Bw']) / (node_num - 1)
    storage = (sum_storage - Fog_resources[device_id]['storage']) / (node_num - 1)
    RAM = (sum_ram - Fog_resources[device_id]['RAM']) / (node_num - 1)

    updated_info.append(
        {'Id': community['Id'], 'member': updated_mem,
         'cpu': {'core_num': cpu_core, 'cache': cpu_cache, 'speed': cpu_speed},
         'network': {'up_Bw': up_bw, 'down_Bw': down_bw}, 'RAM': RAM})

    return updated_info


def topo_comm_tag(device, Fog_comm, topo_com):
    device_tags = []
    topo_num = np.zeros(len(Fog_comm))
    topology_inf = []
    sorted_topo_inf = []
    for k in range(len(device)):
        for i in range(len(Fog_comm)):
            if (i >= topo_com[0]):

                for j in range(len(Fog_comm[i]['member'])):
                    if (Fog_comm[i]['member'][j] == device[k]['device_id']):
                        topo_tag = i
                        device_tags.append(
                            {'device_id': device[k]['device_id'], 'feat_comm_id': device[k]['community_Id'],
                             'topo_comm_id': topo_tag})
                        topo_num[i] = topo_num[i] + 1

    for i in range(len(Fog_comm)):
        topology_inf.append({'topo_com_id': i, 'count': topo_num[i]})

    for sorted_inf in sorted(topology_inf, key=operator.itemgetter("count"), reverse=True):
        sorted_topo_inf.append(sorted_inf)

    return device_tags


# ****************************************************************************************************
# Generation of IoT devices (users) that request each application
# ****************************************************************************************************

def request_generation(t, gatewaysDevices):
    userJson = {}
    myUsers = list()
    appsRequests = list()

    for i in range(0, TOTALNUMBEROFAPPS):
        userRequestList = set()
        probOfRequested = eval(func_REQUESTPROB)
        for j in gatewaysDevices:
            if random.random() < probOfRequested:
                myOneUser = {}
                myOneUser['app'] = str(i)
                myOneUser['message'] = "M.USER.APP." + str(i)
                myOneUser['id_resource'] = j
                myOneUser['lambda'] = eval(func_USERREQRAT)
                userRequestList.add(j)
                myUsers.append(myOneUser)
        appsRequests.append(userRequestList)

    userJson['sources'] = myUsers
    req_file = "usersDefinition" + str(t) + ".json"
    file = open(req_file, "w")
    file.write(json.dumps(userJson))
    file.close()
    return appsRequests, myUsers



# ****************************************************************************************************

# PROS placement

# ****************************************************************************************************

def SLA_aware_placement(tt,G,Delay,sortnettime,devices,topo_mem,topo_par,Fog_community,SLAPar_info,gatewaysDevices,centralityValuesNoOrdered, numberOfServices, service_set,appsDeadlines, appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests):
    FOG_DEVICES = []
    with open("networkDefinition.json", "r") as json_file:
        content = json.load(json_file)
    Fog_resources = content['entity']
    network_size = (len(Fog_resources)) - 1
    FOG_DEVICES.append(Fog_resources)
    available_cpu_speed = {}
    available_Storage = {}
    available_CPUCore = {}
    available_RAM = {}
    nodeBussy_cpu_speed = {}
    nodeBussy_RAM = {}

    for device_id in range(network_size):
        nodeBussy_cpu_speed[device_id] = 0.0
        nodeBussy_RAM[device_id] = 0.0
        available_cpu_speed[device_id] = (Fog_resources[device_id]['cpu']['speed'])
        available_RAM[device_id] = Fog_resources[device_id]['RAM']
        available_Storage[device_id] = Fog_resources[device_id]['storage']
        available_CPUCore[device_id] = Fog_resources[device_id]['cpu']['core_num']


    service2DevicePlacementMatrix = [[0 for j in range(len(G.nodes))] for i in range(numberOfServices)]

    nodeBussyResources = {}
    for i in G.nodes:
        nodeBussyResources[i] = 0.0

    nodeBussyStorage = {}
    for i in G.nodes:
        nodeBussyStorage[i] = 0.0

    nodeBussyCore = {}
    for i in G.nodes:
        nodeBussyCore[i] = 0.0
    app_file = "appDefinition0.json"

    with open(app_file, "r") as json_file:
        content_app = json.load(json_file)
    sortedAppsDeadlines = sorted(appsDeadlines.items(), key=operator.itemgetter(1))
    print("Starting SLA-aware placement policy in time window", tt, " .....")
    App_num = 0
    Service_num = 0
    App_req_num = 0
    cpu_usage = 0.0
    #t = time.time()

    for appToAllocate in sortedAppsDeadlines:
        App_num = App_num + 1
        appId = appToAllocate[0]
        weightNetwork(appsSourceMessage,appId, G)
        nodesWithClients = appsRequests[appId]
        #print("it is placing the app", appId)
        for clientId in nodesWithClients:
            App_req_num = App_req_num + 1
            requiredStrorage1 = 0.0
            requiredRAM1 = 0.0
            requiredcpu1 = 0.0
            alloc_devices = []
            serset_id = 0
            device_id = -1

            modules = content_app[appId]['module']
            App_deadline = content_app[appId]['deadline']
            A = App_deadline / 10000
            App_size = (len(modules))  # the number of modules in one app
            tempServiceAlloc = {}
            for i in range(App_size):
                #requiredcpu1 = requiredcpu1 + modules[i]['requiredcpu']
                requiredcpu1 = requiredcpu1 + modules[i]['requiredcpu']
                requiredStrorage1 = requiredStrorage1 + modules[i]['storage']
                requiredRAM1 = requiredRAM1 + modules[i]['RAM']
                Service_num = Service_num + 1
            ser_id = 0
            for serviceSet in service_set[appId]:
                requiredStrorage = 0.0
                requiredRAM = 0.0
                requiredcpu = 0.0
                #requiredcpu = requiredcpu + modules[ser_id]['INST']
                requiredcpu = requiredcpu + modules[ser_id]['requiredcpu']
                requiredStrorage = requiredStrorage + modules[ser_id]['storage']
                requiredRAM = requiredRAM + modules[ser_id]['RAM']
                ser_id = ser_id + 1


                if (device_id != -1):
                    placed = check_res(requiredcpu, requiredStrorage, requiredRAM, available_Storage[device_id],
                                       available_RAM[device_id], available_CPUCore[device_id])
                    if (placed):
                        alloc_devices.append({'device_id': device_id, 'community_Id': comm_id})
                        tempServiceAlloc[serviceSet] = device_id
                        service2DevicePlacementMatrix[serviceSet][device_id] = 1
                        Overload = False
                        nodeBussy_cpu_speed[device_id] = nodeBussy_cpu_speed[device_id] + requiredcpu
                        nodeBussy_RAM[device_id] = nodeBussy_RAM[device_id] + requiredRAM
                        nodeBussyResources[device_id] = nodeBussyResources[device_id] + requiredRAM
                        nodeBussyStorage[device_id] = nodeBussyStorage[device_id] + requiredStrorage
                        nodeBussyCore[device_id] = nodeBussyCore[device_id] + 1
                        available_RAM[device_id] = available_RAM[device_id] - requiredRAM
                        available_Storage[device_id] = available_Storage[device_id] - requiredStrorage
                        available_CPUCore[device_id] = available_CPUCore[device_id] - 1
                        serset_id = serset_id + 1
                        requiredcpu1 = requiredcpu1 - requiredcpu
                        requiredStrorage1 = requiredStrorage1 - requiredStrorage
                        requiredRAM1 = requiredRAM1 - requiredRAM
                    else:
                        similarity = sim_com_module(G,Fog_community, Delay,requiredcpu, requiredRAM, requiredStrorage,
                                                    device_id, A, clientId)
                        community = []
                        sorted_comm = []

                        for j in range(len(Fog_community)):
                            community.append({'comm_id': j, 'sim_value': similarity[j]})

                        for sorted_com in sorted(community, key=operator.itemgetter("sim_value"), reverse=True):
                            sorted_comm.append(sorted_com)

                        for j in range(len(sorted_comm)):
                            comm_id = sorted_comm[j]['comm_id']
                            overlapp = True

                            if (overlapp):

                                device_id = map_com(G, Fog_community[comm_id],sortnettime,comm_id,topo_mem, SLAPar_info, requiredcpu, requiredRAM, requiredStrorage,
                                                clientId, available_Storage, available_RAM, available_CPUCore)
                                # after finishing the task every thing (used fog node) should come back to it's first step before updatathing
                                if (device_id != -1):
                                    alloc_devices.append({'device_id': device_id, 'community_Id': comm_id})

                                    if (serset_id == 0):
                                        topology_com_id0 = topo_mem[device_id]
                                        service2DevicePlacementMatrix[serviceSet][device_id] = 1
                                        tempServiceAlloc[serviceSet] = device_id
                                        nodeBussy_RAM[device_id] = nodeBussy_RAM[device_id] + requiredRAM
                                        nodeBussyResources[device_id] = nodeBussyResources[device_id] + requiredRAM
                                        nodeBussyStorage[device_id] = nodeBussyStorage[device_id] + requiredStrorage
                                        nodeBussyCore[device_id] = nodeBussyCore[device_id] + 1
                                        available_RAM[device_id] = available_RAM[device_id] - requiredRAM
                                        available_Storage[device_id] = available_Storage[device_id] - requiredStrorage
                                        available_CPUCore[device_id] = available_CPUCore[device_id] - 1
                                        serset_id = serset_id + 1
                                        requiredcpu1 = requiredcpu1 - requiredcpu
                                        requiredStrorage1 = requiredStrorage1 - requiredStrorage
                                        requiredRAM1 = requiredRAM1 - requiredRAM
                                        break
                                    else:
                                        topology_com_id1 = topo_mem[device_id]
                                        if (topology_com_id1 == topology_com_id0):
                                            service2DevicePlacementMatrix[serviceSet][device_id] = 1
                                            tempServiceAlloc[serviceSet] = device_id
                                            nodeBussy_cpu_speed[device_id] = nodeBussy_cpu_speed[
                                                                                 device_id] + requiredcpu
                                            nodeBussy_RAM[device_id] = nodeBussy_RAM[device_id] + requiredRAM
                                            nodeBussyResources[device_id] = nodeBussyResources[device_id] + requiredRAM
                                            nodeBussyStorage[device_id] = nodeBussyStorage[device_id] + requiredStrorage
                                            nodeBussyCore[device_id] = nodeBussyCore[device_id] + 1
                                            available_RAM[device_id] = available_RAM[device_id] - requiredRAM
                                            available_Storage[device_id] = available_Storage[
                                                                               device_id] - requiredStrorage
                                            available_CPUCore[device_id] = available_CPUCore[device_id] - 1
                                            serset_id = serset_id + 1
                                            requiredcpu1 = requiredcpu1 - requiredcpu
                                            requiredStrorage1 = requiredStrorage1 - requiredStrorage
                                            requiredRAM1 = requiredRAM1 - requiredRAM
                                            break
                else:
                    similarity = sim_com_module(G, Fog_community,Delay, requiredcpu, requiredRAM, requiredStrorage, device_id,
                                                A, clientId)
                    community = []
                    sorted_comm = []

                    for j in range(len(Fog_community)):
                        community.append({'comm_id': j, 'sim_value': similarity[j]})
                    for sorted_com in sorted(community, key=operator.itemgetter("sim_value"), reverse=True):
                        sorted_comm.append(sorted_com)

                    for j in range(len(sorted_comm)):
                        comm_id = sorted_comm[j]['comm_id']
                        overlapp = True

                        if (overlapp):

                            device_id = map_com(G, Fog_community[comm_id],sortnettime,comm_id,topo_mem, SLAPar_info, requiredcpu, requiredRAM, requiredStrorage,
                                                clientId, available_Storage, available_RAM, available_CPUCore)

                            if (device_id != -1):
                                alloc_devices.append({'device_id': device_id, 'community_Id': comm_id})

                                if (serset_id == 0):
                                    topology_com_id0 = topo_mem[device_id]
                                    tempServiceAlloc[serviceSet] = device_id
                                    service2DevicePlacementMatrix[serviceSet][device_id] = 1
                                    nodeBussy_RAM[device_id] = nodeBussy_RAM[device_id] + requiredRAM
                                    nodeBussyResources[device_id] = nodeBussyResources[device_id] + requiredRAM
                                    nodeBussyStorage[device_id] = nodeBussyStorage[device_id] + requiredStrorage
                                    nodeBussyCore[device_id] = nodeBussyCore[device_id] + 1
                                    available_RAM[device_id] = available_RAM[device_id] - requiredRAM
                                    available_Storage[device_id] = available_Storage[device_id] - requiredStrorage
                                    available_CPUCore[device_id] = available_CPUCore[device_id] - 1
                                    serset_id = serset_id + 1
                                    requiredcpu1 = requiredcpu1 - requiredcpu
                                    requiredStrorage1 = requiredStrorage1 - requiredStrorage
                                    requiredRAM1 = requiredRAM1 - requiredRAM
                                    break
                                else:
                                    topology_com_id1 = topo_mem[device_id]
                                    if (topology_com_id1 == topology_com_id0):
                                        tempServiceAlloc[serviceSet] = device_id
                                        service2DevicePlacementMatrix[serviceSet][device_id] = 1
                                        nodeBussy_cpu_speed[device_id] = nodeBussy_cpu_speed[device_id] + requiredcpu
                                        nodeBussy_RAM[device_id] = nodeBussy_RAM[device_id] + requiredRAM
                                        nodeBussyResources[device_id] = nodeBussyResources[device_id] + requiredRAM
                                        nodeBussyStorage[device_id] = nodeBussyStorage[device_id] + requiredStrorage
                                        nodeBussyCore[device_id] = nodeBussyCore[device_id] + 1
                                        available_RAM[device_id] = available_RAM[device_id] - requiredRAM
                                        available_Storage[device_id] = available_Storage[device_id] - requiredStrorage
                                        available_CPUCore[device_id] = available_CPUCore[device_id] - 1
                                        serset_id = serset_id + 1
                                        requiredcpu1 = requiredcpu1 - requiredcpu
                                        requiredStrorage1 = requiredStrorage1 - requiredStrorage
                                        requiredRAM1 = requiredRAM1 - requiredRAM
                                        break

            writeStatisticsAllocation(G,appsDeadlines,tempServiceAlloc, clientId, appId)

    # ***********************************************************************************************************************

