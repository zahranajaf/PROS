import json
import math
import operator
import igraph as ig
import louvain
import networkx as nx
import matplotlib.pyplot as plt

import SLA_aware_placement
import louvain_ext
import random
import numpy as np
from SLAassessment import SLACalculation
import Similaritymeasurment
from TSLA import TSLA_cal

CLOUDRAM = 32
CLOUDSTORAGE = 99999999999999
CLOUDSPEED = 100000  # INSTR x MS
CLOUD_CPU_CACHE = 99999999
CLOUD_UP_BANDWITDH = 5000  # BYTES / MS --> 40 Mbits/s
CLOUD_DOWN_BANDWITDH = 5000  # MS
CLOUDBW = 5000
CLOUDPR = 125

# NETWORK
PERCENTATGEOFGATEWAYS = 0.25
func_PROPAGATIONTIME = "random.randint(1,7)"  # MS
func_BANDWITDH = "random.randint(30000,110000)"  # BYTES / MS
func_NETWORKGENERATION = "nx.barabasi_albert_graph(n=200, m=1)"  # algorithm for the generation of the network topology
func_NODERAM = "random.randint(2,16)"  # MB RAM #random distribution for the resources of the fog devices
func_NODESTORAGE = "random.randint(64,256)"  # random distribution for the resources of the fog devices
func_CPU_Core = "random.randint(2,8)"
func_NODESPEED = "random.randint(10000,40000)"  # INTS / MS #random distribution for the speed of the fog devices

# APP and SERVICES
TOTALNUMBEROFAPPS =10
func_APPGENERATION = "nx.gn_graph(random.randint(2,10))"
func_SERVICEINSTR = "random.randint(100,500)"  # INSTR --> taking into account node speed this gives us between 200 and 600 MS
func_SERVICEMESSAGESIZE = "random.randint(1500000,4500000)"  # BYTES and taking into account net bandwidth it gives us between 20 and 60 MS
func_SERVICERAM = "random.randint(1,7)"  # MB of RAM consumed by the service, taking into account noderesources and appgeneration we have to fit approx 1 app per node or about 10 services
func_STORAGE = "random.randint(1,7)"
#func_APPDEADLINE = "random.randint(50,2000)"  # MS

# USERS and IoT DEVICES
func_REQUESTPROB = "random.random()/8"  # Popularidad de la app. threshold que determina la probabilidad de que un dispositivo tenga asociado peticiones a una app. tle threshold es para cada ap
func_USERREQRAT = "random.randint(10,100)"  # MS
pathSimple = "./scenariot/"

# SLA parameters
func_AcceptPar = "random.randint(0,1800)"
func_AcceptPar1 = "random.randint(1100,1800)"
#func_vioAcceptance = "random.randint(0,180)"
func_vioAcceptance = 1800
func_vioSuccessPar="random.randint(0,1800)"
func_vioSuccessPar1="random.randint(1100,1800)"
# fun_SuccessPar="random.randint(1,30)"
# fun_SatiPar="random.randint(1,30)"
random.seed(8)
verbose_log = False
ILPoptimization = True
generatePlots = True
graphicTerminal = True

devices = list()
devices1 = list()
nodeRAM = {}
CPUCore = {}
nodeSTORAGE = {}
SumRAM = 0.0
SumStorage = 0.0
SumCore = 0.0
cloudId = 1000
nodeFreeResources = {}
nodeSpeed = {}
nodelat = {}
nodelong = {}
mylabels = {}


# initializing the Network

devices = list()
devices1 = list()
Device_ifo=[{'id': 0, 'name':"City-D_Large", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000},'storage': 10,'RAM': 8},
            {'id': 1, 'name':"City-D_Medium",'IPT': 7200, 'cpu': {'core_num': 2, 'cache': 4, 'speed': 7200},'storage': 10, 'RAM': 4},
            {'id': 2, 'name':"City-D_Small",'IPT': 7100, 'cpu': {'core_num': 2, 'cache': 4, 'speed': 7100},'storage': 10,'RAM': 2},
            {'id': 3, 'name':"City-B", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000},'storage': 10,'RAM': 8},
            {'id': 4, 'name':"City-C", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000},'storage': 10,'RAM': 8},
            {'id': 5, 'name':"City-F", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000},'storage': 10,'RAM': 8},
            {'id': 6, 'name':"City-G", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000},'storage': 10,'RAM': 8},
            {'id': 7,'name':"City-E", 'IPT': 12000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 12000},'storage': 10,'RAM': 8},
            {'id': 8,'name':"City-E-Large", 'IPT': 58000, 'cpu': {'core_num': 12, 'cache': 4, 'speed': 58000},'storage': 32,'RAM': 32},
            {'id': 9,'name':"City-E-Medium", 'IPT': 21700, 'cpu': {'core_num': 8, 'cache': 4, 'speed': 21700},'storage': 32,'RAM': 16},
            {'id': 10,'name':"Jetson", 'IPT': 4080, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 4080},'storage': 64,'RAM': 4},
            {'id': 11,'name':"RPi4", 'IPT': 5100, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 5100}, 'storage': 64,'RAM': 4},
            {'id': 12,'name':"City-A_Large", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000},'storage': 10,'RAM': 8}]
cloud_info= [{'id': 1,'name':"City-A_Large", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000}, 'storage': 10,'RAM': 8}]

res_num=[{'id': 0, 'num':20},{'id': 1, 'num':20},{'id': 2, 'num':20},{'id': 3, 'num':60},{'id': 4, 'num':60},{'id': 5, 'num':90},{'id': 6, 'num':60},{'id': 7, 'num':60},{'id': 8, 'num':40},{'id': 9, 'num':40}, {'id': 10, 'num':5}, {'id': 11, 'num':40}, {'id': 12, 'num':90}]

