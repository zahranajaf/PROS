from pickle import TRUE
from telnetlib import NOOPT, NOP
import numpy
from operator import itemgetter, attrgetter
import networkx as nx
import yaml
import subprocess as commands
import json
import sys
import time
import pandas as pd

########### if device is ready and has enough capacity

############# if the service is successful

############### if the deadline is satisfied
###################### to create some delays 
###################### based on the processing, queuing, and latency based on software or network delays
######################

ranks = {'0':[0,0,0,0,0,0],  
        '1': [0,0,0,0,0,0],   '2': [0,0,0,0,0,0],   '3': [0,0,0,0,0,0],  '4': [0,0,0,0,0,0],
        '5': [0,0,0,0,0,0],   '6': [0,0,0,0,0,0],   '7': [0,0,0,0,0,0],   '8': [0,0,0,0,0,0],  '9': [0,0,0,0,0,0],  '10':[0,0,0,0,0,0],  
        '11': [0,0,0,0,0,0],   '12': [0,0,0,0,0,0],   '13': [0,0,0,0,0,0],  '14': [0,0,0,0,0,0],
        '15': [0,0,0,0,0,0],   '16': [0,0,0,0,0,0],   '17': [0,0,0,0,0,0],  '18': [0,0,0,0,0,0],  '19': [0,0,0,0,0,0],  '20':[0,0,0,0,0,0], 
        '21': [0,0,0,0,0,0],   '22': [0,0,0,0,0,0],   '23': [0,0,0,0,0,0],  '24': [0,0,0,0,0,0],
        '25': [0,0,0,0,0,0],   '26': [0,0,0,0,0,0],   '27': [0,0,0,0,0,0],  '28': [0,0,0,0,0,0],  '29': [0,0,0,0,0,0],  '30':[0,0,0,0,0,0],
        '31': [0,0,0,0,0,0],   '32': [0,0,0,0,0,0],   '33': [0,0,0,0,0,0],  '34': [0,0,0,0,0,0],
        '35': [0,0,0,0,0,0],   '36': [0,0,0,0,0,0],   '37': [0,0,0,0,0,0],  '38': [0,0,0,0,0,0],  '39': [0,0,0,0,0,0],  '40':[0,0,0,0,0,0],
        '41': [0,0,0,0,0,0],   '42': [0,0,0,0,0,0],   '43': [0,0,0,0,0,0],  '44': [0,0,0,0,0,0],
        '45': [0,0,0,0,0,0],   '46': [0,0,0,0,0,0],   '47': [0,0,0,0,0,0],  '48': [0,0,0,0,0,0],  '49': [0,0,0,0,0,0],  '50':[0,0,0,0,0,0],
        '51': [0,0,0,0,0,0],   '52': [0,0,0,0,0,0],   '53': [0,0,0,0,0,0],  '54': [0,0,0,0,0,0],
        '55': [0,0,0,0,0,0],   '56': [0,0,0,0,0,0],   '57': [0,0,0,0,0,0],  '58': [0,0,0,0,0,0],  '59': [0,0,0,0,0,0],  '60':[0,0,0,0,0,0],
        '61': [0,0,0,0,0,0],   '62': [0,0,0,0,0,0],   '63': [0,0,0,0,0,0],  '64': [0,0,0,0,0,0],
        '65': [0,0,0,0,0,0],   '66': [0,0,0,0,0,0],   '67': [0,0,0,0,0,0],  '68': [0,0,0,0,0,0],  '69': [0,0,0,0,0,0],  '70':[0,0,0,0,0,0],
        '71': [0,0,0,0,0,0],   '72': [0,0,0,0,0,0],   '73': [0,0,0,0,0,0],  '74': [0,0,0,0,0,0],
        '75': [0,0,0,0,0,0],   '76': [0,0,0,0,0,0],   '77': [0,0,0,0,0,0],  '78': [0,0,0,0,0,0],  '79': [0,0,0,0,0,0],  '80':[0,0,0,0,0,0],
        '81': [0,0,0,0,0,0],   '82': [0,0,0,0,0,0],   '83': [0,0,0,0,0,0],  '84': [0,0,0,0,0,0],
        '85': [0,0,0,0,0,0],   '86': [0,0,0,0,0,0],   '87': [0,0,0,0,0,0],  '88': [0,0,0,0,0,0],  '89': [0,0,0,0,0,0],  '90':[0,0,0,0,0,0],
        '91': [0,0,0,0,0,0],   '92': [0,0,0,0,0,0],   '93': [0,0,0,0,0,0],  '94': [0,0,0,0,0,0],
        '95': [0,0,0,0,0,0],   '96': [0,0,0,0,0,0],   '97': [0,0,0,0,0,0],  '98': [0,0,0,0,0,0],  '99': [0,0,0,0,0,0],  '100':[0,0,0,0,0,0],
        '101': [0,0,0,0,0,0],   '102': [0,0,0,0,0,0],   '103': [0,0,0,0,0,0],  '104': [0,0,0,0,0,0],
        '105': [0,0,0,0,0,0],   '106': [0,0,0,0,0,0],   '107': [0,0,0,0,0,0],  '108': [0,0,0,0,0,0],  '109': [0,0,0,0,0,0],  '110':[0,0,0,0,0,0],
        '111': [0,0,0,0,0,0],   '112': [0,0,0,0,0,0],   '113': [0,0,0,0,0,0],  '114': [0,0,0,0,0,0],
        '115': [0,0,0,0,0,0],   '116': [0,0,0,0,0,0],   '117': [0,0,0,0,0,0],  '118': [0,0,0,0,0,0],  '119': [0,0,0,0,0,0]}