netMatrix= [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),(0, 10),(0, 11),(0, 12),
            (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),(1, 10),(1, 11),(1, 12),
            (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9),(2, 10),(2, 11),(2, 12),
            (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9),(3, 10),(3, 11),(3, 12),
            (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),(4, 10),(4, 11),(4, 12),
            (5, 6), (5, 7), (5, 8), (5, 9),(5, 10),(5, 11),(5, 12),
            (6, 7), (6, 8), (6, 9),(6, 10),(6, 11),(6, 12),
            (7, 8), (7, 9),(7, 10),(7, 11),(7, 12),
            (8, 9),(8, 10),(8, 11),(8, 12),
            (9, 10),(9, 11),(9, 12),
            (10, 11),(10, 12),
            (11, 12),
]
net_info=[[{'sourceID':0,'desID':1, 'S_name':"City-D_Medium", 'D_name':"City-D_Small", 'bandwidth':13000, 'latency': 0.5}, {'sourceID':0,'desID':2, 'S_name':"City-D_Medium", 'D_name':"City-D_Tiny", 'bandwidth':13000, 'latency': 0.5},{'sourceID':0,'desID':3, 'S_name':"City-D_Medium", 'D_name':"City-B_Medium", 'bandwidth':1950, 'latency': 12.5},{'sourceID':0,'desID':4, 'S_name':"City-D_Medium", 'D_name':"MUC_Medium", 'bandwidth':3000, 'latency': 7.3},{'sourceID':0,'desID':5, 'S_name':"City-D_Medium", 'D_name':"GEN_Medium", 'bandwidth':1500, 'latency': 16.5},{'sourceID':0,'desID':6, 'S_name':"City-D_Medium", 'D_name':"FRA_Medium", 'bandwidth':1600, 'latency': 12.5},{'sourceID':0,'desID':7, 'S_name':"City-D_Medium", 'D_name':"City-E", 'bandwidth':5000, 'latency': 4.8}, {'sourceID':0,'desID':8, 'S_name':"City-D_Medium", 'D_name':"City-E-Large", 'bandwidth':950, 'latency': 7.2}, {'sourceID':0,'desID':9, 'S_name':"City-D_Medium", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 7.2}, {'sourceID':0,'desID':10, 'S_name':"City-D_Medium", 'D_name':"Jetson", 'bandwidth':900, 'latency': 7.5}, {'sourceID':0,'desID':11, 'S_name':"City-D_Medium", 'D_name':"RPi4", 'bandwidth':900, 'latency': 7.5}, {'sourceID':0,'desID':12, 'D_name':"City-A_Large", 'S_name':"City-D_Medium", 'bandwidth':1500, 'latency': 15}],
                                                                                                                      [{'sourceID':1,'desID':2, 'S_name':"City-D_Small", 'D_name':"City-D_Tiny", 'bandwidth':13000, 'latency': 0.5},{'sourceID':1,'desID':3, 'S_name':"City-D_Small", 'D_name':"City-B_Medium", 'bandwidth':1950, 'latency': 12.5},{'sourceID':1,'desID':4, 'S_name':"City-D_Small", 'D_name':"MUC_Medium", 'bandwidth':3000, 'latency': 7.3},{'sourceID':1,'desID':5, 'S_name':"City-D_Small", 'D_name':"GEN_Medium", 'bandwidth':1500, 'latency': 16.5},{'sourceID':1,'desID':6, 'S_name':"City-D_Small", 'D_name':"FRA_Medium", 'bandwidth':1600, 'latency': 12.5},{'sourceID':1,'desID':7, 'S_name':"City-D_Small", 'D_name':"City-E", 'bandwidth':5000, 'latency': 4.8}, {'sourceID':1,'desID':8, 'S_name':"City-D_Small", 'D_name':"City-E-Large", 'bandwidth':950, 'latency': 7.2}, {'sourceID':1,'desID':9, 'S_name':"City-D_Small", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 7.2}, {'sourceID':1,'desID':10, 'S_name':"City-D_Small", 'D_name':"Jetson", 'bandwidth':900, 'latency': 7.5}, {'sourceID':1,'desID':11, 'S_name':"City-D_Small", 'D_name':"RPi4", 'bandwidth':900, 'latency': 7.5}, {'sourceID':1,'desID':12, 'D_name':"City-A_Large", 'S_name':"City-D_Medium", 'bandwidth':1500, 'latency': 15}],
                                                                                                                                                                                                                               [{'sourceID':2,'desID':3, 'S_name':"City-D_Tiny", 'D_name':"City-B_Medium", 'bandwidth':1950, 'latency': 12.5}, {'sourceID':2,'desID':4, 'S_name':"City-D_Tiny", 'D_name':"MUC_Medium", 'bandwidth':3000, 'latency': 7.3},{'sourceID':2,'desID':5, 'S_name':"City-D_Tiny", 'D_name':"GEN_Medium", 'bandwidth':1500, 'latency': 16.5},{'sourceID':2,'desID':6, 'S_name':"City-D_Tiny", 'D_name':"FRA_Medium", 'bandwidth':1600, 'latency': 12.5}, {'sourceID':2,'desID':7, 'S_name':"City-D_Tiny", 'D_name':"City-E", 'bandwidth':5000, 'latency': 4.8}, {'sourceID':2,'desID':8, 'S_name':"City-D_Tiny", 'D_name':"City-E-Large", 'bandwidth':950, 'latency': 7.2}, {'sourceID':2,'desID':9, 'S_name':"City-D_Tiny", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 7.2}, {'sourceID':2,'desID':10, 'S_name':"City-D_Tiny", 'D_name':"Jetson", 'bandwidth':900, 'latency': 7.5}, {'sourceID':2,'desID':11, 'S_name':"City-D_Tiny", 'D_name':"RPi4", 'bandwidth':900, 'latency': 7.5}, {'sourceID':0,'desID':12, 'D_name':"City-A_Large", 'S_name':"City-D_Small", 'bandwidth':1500, 'latency': 15}],

[{'sourceID':3,'desID':4, 'S_name':"City-B_Medium", 'D_name':"MUC_Medium", 'bandwidth':3200, 'latency': 6.7},  {'sourceID':3,'desID':5, 'S_name':"City-B_Medium", 'D_name':"GEN_Medium", 'bandwidth':4500, 'latency': 5.1},  {'sourceID':3,'desID':6, 'S_name':"City-B_Medium", 'D_name':"FRA_Medium", 'bandwidth':2700, 'latency': 12},  {'sourceID':3,'desID':7, 'S_name':"City-B_Medium", 'D_name':"City-E", 'bandwidth':1400, 'latency': 16.6}, {'sourceID':3,'desID':8, 'S_name':"City-B_Medium", 'D_name':"City-E-Large", 'bandwidth':900, 'latency': 23.2}, {'sourceID':3,'desID':9, 'S_name':"City-B_Medium", 'D_name':"City-E-Medium", 'bandwidth':850, 'latency': 23.6}, {'sourceID':3,'desID':10, 'S_name':"City-B_Medium", 'D_name':"Jetson", 'bandwidth':700, 'latency': 23.2}, {'sourceID':3,'desID':11, 'S_name':"City-B_Medium", 'D_name':"RPi4", 'bandwidth':770, 'latency': 23.6}, {'sourceID':3,'desID':12, 'D_name':"City-A_Large", 'S_name':"City-B_Medium", 'bandwidth':900, 'latency': 25.9}],

[{'sourceID':4,'desID':5, 'S_name':"MUC_Medium", 'D_name':"GEN_Medium", 'bandwidth':2200, 'latency': 10.6},{'sourceID':4,'desID':6, 'S_name':"MUC_Medium", 'D_name':"FRA_Medium", 'bandwidth':3400, 'latency': 6.8},{'sourceID':4,'desID':7, 'S_name':"MUC_Medium", 'D_name':"City-E", 'bandwidth':2100, 'latency': 11.5}, {'sourceID':4,'desID':8, 'S_name':"MUC_Medium", 'D_name':"City-E-Large", 'bandwidth':930, 'latency': 12.2}, {'sourceID':4,'desID':9, 'S_name':"MUC_Medium", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 12.5}, {'sourceID':4,'desID':10, 'S_name':"MUC_Medium", 'D_name':"Jetson", 'bandwidth':900, 'latency': 12.6}, {'sourceID':4,'desID':11, 'S_name':"MUC_Medium", 'D_name':"RPi4", 'bandwidth':850, 'latency': 12.6},{'sourceID':4,'desID':12, 'D_name':"City-A_Large", 'S_name':"MUC_Medium", 'bandwidth':1100, 'latency': 21}],


[{'sourceID':5,'desID':6, 'S_name':"GEN_Medium", 'D_name':"FRA_Medium", 'bandwidth':1800, 'latency': 10},{'sourceID':5,'desID':6, 'S_name':"GEN_Medium", 'D_name':"City-E", 'bandwidth':2100, 'latency': 11.5}, {'sourceID':5,'desID':8, 'S_name':"GEN_Medium", 'D_name':"City-E-Large", 'bandwidth':930, 'latency': 12.2}, {'sourceID':5,'desID':9, 'S_name':"GEN_Medium", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 12.5}, {'sourceID':5,'desID':10, 'S_name':"GEN_Medium", 'D_name':"Jetson", 'bandwidth':900, 'latency': 12.6}, {'sourceID':5,'desID':11, 'S_name':"GEN_Medium", 'D_name':"RPi4", 'bandwidth':850, 'latency': 12.6},{'sourceID':5,'desID':12, 'D_name':"City-A_Large", 'S_name':"GEN_Medium", 'bandwidth':1100, 'latency': 21}],
[{'sourceID':6,'desID':7, 'S_name':"FRA_Medium", 'D_name':"City-E", 'bandwidth':2100, 'latency': 11.5}, {'sourceID':6,'desID':8, 'S_name':"FRA_Medium", 'D_name':"City-E-Large", 'bandwidth':930, 'latency': 12.2}, {'sourceID':6,'desID':9, 'S_name':"FRA_Medium", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 12.5}, {'sourceID':6,'desID':10, 'S_name':"FRA_Medium", 'D_name':"Jetson", 'bandwidth':900, 'latency': 12.6}, {'sourceID':6,'desID':11, 'S_name':"FRA_Medium", 'D_name':"RPi4", 'bandwidth':850, 'latency': 12.6},{'sourceID':6,'desID':12, 'D_name':"City-A_Large", 'S_name':"FRA_Medium", 'bandwidth':1100, 'latency': 21}],


[{'sourceID':7,'desID':8, 'S_name':"City-E", 'D_name':"City-E-Large", 'bandwidth':930, 'latency': 11.4}, {'sourceID':7,'desID':9, 'S_name':"City-E", 'D_name':"City-E-Medium", 'bandwidth':860, 'latency': 11.5}, {'sourceID':7,'desID':10, 'S_name':"City-E", 'D_name':"Jetson", 'bandwidth':840, 'latency': 12}, {'sourceID':7,'desID':11, 'S_name':"City-E", 'D_name':"RPi4", 'bandwidth':850, 'latency': 11.5},{'sourceID':7,'desID':12, 'S_name':"City-E", 'D_name':"City-A_Large", 'bandwidth':1200, 'latency': 10}],
[{'sourceID':8,'desID':9, 'S_name':"City-E-Large", 'D_name':"City-E-Medium", 'bandwidth':930, 'latency': 0.5}, {'sourceID':8,'desID':10, 'S_name':"City-E-Large", 'D_name':"Jetson", 'bandwidth':930, 'latency': 0.5}, {'sourceID':8,'desID':11, 'S_name':"City-E-Large", 'D_name':"RPi4", 'bandwidth':850, 'latency': 0.5},{'sourceID':8,'desID':12, 'S_name':"City-A_Large", 'D_name':"City-E-Large", 'bandwidth':920, 'latency': 22.4}],
[{'sourceID':9,'desID':10, 'S_name':"City-E-Medium", 'D_name':"Jetson", 'bandwidth':920, 'latency': 0.5}, {'sourceID':9,'desID':11, 'S_name':"City-E-Medium", 'D_name':"RPi4", 'bandwidth':850, 'latency': 0.5}, {'sourceID':9,'desID':12, 'D_name':"City-A_Large", 'S_name':"City-E-Medium", 'bandwidth':900, 'latency': 22.8}],
[{'sourceID':10,'desID':11, 'S_name':"Jetson", 'D_name':"RPi4", 'bandwidth':920, 'latency': 0.5}, {'sourceID':10,'desID':12, 'D_name':"City-A_Large", 'S_name':"Jetson", 'bandwidth':900, 'latency': 22.8}],
[{'sourceID':11,'desID':12, 'D_name':"City-A_Large", 'S_name':"RPi4", 'bandwidth':850, 'latency': 22.6}]]

net_cloud_info=[{'sourceID':1,'desID':0, 'D_name':"City-D_Medium", 'S_name':"City-A_Large", 'bandwidth':1500, 'latency': 15},  {'sourceID':1,'desID':1, 'D_name':"City-D_Small", 'S_name':"City-A_Large", 'bandwidth':1500, 'latency': 15}, {'sourceID':1,'desID':2, 'D_name':"City-D_Tiny", 'S_name':"City-A_Large", 'bandwidth':1500, 'latency': 15}, {'sourceID':1,'desID':3, 'D_name':"City-B_Medium", 'S_name':"City-A_Large", 'bandwidth':900, 'latency': 25.9},{'sourceID':1,'desID':4, 'D_name':"MUC_Medium", 'S_name':"City-A_Large", 'bandwidth':1100, 'latency': 21},
                 {'sourceID':1,'desID':5, 'S_name':"City-A_Large", 'D_name':"City-E", 'bandwidth':1200, 'latency': 10}, {'sourceID':1,'desID':6, 'S_name':"City-A_Large", 'D_name':"City-E-Large", 'bandwidth':920, 'latency': 22.4}, {'sourceID':1,'desID':7, 'S_name':"City-A_Large", 'D_name':"City-E-Medium", 'bandwidth':900, 'latency': 22.8}, {'sourceID':1,'desID':8, 'S_name':"City-A_Large", 'D_name':"Jetson", 'bandwidth':900, 'latency': 22.8}, {'sourceID':1,'desID':9, 'S_name':"City-A_Large", 'D_name':"RPi4", 'bandwidth':850, 'latency': 22.6},  {'sourceID':1,'desID':10, 'S_name':"City-A_Large", 'D_name':"City-A_Large", 'bandwidth':12000, 'latency': 0.5}]