Device_ifo=[{'id': 0, 'name':"City-D_Large", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000}, 'network': {'up_Bw': 140, 'down_Bw': 140, 'Latency':23}, 'storage': 10,'RAM': 8},
            {'id': 1, 'name':"City-D_Medium",'IPT': 7200, 'cpu': {'core_num': 2, 'cache': 4, 'speed': 7200},'network': {'up_Bw': 220, 'down_Bw': 220, 'Latency':7}, 'storage': 10, 'RAM': 4},
            {'id': 2, 'name':"City-D_Small",'IPT': 7100, 'cpu': {'core_num': 2, 'cache': 4, 'speed': 7100}, 'network': {'up_Bw': 220, 'down_Bw': 220, 'Latency':7}, 'storage': 10,'RAM': 2},
            {'id': 3, 'name':"City-B", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000}, 'network': {'up_Bw': 140, 'down_Bw': 140, 'Latency':23}, 'storage': 10,'RAM': 8},
            {'id': 4, 'name':"City-C", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000}, 'network': {'up_Bw': 140, 'down_Bw': 140, 'Latency':23}, 'storage': 10,'RAM': 8},
            {'id': 5,'name':"City-E", 'IPT': 12000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 12000}, 'network': {'up_Bw': 220, 'down_Bw': 220, 'Latency':12}, 'storage': 10,'RAM': 8},
            {'id': 6,'name':"City-E-Large", 'IPT': 58000, 'cpu': {'core_num': 12, 'cache': 4, 'speed': 58000}, 'network': {'up_Bw': 940, 'down_Bw': 940, 'Latency':2}, 'storage': 32,'RAM': 32},
            {'id': 7,'name':"City-E-Medium", 'IPT': 21700, 'cpu': {'core_num': 8, 'cache': 4, 'speed': 21700}, 'network': {'up_Bw': 920, 'down_Bw': 920, 'Latency':2}, 'storage': 32,'RAM': 16},
            {'id': 8,'name':"Jetson", 'IPT': 4080, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 4080}, 'network': {'up_Bw': 840, 'down_Bw': 840, 'Latency':2}, 'storage': 64,'RAM': 4},
            {'id': 9,'name':"RPi4", 'IPT': 5100, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 5100}, 'network': {'up_Bw': 800, 'down_Bw': 800, 'Latency':2}, 'storage': 64,'RAM': 4}]
cloud_info=  [{'id': 1,'name':"City-A_Large", 'IPT': 14000, 'cpu': {'core_num': 4, 'cache': 4, 'speed': 14000}, 'network': {'up_Bw': 140, 'down_Bw': 140, 'Latency':23}, 'storage': 10,'RAM': 8}]


alloc_file = "D:\\00Research\\00Fog\\TimeIntervals-large - diffStress\\00Light\\2\\No\\networkDefinition2.json"
with open(alloc_file, "r") as json_file:
    devices = json.load(json_file)
#print(len(devices["entity"]))
#print((devices["link"][203]))
app_file = "D:\\00Research\\00Fog\\TimeIntervals-large - diffStress\\00Light\\2\\No\\allocDefinition_NF2.json"
with open(app_file, "r") as json_file2:
        services = json.load(json_file2)

for j in range(len(devices["entity"])):
        if(j == 0 or j == 30 or j == 50 or j == 110):
                devices["entity"][j]["Status"] = "NotReady"
        elif (j == 60 or j == 63):
                devices["entity"][j]["Status"] = "NotReady"
        elif (j == 70 or j == 80 or j == 90 or j == 91 or j == 92):
                devices["entity"][j]["Status"] = "NotReady"
'''with open(alloc_file, "w") as outfile:
	json.dump(devices,outfile)
	outfile.close'''