net_info1=[{'sourceID':0,'desID':0, 'S_name':"City-D_large", 'D_name':"City-D_Small", 'bandwidth':13000, 'latency': 0.5},
           {'sourceID':1,'desID':1, 'S_name':"City-D_Medium", 'D_name':"City-D_Small", 'bandwidth':13000, 'latency': 0.5},
           {'sourceID':2,'desID':2, 'S_name':"City-D_Small", 'D_name':"City-D_Tiny", 'bandwidth':13000, 'latency': 0.5},
           {'sourceID':3,'desID':3, 'S_name':"City-B_Medium", 'D_name':"City-B_Medium", 'bandwidth':12000, 'latency': 0.5},
           {'sourceID':4,'desID':4, 'S_name':"MUC_Medium", 'D_name':"MUC_Medium", 'bandwidth':12000, 'latency': 0.5},
           {'sourceID':5,'desID':5, 'S_name':"GEN_Medium", 'D_name':"GEN_Medium", 'bandwidth':12000, 'latency': 0.5},
           {'sourceID':6,'desID':6, 'S_name':"FRA_Medium", 'D_name':"FRA_Medium", 'bandwidth':12000, 'latency': 0.5},
           {'sourceID':7,'desID':7, 'S_name':"City-E", 'D_name':"City-E", 'bandwidth':12000, 'latency': 0.5},
           {'sourceID':8,'desID':8, 'S_name':"Large", 'D_name':"Large", 'bandwidth':930, 'latency': 0.5},
           {'sourceID':9,'desID':9, 'S_name':"Medium", 'D_name':"Medium", 'bandwidth':860, 'latency': 0.5},
           {'sourceID':10,'desID':10, 'S_name':"Jetson", 'D_name':"Jetson", 'bandwidth':920, 'latency': 0.5},
           {'sourceID':11,'desID':11, 'S_name':"RPi4", 'D_name':"RPi4", 'bandwidth':850, 'latency': 0.5},
           {'sourceID':12,'desID':12, 'S_name':"City-A_Large", 'D_name':"City-A_Large", 'bandwidth':12000, 'latency': 0.5}]