for j in range(len(services["initialAllocation"])):
        #print(services["initialAllocation"][j]["id_resource"])
        if (services["initialAllocation"][j]["id_resource"] == 10 or services["initialAllocation"][j]["id_resource"] == 20 or services["initialAllocation"][j]["id_resource"] == 40 or services["initialAllocation"][j]["id_resource"] == 100):
                services["initialAllocation"][j]["Status"] = "Crashed"
        elif (services["initialAllocation"][j]["id_resource"] == 61 or services["initialAllocation"][j]["id_resource"] == 62):
                services["initialAllocation"][j]["Status"] = "Crashed" 
        elif (services["initialAllocation"][j]["id_resource"] == 71 or services["initialAllocation"][j]["id_resource"] == 72 or services["initialAllocation"][j]["id_resource"] == 80 or services["initialAllocation"][j]["id_resource"] == 81 or services["initialAllocation"][j]["id_resource"] == 82 or services["initialAllocation"][j]["id_resource"] == 92):
                services["initialAllocation"][j]["Status"] = "Crashed" 
with open(app_file, "w") as outfile:
	json.dump(services,outfile)
	outfile.close

time = [0.7835 , 0.2585 , 0.2585 , 0.105 , 0.7835 , 0.8336 , 0.702 , 0.105 , 0.895 , 0.4458 ,
0.748 , 1.0486 , 0.1176 , 0.8094 , 2.1883 , 1.7224 , 2.6004 , 1.7424 , 2.016 , 1.7424 ,
3.0704 , 3.0704 , 1.7422 , 1.7262 , 1.7262 , 1.7262 , 3.4812 , 3.4812 , 3.4812 , 3.208]

deadline = [0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4,3.4]

'''for j in range(len(devices["entity"])):
        if (devices["entity"][j]["id"] == j and devices["entity"][j]["Status"] == "Ready"):                
                for service in range(len(services["initialAllocation"])):
                        if (devices["entity"][j]["id"] == services["initialAllocation"][service]["id_resource"] and services["initialAllocation"][service]["Status"] == "Completed"):
                                if (j>69 and j<100):
                                        if(j==64 or j==65 or j==66 or j==73 or j==74 or j==75 or j==83 or j==84 or j==85 or j==93 or j==94 or j==95):
                                                time[int(services["initialAllocation"][service]["app"])]  =  time[int(services["initialAllocation"][service]["app"])] + 0''' #0.1

for j in range(len(devices["entity"])):
        if (devices["entity"][j]["id"] == j and devices["entity"][j]["Status"] == "Ready"):                
                for service in range(len(services["initialAllocation"])):
                    
                    if (devices["entity"][j]["id"] == services["initialAllocation"][service]["id_resource"] and services["initialAllocation"][service]["Status"] == "Completed"):
                        ranks[str(devices["entity"][j]["id"])][0] = ranks[str(devices["entity"][j]["id"])][0] + 1
                        ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][2] = ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][2] + 1
                        #######print(ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][2])
                        
                        if(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"]==j and time[int(services["initialAllocation"][service]["app"])] <= deadline[int(services["initialAllocation"][service]["app"])]):
                            ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][4] = ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][4] + 1
                        elif(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"]==j and time[int(services["initialAllocation"][service]["app"])] > deadline[int(services["initialAllocation"][service]["app"])]):
                            ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][5] = ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][5] + 1
                    
                    elif (devices["entity"][j]["id"] == services["initialAllocation"][service]["id_resource"] and services["initialAllocation"][service]["Status"] != "Completed"):
                        ranks[str(devices["entity"][j]["id"])][0] = ranks[str(devices["entity"][j]["id"])][0] + 1
                        ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][3] = ranks[str(devices["entity"][services["initialAllocation"][service]["id_resource"]]["id"])][3] + 1

        elif (devices["entity"][j]["id"] == j and devices["entity"][j]["Status"] != "Ready"):
            ranks[str(devices["entity"][j]["id"])][1] = ranks[str(devices["entity"][j]["id"])][1] + 1
            
print(ranks)
acceptance = 0
service_success = 0
deadline_violation = 0
for j in range(len(devices["entity"])):
        acceptance = acceptance + ranks[str(devices["entity"][j]["id"])][0]
        service_success = service_success + ranks[str(devices["entity"][j]["id"])][2]
        deadline_violation = deadline_violation + ranks[str(devices["entity"][j]["id"])][5]

print(numpy.average(time)," seconds")
print(acceptance," from ", len(services["initialAllocation"]))
print(service_success," from ", len(services["initialAllocation"]))
print(len(services["initialAllocation"])-deadline_violation," from ", len(services["initialAllocation"]))