def network_initiat():
    PERCENTATGEOFGATEWAYS = 0.25
    mylabels = {}
    nodeRAM = {}
    CPUCore = {}
    nodeSTORAGE = {}
    nodeFreeResources = {}
    node_Up_BW = {}
    node_Dwon_BW = {}
    nodeSpeed = {}
    SumRAM = 0.0
    SumStorage = 0.0
    SumCore = 0.0
    myEdges = list()
    nodeID = {}
    Flag = {}
    num = 0
    centralityValuesNoOrdered = 0
    gatewaysDevices = []
    cloudgatewaysDevices = set()


    for i in range(len(Device_ifo)):
        if Device_ifo[i]['id'] == 0:
            for j in range(num, res_num[0]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                nodeID[j] = Device_ifo[i]['id']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
            print("device type:", Device_ifo[i]['id'])
            num = res_num[0]['num']
        elif Device_ifo[i]['id'] == 1:
            for j in range(num, num + res_num[1]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[1]['num']
        elif Device_ifo[i]['id'] == 2:
            for j in range(num, num + res_num[2]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[2]['num']

        elif Device_ifo[i]['id'] == 3:
            for j in range(num, num + res_num[3]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[3]['num']

        elif Device_ifo[i]['id'] == 4:
            for j in range(num, num + res_num[4]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[4]['num']

        elif Device_ifo[i]['id'] == 5:
            for j in range(num, num + res_num[5]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[5]['num']

        elif Device_ifo[i]['id'] == 6:
            for j in range(num, num + res_num[6]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[6]['num']

        elif Device_ifo[i]['id'] == 7:
            for j in range(num, num + res_num[7]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[7]['num']

        elif Device_ifo[i]['id'] == 8:
            for j in range(num, num + res_num[8]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
                if j > 400:
                    gatewaysDevices.append(j)

            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[8]['num']

        elif Device_ifo[i]['id'] == 9:
            for j in range(num, num + res_num[9]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
                if j > 440:
                    gatewaysDevices.append(j)
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[9]['num']
        elif Device_ifo[i]['id'] == 10:
            for j in range(num, num + res_num[10]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
                if j > 470:
                    gatewaysDevices.append(j)
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[10]['num']
        elif Device_ifo[i]['id'] == 11:
            for j in range(num, num + res_num[11]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[11]['num']
        elif Device_ifo[i]['id'] == 12:
            for j in range(num, num + res_num[12]['num']):
                nodeRAM[j] = Device_ifo[i]['RAM']
                CPUCore[j] = Device_ifo[i]['cpu']['core_num']
                nodeSpeed[j] = Device_ifo[i]['cpu']['speed']
                nodeSTORAGE[j] = Device_ifo[i]['storage']
                SumRAM = SumRAM + nodeRAM[j]
                SumStorage = SumStorage + nodeSTORAGE[j]
                SumCore = SumCore + CPUCore[j]
                Flag[j] = False
                nodeID[j] = Device_ifo[i]['id']
            print("device type:", Device_ifo[i]['id'])
            num = num + res_num[12]['num']
    netJson = {}
    netJson1 = {}

    for i in range(0, num):
        myNode = {'id': i, 'IPT': nodeSpeed[i], 'cpu': {'core_num': CPUCore[i], 'cache': 4, 'speed': nodeSpeed[i]},
                  'storage': nodeSTORAGE[i], 'RAM': nodeRAM[i]}

        devices.append(myNode)

    for i in range(0, num):
        myNode1 = {}
        myNode1['id'] = i
        myNode1['RAM'] = nodeRAM[i]
        myNode1['IPT'] = nodeSpeed[i]
        myNode1['core'] = CPUCore[i]
        myNode1['storage'] = nodeSTORAGE[i]
        devices1.append(myNode1)
    netMatrix1=[]
    all_Edge=[]
    for i in range(0, num):
        edges = []
        for j in range(i, num):
            if i == j:
                pass
            else:
                netMatrix1.append((i, j))
                if nodeID[i] == nodeID[j]:
                    myLink = {}
                    myLink['s'] = i
                    myLink['d'] = j
                    myLink['PR'] = net_info1[nodeID[i]]['latency']
                    myLink['BW'] = net_info1[nodeID[i]]['bandwidth']
                    myEdges.append(myLink)
                    edges.append(myLink)
                else:
                    if j == num:
                        pass
                    else:
                        myLink = {}
                        myLink['s'] = i
                        myLink['d'] = j
                        myLink['PR'] = net_info[nodeID[i]][nodeID[j] - (nodeID[i] + 1)]['latency']
                        myLink['BW'] = net_info[nodeID[i]][nodeID[j] - (nodeID[i] + 1)]['bandwidth']

                        myEdges.append(myLink)
                        edges.append(myLink)
        all_Edge.append(edges)


    G = nx.Graph()
    G.add_edges_from(netMatrix1)
    for n in range(0, len(G.nodes)):
        mylabels[n] = str(n)

    for e in G.edges:
        i = 1
        #print("edge source and distination:", e[0], " -> ", e[1])
        G[e[0]][e[1]]['PR'] = all_Edge[e[0]][e[1] - (i + e[0])]['PR']
        #print("The graph link latency", G[e[0]][e[1]]['PR'])
        G[e[0]][e[1]]['BW'] = all_Edge[e[0]][e[1] - (i + e[0])]['BW']
        #print("The graph link bandwidth", G[e[0]][e[1]]['BW'])
        G[e[0]][e[1]]['weight'] = 1 / (float(G[e[0]][e[1]]['PR']))
        #print("The graph weigths", G[e[0]][e[1]]['weight'])
        i = i + 2

    cloudId = 1000
    myNode = {'id': cloudId, 'cpu': {'core_num': cloud_info[0]['cpu']['core_num'], 'cache': CLOUD_CPU_CACHE, 'speed': cloud_info[0]['cpu']['speed']},
              'storage': cloud_info[0]['storage'],'RAM': cloud_info[0]['RAM']}
    devices.append(myNode)

    myNode1 = {}
    myNode1['id'] = cloudId
    myNode1['RAM'] = cloud_info[0]['RAM']
    myNode1['IPT'] = cloud_info[0]['cpu']['speed']
    devices1.append(myNode1)

    for i in G.nodes:
        myLink = {}
        if i<res_num[0]['num']:
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[0]['latency']
            myLink['BW'] = net_cloud_info[0]['bandwidth']
            #print("The resource type 0")
        elif i<(res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[1]['latency']
            myLink['BW'] = net_cloud_info[1]['bandwidth']
            #print("The resource type 1")
        elif i < (res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[2]['latency']
            myLink['BW'] = net_cloud_info[2]['bandwidth']
            #print("The resource type 2")
        elif i < (res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[3]['latency']
            myLink['BW'] = net_cloud_info[3]['bandwidth']
            #print("The resource type 3")
        elif i < (res_num[4]['num']+res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[4]['latency']
            myLink['BW'] = net_cloud_info[4]['bandwidth']
            #print("The resource type 4")
        elif i < (res_num[5]['num']+res_num[4]['num']+res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[5]['latency']
            myLink['BW'] = net_cloud_info[5]['bandwidth']
            #print("The resource type 5")
        elif i < (res_num[6]['num']+res_num[5]['num']+res_num[4]['num']+res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[6]['latency']
            myLink['BW'] = net_cloud_info[6]['bandwidth']
            #print("The resource type 6")
        elif i < (res_num[7]['num']+res_num[6]['num']+res_num[5]['num']+res_num[4]['num']+res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[7]['latency']
            myLink['BW'] = net_cloud_info[7]['bandwidth']
            #print("The resource type 7")
        elif i < (res_num[8]['num']+res_num[7]['num']+res_num[6]['num']+res_num[5]['num']+res_num[4]['num']+res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[8]['latency']
            myLink['BW'] = net_cloud_info[8]['bandwidth']
            #print("The resource type 8")
        elif i < (res_num[9]['num']+res_num[8]['num']+res_num[7]['num']+res_num[6]['num']+res_num[5]['num']+res_num[4]['num']+res_num[3]['num']+res_num[2]['num']+res_num[1]['num']+res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[9]['latency']
            myLink['BW'] = net_cloud_info[9]['bandwidth']
            #print("The resource type 9")
        elif i < (res_num[10]['num'] +res_num[9]['num'] + res_num[8]['num'] + res_num[7]['num'] + res_num[6]['num'] + res_num[5]['num'] +
                  res_num[4]['num'] + res_num[3]['num'] + res_num[2]['num'] + res_num[1]['num'] + res_num[0]['num']):
            myLink['s'] = i
            myLink['d'] = cloudId
            myLink['PR'] = net_cloud_info[10]['latency']
            myLink['BW'] = net_cloud_info[10]['bandwidth']
        else:
            pass
        myEdges.append(myLink)
    netJson['entity'] = devices
    netJson['link'] = myEdges
    netJson1['entity'] = devices1
    netJson1['link'] = myEdges
    file = open("networkDefinition1.json", "w")
    file.write(json.dumps(netJson1))
    file = open("networkDefinition.json", "w")
    file.write(json.dumps(netJson))
    file.close()
    initial_len = len(G.nodes)
    initGraph = G.copy()

    return G, initGraph, initial_len, centralityValuesNoOrdered, gatewaysDevices, SumRAM, SumStorage, SumCore, nodeSpeed, nodeRAM, CPUCore, nodeSTORAGE

def network_update_del(G, del_nodes, SumRAM, SumStorage, SumCore, devices):
    mylabels = {}
    print("The number of devices befor deleting nodes:  ", len(devices))

    for i in range(len(del_nodes)):
        G.remove_node(del_nodes[i])
        for j in range(len(devices)):
            if devices[j]['id'] == del_nodes[i]:
                devices.pop(j)
                print("the node (", del_nodes[i], ") was deleted from the network")
                devices1.pop(j)
                SumRAM = SumRAM - devices[j]['RAM']
                SumStorage = SumStorage - devices[j]['storage']
                SumCore = SumCore - devices[j]['cpu']['core_num']
                break
    for n in range(0, len(G.nodes)):
        mylabels[n] = str(n)
    mapping = dict(zip(G, range(len(mylabels))))
    G = nx.relabel_nodes(G, mapping)
    print("The number of devices after deleting nodes:  ", len(devices))
    weightNetwork1(G)
    return G, devices, SumRAM, SumStorage, SumCore


def NETWORKGENERATION(G):
    topology_matrix = nx.to_numpy_matrix(G)
    return topology_matrix


def GraphGeneration(topo_matrix):
    graph = nx.from_numpy_matrix(topo_matrix)
    return graph


def get_devices():
    return devices


def network_update_add(G, initial_len, tt, newnodes, SumRAM, SumStorage, SumCore, devices):
    PERCENTATGEOFGATEWAYS = 0.25
    gatewaysDevices = set()
    cloudgatewaysDevices = set()
    mylabels = {}
    nodeRAM = {}
    CPUCore = {}
    nodeSpeed = {}
    nodeSTORAGE = {}
    myEdges = list()
    isolated_Devices = []
    n = len(G.nodes)
    newsize = n + newnodes
    centralityValuesNoOrdered = nx.betweenness_centrality(G, weight="weight")
    centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=False)
    for id in range(0, len(G.nodes)):
        if G.degree(centralityValues[id][0]) == 0:
            isolated_Devices.append(centralityValues[id][0])
    for i in range(n, newsize):
        G.add_node(i)
        if len(isolated_Devices) == 0:
            PR = eval(func_PROPAGATIONTIME)
            BW = eval(func_BANDWITDH)
            G.add_edge(i, i - 40, PR=PR, BW=BW)
            PR = eval(func_PROPAGATIONTIME)
            BW = eval(func_BANDWITDH)
            G.add_edge(i, i - 6, PR=PR, BW=BW)
        elif len(isolated_Devices) < 2:
            for dev in isolated_Devices:
                PR = eval(func_PROPAGATIONTIME)
                BW = eval(func_BANDWITDH)
                G.add_edge(i, dev, PR=PR, BW=BW)
                PR = eval(func_PROPAGATIONTIME)
                BW = eval(func_BANDWITDH)
                G.add_edge(i, i - 40, PR=PR, BW=BW)
                print("This is isolated devices: ", dev)
        else:
            for dev in isolated_Devices:
                G.add_edge(i, dev, PR=eval(func_PROPAGATIONTIME), BW=BW)

    for i in range(0, len(G.nodes)):
        mylabels[i] = str(i)
    mapping = dict(zip(G, range(len(mylabels))))
    G = nx.relabel_nodes(G, mapping)

    for i in range(n, newsize):
        nodeRAM[i] = eval(func_NODERAM)
        CPUCore[i] = eval(func_CPU_Core)
        nodeSpeed[i] = eval(func_NODESPEED)
        nodeSTORAGE[i] = eval(func_NODESTORAGE)
        SumRAM = SumRAM + nodeRAM[i]
        SumStorage = SumStorage + nodeSTORAGE[i]
        SumCore = SumCore + CPUCore[i]

    # JSON EXPORT
    netJson = {}
    netJson1 = {}

    for i in range(n, newsize):
        myNode = {'id': initial_len, 'IPT': nodeSpeed[i],
                  'cpu': {'core_num': CPUCore[i], 'cache': 4, 'speed': nodeSpeed[i]}, 'storage': nodeSTORAGE[i],
                  'RAM': nodeRAM[i]}
        initial_len = initial_len + 1
        devices.append(myNode)

    for e in G.edges:
        myLink = {}
        myLink['s'] = e[0]
        myLink['d'] = e[1]
        myLink['PR'] = G[e[0]][e[1]]['PR']
        myLink['BW'] = G[e[0]][e[1]]['BW']
        myEdges.append(myLink)

    for i in range(n, newsize):
        myNode1 = {}
        myNode1['id'] = i
        myNode1['RAM'] = nodeRAM[i]
        myNode1['RAM-norm'] = nodeRAM[i] / SumRAM
        myNode1['IPT'] = nodeSpeed[i]
        myNode1['core'] = CPUCore[i]
        myNode1['storage'] = nodeSTORAGE[i]
        devices1.append(myNode1)

    weightNetwork1(G)

    centralityValuesNoOrdered = nx.betweenness_centrality(G, weight="weight")
    centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)

    highestCentrality = centralityValues[0][1]
    gateway_info = []
    for device in centralityValues:
        if device[1] == highestCentrality:
            cloudgatewaysDevices.add(device[0])

    initialIndx = int((1 - PERCENTATGEOFGATEWAYS) * len(G.nodes))  # Indice del final para los X tanto por ciento nodos
    cloudgateway = True
    for idDev in range(initialIndx - 1, (len(G.nodes))):
        if (cloudgateway == True):
            cloudgateway = False
        else:
            gatewaysDevices.add(centralityValues[idDev][0])
            gateway_info.append({'id': centralityValues[idDev][0], 'centrality_value': centralityValues[idDev][1]})
    print("This gateway devices in this certain time window:", gateway_info)

    for cloudGtw in cloudgatewaysDevices:
        myLink = {}
        myLink['s'] = cloudGtw
        myLink['d'] = cloudId
        myLink['PR'] = CLOUDPR
        myLink['BW'] = CLOUDBW

        myEdges.append(myLink)

    netJson['entity'] = devices
    netJson['link'] = myEdges
    netJson1['entity'] = devices1
    netJson1['link'] = myEdges
    netfile = "networkDefinition_" + str(tt) + ".json"
    netfile1 = "networkDefinition1_" + str(tt) + ".json"
    file = open(netfile, "w")
    file.write(json.dumps(netJson))
    file.close()
    file = open(netfile1, "w")
    file.write(json.dumps(netJson1))
    file.close()
    return G, initial_len, devices, centralityValuesNoOrdered, gatewaysDevices, SumRAM, SumStorage, SumCore


def weightNetwork1(G):
    size = float(1)
    for e in G.edges:
        G[e[0]][e[1]]['weight'] = float(G[e[0]][e[1]]['PR']) + (size / float(G[e[0]][e[1]]['BW']))


# ***********************************************************************************************************************
# Commmunity calculation based on modularity maximization in multilayer network

# ***********************************************************************************************************************

def initial_partitioning(G, resolution):
    devices = get_devices()

    nx.write_graphml(G, 'graph.graphml')  # Export NX graph to file
    Gix = ig.read('graph.graphml', format="graphml")  # Create new IG graph from file

    partitions = louvain.find_partition(Gix, louvain.RBConfigurationVertexPartition, resolution_parameter=resolution)
    membership = partitions.membership

    return partitions, membership


def update_partitions(G, initial_len, new_nodes, del_nodes, tt, pre_topo_par,
                      pre_topo_mem, SumRAM, SumStorage, SumCore):
    devices = get_devices()
    nx.write_graphml(G, 'graph0.graphml')  # Export NX graph to file
    pre_Gix = ig.read('graph0.graphml', format="graphml")
    print("The number of devices in update function before any changes:  ", len(devices))
    G, devices, SumRAM, SumStorage, SumCore = network_update_del(G, del_nodes, SumRAM, SumStorage, SumCore, devices)
    topology_layer = NETWORKGENERATION(G)

    nx.write_graphml(G, 'graph.graphml1')  # Export NX graph to file
    Gix = ig.read('graph.graphml1', format="graphml")
    topo_par, topo_mem = louvain_ext.monolaye_update_partition_del2(del_nodes, pre_Gix, Gix, G, pre_topo_par,
                                                                    pre_topo_mem)

    G, initial_len, devices, centralityValuesNoOrdered, gatewaysDevices, SumRAM, SumStorage, SumCore = network_update_add(
        G, initial_len, tt, new_nodes, SumRAM, SumStorage, SumCore, devices)

    print("number of fog devices: ", len(devices))
    topology_layer = NETWORKGENERATION(G)
    print("deleted nodes: ", del_nodes)
    print("Graph size: ", len(topology_layer))
    n = (len(devices))

    nx.write_graphml(G, 'graph.graphml2')  # Export NX graph to file
    Gix = ig.read('graph.graphml2', format="graphml")  # Create new IG graph from file
    topo_par1, topo_mem1 = louvain_ext.monolaye_update_partition_add2(new_nodes, Gix, topo_par, topo_mem)

    return topo_par1, topo_mem1, G, initial_len, SumRAM, SumStorage, SumCore, centralityValuesNoOrdered, gatewaysDevices

def initial_multilayer_on_layer(G, devices):
    print("The number of devices in initial state:  ", len(devices))
    layer_name = {0: 'cpu', 1: 'storage', 2: 'RAM', 4: 'topology'}
    cpu_layer = Similaritymeasurment.layer_creation('cpu', devices)
    storage_layer = Similaritymeasurment.layer_creation('storage', devices)
    RAM_layer = Similaritymeasurment.layer_creation('RAM', devices)
    topology_layer = NETWORKGENERATION(G)

    n = (len(topology_layer)) + 1
    l = len(layer_name) - 1
    # Here we represent intralayer in a single "supra-adjacency"
    super_adj = np.zeros((l * n, l * n))
    super_adj[:n, :n] = cpu_layer
    super_adj[n:2 * n, n:2 * n] = storage_layer
    super_adj[2 * n:3 * n, 2 * n:3 * n] = RAM_layer

    print(super_adj)

    #
    inter_elist = [(i, i + n) for i in range(n)] + \
                  [(i + n, 2 * n + i) for i in range(n)] + \
                  [(2 * n + i, i) for i in range(n)]

    C = np.zeros((3 * n, 3 * n))
    for i, j in inter_elist:
        C[i, j] = 1
        C[j, i] = 1

    layer_vec = np.array([i // n for i in range(3 * n)])


    partitions = []
    membership = []
    mult_part_ens = louvain_ext.parallel_multilayer_louvain_from_adj(intralayer_adj=super_adj,
                                                                     interlayer_adj=C, layer_vec=layer_vec,
                                                                     progress=True, numprocesses=2,
                                                                     inter_directed=False, intra_directed=False,
                                                                     gamma_range=[0, 4], ngamma=5,
                                                                     omega_range=[0, 4], nomega=5, maxpt=[4, 10])

    for i in range(len(mult_part_ens)):
        if mult_part_ens[i]['coupling'] == 1:
            if mult_part_ens[i]['resolution'] == 4:
                partitions.append(mult_part_ens[i]['part'])
                membership.append(mult_part_ens[i]['membership'])
    print("The length of feature partitions:", len(partitions))

    nx.write_graphml(G, 'graph.graphml')  # Export NX graph to file
    Gix = ig.read('graph.graphml', format="graphml")  # Create new IG graph from file
    print("This is the graph:", Gix.es["weight"])

    topo_par = louvain.find_partition(Gix, louvain.RBConfigurationVertexPartition,weights='weight',
                                          resolution_parameter=1)
    topo_mem = topo_par.membership

    return partitions, membership, topo_par, topo_mem, cpu_layer, storage_layer, RAM_layer, super_adj
G, initGraph, initial_len, centralityValuesNoOrdered, gatewaysDevices, SumRAM, SumStorage, SumCore, nodeSpeed, nodeRAM, CPUCore, nodeSTORAGE = network_initiat()

devices = get_devices()


with open("networkDefinition.json", "r") as json_file:
    content = json.load(json_file)
Fog_resources = content['entity']
network_size = (len(Fog_resources)) - 1
Feature_partitions, Feature_membership, topo_par, topo_mem, cpu_layer, storage_layer, RAM_layer, super_adj = initial_multilayer_on_layer(
    G, devices)
print("topological partitions:", topo_par)
print("Feature partitions:", Feature_partitions)
Fog_community = SLA_aware_placement.comm_attribute1(Fog_resources, Feature_partitions, network_size)
Delay, sortnettime = SLA_aware_placement.nettime(G, Fog_community)
plt.figure(0)
com_color = ['#FF9F33', 'g', 'b', 'r', 'y', 'c', 'm', '#8033FF', '#FF338A', '#A08AAD', '#EAC8EC', '#D4C8EC',
             '#93EAAF', 'g', 'b', 'r', 'y', 'c', 'm', 'g', 'b', 'r', 'y', 'c', 'm', '#FF9F33', 'g', 'b', 'r', 'y', 'c', 'm', '#8033FF', '#FF338A', '#A08AAD', '#EAC8EC', '#D4C8EC',
             '#93EAAF', 'g', 'b', 'r', 'y', 'c', 'm', 'g', 'b', 'r', 'y', 'c', 'm']
pos = nx.spring_layout(G)
topo_count = 0
#print("This is length of topological partition: ", len(topo_par))
for i in range(len(topo_par)):
    nx.draw_networkx_nodes(G, pos, nodelist=topo_par[i], node_color=com_color[topo_count])
    topo_count = topo_count + 1
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos)

PAr_SLAList = [[] for j in range(len(topo_par))]  # General SLA assurance at different time intervals for different partitions
SA1 = []
SA2 = []
SA3 = []

SLAassurance1 = [[] for j in range(len(topo_par))]  # SLA assurance 1 at different time intervals for different partitions
SLAassurance2 = [[] for j in range(len(topo_par))]  # SLA assurance 2 at different time intervals
SLAassurance3 = [[] for j in range(len(topo_par))]  # SLA assurance 3 at different time intervals
GSLAList = []

###########################################################################################################################################

# ****************SLA_agent selection**********************

###########################################################################################################################################

centralityValuesNoOrdered = nx.betweenness_centrality(G, weight="weight")
centralityValues = sorted(centralityValuesNoOrdered.items(), key=operator.itemgetter(1), reverse=True)
partitions, membership = initial_partitioning(G, resolution=1)
highestCentrality = centralityValues[0][1]
device= centralityValues[0][0]
SLA_coordinatoors=[0.0]*len(partitions)
for device in centralityValues:
    SLA_coordinatoors[membership[device[0]]]=device[0]

###########################################################################################################################################
