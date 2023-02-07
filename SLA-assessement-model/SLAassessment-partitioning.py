import json
import operator
import SLA_aware_placement
import Networkpartitioning
import random
import numpy as np
from SLAassessment import SLACalculation
from Similaritymeasurment import SLA_Sim_graph
from TSLA import TSLA_cal


# USERS and IoT DEVICES
func_REQUESTPROB = "random.random()/8"
func_USERREQRAT = "random.randint(10,100)"  # MS
pathSimple = "./scenariot/"



def Normalizing(data):
    normalized = []
    d=np.array(data)
    min=d.min()
    max=d.max()
    for i in range(len(data)):
        if (max-min)!=0:
            norm= (d[i]-min)/(max-min)*10
        else:
            norm=0
        normalized.append(norm)

    return normalized


def SLAPartitioning(SLAValue, partitionmem):
    G_SLA = SLA_Sim_graph(SLAValue)
    partitions, membership = Networkpartitioning.initial_partitioning(G_SLA, resolution=2)
    AVG = []
    Par_SLA_info = []  # The average SLA value of each SLA partition at time t
    sorted_SLAPar = []
    for par in partitions:
        sum = 0.0
        member = []
        for device in par:
            sum = sum + SLAValue[device]
            member.append(partitionmem[device])
        avg = sum / len(par)
        AVG.append(avg)
        Par_SLA_info.append({'member': member, 'SLAValue': avg})
    for sorted_inf in sorted(Par_SLA_info, key=operator.itemgetter('SLAValue'), reverse=True):
        sorted_SLAPar.append(sorted_inf)
    return sorted_SLAPar, partitions, membership


AcceptPar = []
Vio_accept = []
SuccessPar = []
Vio_success = []
SatiPar = []
Vio_satify = []
SPt = []
NPt = []
SP = []
NP = []

devices = Networkpartitioning.get_devices()
G=Networkpartitioning.G
topo_par=Networkpartitioning.topo_par
Delay=Networkpartitioning.Delay
sortnettime=Networkpartitioning.sortnettime
topo_mem=Networkpartitioning.topo_mem
Fog_community=Networkpartitioning.Fog_community
PAr_SLAList = [[] for j in range(len(topo_par))]  # General SLA assurance at different time intervals for different partitions
SA1 = []
SA2 = []
SA3 = []

SLAassurance1 = [[] for j in range(len(topo_par))]  # SLA assurance 1 at different time intervals for different partitions
SLAassurance2 = [[] for j in range(len(topo_par))]  # SLA assurance 2 at different time intervals
SLAassurance3 = [[] for j in range(len(topo_par))]  # SLA assurance 3 at different time intervals
GSLAList = []

#********************************************************************************************************************************
#time=0
#********************************************************************************************************************************
alpha0 = [0.0 for i in range(0, len(devices))]
Beta0 = [0.0 for i in range(0, len(devices))]
SLAPar_info = []
SPt = []
NPt = []
SP0=[]
NP0=[]
SP2=[]
NP2=[]
SLA_par = []
SLA_mem = []
t=0

for i in range(len(devices) - 1):
    SPt.append([0,0,0])
    NPt.append([0,0,0])
SP0.append(SPt)
NP0.append(NPt)

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP0[-1], NP0[-1], SLAassurance1[i], SLAassurance2[i],
                                             SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    PAr_SLAList[i].append(SLAvalue)
    SLA_par_info, SLApar, SLAmem = SLAPartitioning(SLAvalue, topo_par[i])
    SLAPar_info.append(SLA_par_info)
    SLA_par.append(SLApar)
    SLA_mem.append(SLAmem)
    GSLAList.append(SLAvalue)
numberOfServices, serviceset, appsDeadlines, appsSourceMessage, mapService2App, mapServiceId2ServiceName = SLA_aware_placement.Generating_application(t)
appsRequests, myusers = SLA_aware_placement.request_generation(t, Networkpartitioning.gatewaysDevices)
SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)



# **********************************************************************************************

#********************************************************************************************************************************
#time=1
#********************************************************************************************************************************
alpha0 = [0.0 for i in range(0, len(devices))]
Beta0 = [0.0 for i in range(0, len(devices))]
SLAPar_info = []
SPt = []
NPt = []
SLA_par = []
SLA_mem = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
t=1
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar.append(SLA_info[j]['SLA'][0])
    Vio_accept.append(SLA_info[j]['SLA'][1])
    Vio_success.append(SLA_info[j]['SLA'][2])
    SuccessPar.append(SLA_info[j]['SLA'][3])
    SatiPar.append(SLA_info[j]['SLA'][4])
    Vio_satify.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar[i], SuccessPar[i], SatiPar[i]])
    NPt.append([Vio_accept[i], Vio_success[i], Vio_satify[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar[i], 'SuccessPar': SuccessPar[i], 'SatiPar': SatiPar[i]})
    i=i+1

AcceptPar_n=Normalizing(AcceptPar)
Vio_accept_n=Normalizing(Vio_accept)
SuccessPar_n=Normalizing(SuccessPar)
Vio_success_n=Normalizing(Vio_success)
SatiPar_n = Normalizing(SatiPar)
Vio_satify_n = Normalizing(Vio_satify)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]

for item in range(len(NPt)):
    Fail_t.append((SPt[item][1] / 1800) * 3600)



SPt_info=[]
NPt_info=[]
for i in range(len(SPt)):
    SPt_info.append({"id":i, "SLA_value":SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id":i, "SLAVio_value":NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i], SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id':i, 'members': topo_par[i], 'SLAvalue': SLAvalue ,'Acceptance_rate':SA1, 'success_rate':SA2, 'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par_info, SLApar, SLAmem = SLAPartitioning(SLAvalue, topo_par[i])
    SLAPar_info.append(SLA_par_info)
    SLA_par.append(SLApar)
    SLA_mem.append(SLAmem)
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)


#********************************************************************************************************************************
#time=2
#********************************************************************************************************************************
t=2
AcceptPar1 = []
Vio_accept1 = []
SuccessPar1 = []
Vio_success1 = []
SatiPar1 = []
Vio_satify1 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
NPt_norm=[]
SPt_norm=[]

SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar1.append(SLA_info[j]['SLA'][0])
    Vio_accept1.append(SLA_info[j]['SLA'][1])
    Vio_success1.append(SLA_info[j]['SLA'][2])
    SuccessPar1.append(SLA_info[j]['SLA'][3])
    SatiPar1.append(SLA_info[j]['SLA'][4])
    Vio_satify1.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar1[i], SuccessPar1[i], SatiPar1[i]])
    NPt.append([Vio_accept1[i], Vio_success1[i], Vio_satify1[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar1[i], 'SuccessPar': SuccessPar1[i], 'SatiPar': SatiPar1[i]})
    i=i+1
AcceptPar_n=Normalizing(AcceptPar1)
Vio_accept_n=Normalizing(Vio_accept1)
SuccessPar_n=Normalizing(SuccessPar1)
Vio_success_n=Normalizing(Vio_success1)
SatiPar_n = Normalizing(SatiPar1)
Vio_satify_n = Normalizing(Vio_satify1)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

# For the previous times


app_requests = []
my_users = []
cloudId = 500
FOG_DEVICES = []
number_Of_Services = []
apps_ = []
apps_Deadlines = []
apps_Resources = []
app_storage = []
apps_SourceMessage = []
apps_TotalMIPS = []
map_Service2App = []
map_ServiceId2ServiceName = []
apps_Communities = []
services_Resources = []
service_set = []
SLAPar_info = []
SLA_par = []
SLA_mem = []
for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],
                                                 SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append(
        {'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})

    PAr_SLAList[i].append(SLAvalue)
    SLA_par_info, SLApar, SLAmem = SLAPartitioning(SLAvalue, topo_par[i])
    SLAPar_info.append(SLA_par_info)
    SLA_par.append(SLApar)
    SLA_mem.append(SLAmem)
    GSLAList.append(SLAvalue)


SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)



#********************************************************************************************************************************
#time=3
#********************************************************************************************************************************

# For the new time interval
t=3
AcceptPar2 = []
Vio_accept2 = []
SuccessPar2 = []
Vio_success2 = []
SatiPar2 = []
Vio_satify2 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar2.append(SLA_info[j]['SLA'][0])
    Vio_accept2.append(SLA_info[j]['SLA'][1])
    Vio_success2.append(SLA_info[j]['SLA'][2])
    SuccessPar2.append(SLA_info[j]['SLA'][3])
    SatiPar2.append(SLA_info[j]['SLA'][4])
    Vio_satify2.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar2[i], SuccessPar2[i], SatiPar2[i]])
    NPt.append([Vio_accept2[i], Vio_success2[i], Vio_satify2[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar2[i], 'SuccessPar': SuccessPar2[i], 'SatiPar': SatiPar2[i]})
    i=i+1


AcceptPar_n=Normalizing(AcceptPar2)
Vio_accept_n=Normalizing(Vio_accept2)
SuccessPar_n=Normalizing(SuccessPar2)
Vio_success_n=Normalizing(Vio_success2)
SatiPar_n = Normalizing(SatiPar2)
Vio_satify_n = Normalizing(Vio_satify2)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]

for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)


SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)


# **********************************************************************************************
#********************************************************************************************************************************
#time=4
#********************************************************************************************************************************

# For the new time interval
t=4
AcceptPar3 = []
Vio_accept3 = []
SuccessPar3 = []
Vio_success3 = []
SatiPar3 = []
Vio_satify3 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar3.append(SLA_info[j]['SLA'][0])
    Vio_accept3.append(SLA_info[j]['SLA'][1])
    Vio_success3.append(SLA_info[j]['SLA'][2])
    SuccessPar3.append(SLA_info[j]['SLA'][3])
    SatiPar3.append(SLA_info[j]['SLA'][4])
    Vio_satify3.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar3[i], SuccessPar3[i], SatiPar3[i]])
    NPt.append([Vio_accept3[i], Vio_success3[i], Vio_satify3[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar3[i], 'SuccessPar': SuccessPar3[i], 'SatiPar': SatiPar3[i]})
    i=i+1

AcceptPar_n=Normalizing(AcceptPar3)
Vio_accept_n=Normalizing(Vio_accept3)
SuccessPar_n=Normalizing(SuccessPar3)
Vio_success_n=Normalizing(Vio_success3)
SatiPar_n = Normalizing(SatiPar3)
Vio_satify_n = Normalizing(Vio_satify3)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]
for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)


SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3= SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)





#********************************************************************************************************************************
#time=5
#********************************************************************************************************************************

# For the new time interval
t=5
AcceptPar4 = []
Vio_accept4 = []
SuccessPar4 = []
Vio_success4 = []
SatiPar4 = []
Vio_satify4 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar4.append(SLA_info[j]['SLA'][0])
    Vio_accept4.append(SLA_info[j]['SLA'][1])
    Vio_success4.append(SLA_info[j]['SLA'][2])
    SuccessPar4.append(SLA_info[j]['SLA'][3])
    SatiPar4.append(SLA_info[j]['SLA'][4])
    Vio_satify4.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar4[i], SuccessPar4[i], SatiPar4[i]])
    NPt.append([Vio_accept4[i], Vio_success4[i], Vio_satify4[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar4[i], 'SuccessPar': SuccessPar4[i], 'SatiPar': SatiPar4[i]})

AcceptPar_n=Normalizing(AcceptPar4)
Vio_accept_n=Normalizing(Vio_accept4)
SuccessPar_n=Normalizing(SuccessPar4)
Vio_success_n=Normalizing(Vio_success4)
SatiPar_n = Normalizing(SatiPar4)
Vio_satify_n = Normalizing(Vio_satify4)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]

for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)



# **********************************************************************************************
#********************************************************************************************************************************
#time=6
#********************************************************************************************************************************

# For the new time interval
t=6
AcceptPar5 = []
Vio_accept5 = []
SuccessPar5 = []
Vio_success5 = []
SatiPar5 = []
Vio_satify5 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar5.append(SLA_info[j]['SLA'][0])
    Vio_accept5.append(SLA_info[j]['SLA'][1])
    Vio_success5.append(SLA_info[j]['SLA'][2])
    SuccessPar5.append(SLA_info[j]['SLA'][3])
    SatiPar5.append(SLA_info[j]['SLA'][4])
    Vio_satify5.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar5[i], SuccessPar5[i], SatiPar5[i]])
    NPt.append([Vio_accept5[i], Vio_success5[i], Vio_satify5[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar5[i], 'SuccessPar': SuccessPar5[i], 'SatiPar': SatiPar5[i]})

AcceptPar_n=Normalizing(AcceptPar5)
Vio_accept_n=Normalizing(Vio_accept5)
SuccessPar_n=Normalizing(SuccessPar5)
Vio_success_n=Normalizing(Vio_success5)
SatiPar_n = Normalizing(SatiPar5)
Vio_satify_n = Normalizing(Vio_satify5)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]

for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})


for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)




#********************************************************************************************************************************
#time=7
#********************************************************************************************************************************

# For the new time interval
t=7
AcceptPar6 = []
Vio_accept6 = []
SuccessPar6 = []
Vio_success6 = []
SatiPar6 = []
Vio_satify6 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar6.append(SLA_info[j]['SLA'][0])
    Vio_accept6.append(SLA_info[j]['SLA'][1])
    Vio_success6.append(SLA_info[j]['SLA'][2])
    SuccessPar6.append(SLA_info[j]['SLA'][3])
    SatiPar6.append(SLA_info[j]['SLA'][4])
    Vio_satify6.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar6[i], SuccessPar6[i], SatiPar6[i]])
    NPt.append([Vio_accept6[i], Vio_success6[i], Vio_satify6[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar6[i], 'SuccessPar': SuccessPar6[i], 'SatiPar': SatiPar6[i]})

AcceptPar_n=Normalizing(AcceptPar6)
Vio_accept_n=Normalizing(Vio_accept6)
SuccessPar_n=Normalizing(SuccessPar6)
Vio_success_n=Normalizing(Vio_success6)
SatiPar_n = Normalizing(SatiPar6)
Vio_satify_n = Normalizing(Vio_satify6)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]

for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)



#********************************************************************************************************************************
#time=8
#********************************************************************************************************************************

# For the new time interval
t=8
AcceptPar7 = []
Vio_accept7 = []
SuccessPar7 = []
Vio_success7 = []
SatiPar7 = []
Vio_satify7 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar7.append(SLA_info[j]['SLA'][0])
    Vio_accept7.append(SLA_info[j]['SLA'][1])
    Vio_success7.append(SLA_info[j]['SLA'][2])
    SuccessPar7.append(SLA_info[j]['SLA'][3])
    SatiPar7.append(SLA_info[j]['SLA'][4])
    Vio_satify7.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar7[i], SuccessPar7[i], SatiPar7[i]])
    NPt.append([Vio_accept7[i], Vio_success7[i], Vio_satify7[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar7[i], 'SuccessPar': SuccessPar7[i], 'SatiPar': SatiPar7[i]})


AcceptPar_n=Normalizing(AcceptPar7)
Vio_accept_n=Normalizing(Vio_accept7)
SuccessPar_n=Normalizing(SuccessPar7)
Vio_success_n=Normalizing(Vio_success7)
SatiPar_n = Normalizing(SatiPar7)
Vio_satify_n = Normalizing(Vio_satify7)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]
for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)


#********************************************************************************************************************************
#time=9
#********************************************************************************************************************************

# For the new time interval
t=9
AcceptPar8 = []
Vio_accept8 = []
SuccessPar8 = []
Vio_success8 = []
SatiPar8 = []
Vio_satify8 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]

devices = Networkpartitioning.get_devices()
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar8.append(SLA_info[j]['SLA'][0])
    Vio_accept8.append(SLA_info[j]['SLA'][1])
    Vio_success8.append(SLA_info[j]['SLA'][2])
    SuccessPar8.append(SLA_info[j]['SLA'][3])
    SatiPar8.append(SLA_info[j]['SLA'][4])
    Vio_satify8.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar8[i], SuccessPar8[i], SatiPar8[i]])
    NPt.append([Vio_accept8[i], Vio_success8[i], Vio_satify8[i]])
    SLA_Dict.append({'id': i, 'AcceptPar': AcceptPar8[i], 'SuccessPar': SuccessPar8[i], 'SatiPar': SatiPar8[i]})
print("SLA_Dict in time window", t, ":", SLA_Dict)

AcceptPar_n=Normalizing(AcceptPar8)
Vio_accept_n=Normalizing(Vio_accept8)
SuccessPar_n=Normalizing(SuccessPar8)
Vio_success_n=Normalizing(Vio_success8)
SatiPar_n = Normalizing(SatiPar8)
Vio_satify_n = Normalizing(Vio_satify8)

for i in range(len(devices) - 1):
    SPt_norm.append([AcceptPar_n[i], SuccessPar_n[i], SatiPar_n[i]])
    NPt_norm.append([Vio_accept_n[i], Vio_success_n[i], Vio_satify_n[i]])

SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]
for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

for i in range(len(topo_par)):
    SLAvalue, SA1, SA2, SA3 = SLACalculation(topo_par[i], i, SP[-1], NP[-1], SLAassurance1[i], SLAassurance2[i],SLAassurance3[i])  # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
    Sinf_t.append({'topo_id': i, 'members': topo_par[i], 'SLAvalue': SLAvalue, 'Acceptance_rate': SA1, 'success_rate': SA2,'satisfation_rate': SA3})
    PAr_SLAList[i].append(SLAvalue)
    SLA_par = SLAPartitioning(SLAvalue, topo_par[i])
    GSLAList.append(SLAvalue)

SLA_aware_placement.SLA_aware_placement(t,G,Delay, sortnettime,devices, topo_mem,topo_par, Fog_community, SLAPar_info, Networkpartitioning.gatewaysDevices,
                                      Networkpartitioning.centralityValuesNoOrdered, numberOfServices, serviceset, appsDeadlines,
                                      appsSourceMessage, mapService2App, mapServiceId2ServiceName, appsRequests)



# **********************************************************************************************

AcceptPar9 = []
Vio_accept9 = []
SuccessPar9 = []
Vio_success9 = []
SatiPar9 = []
Vio_satify9 = []
SPt = []
NPt = []
SLA_Dict=[]
Sinf_t=[]
SPt_norm=[]
NPt_norm=[]
devices = Networkpartitioning.get_devices()
t=10
SLA_file="SLA-info/SLAInfo"+str(t)+".json"
with open(SLA_file, "r") as json_file:
    SLA_info = json.load(json_file)
i=0
for j in range(len(SLA_info)):
    AcceptPar9.append(SLA_info[j]['SLA'][0])
    Vio_accept9.append(SLA_info[j]['SLA'][1])
    Vio_success9.append(SLA_info[j]['SLA'][2])
    SuccessPar9.append(SLA_info[j]['SLA'][3])
    SatiPar9.append(SLA_info[j]['SLA'][4])
    Vio_satify9.append(SLA_info[j]['SLA'][5])
    SPt.append([AcceptPar9[i], SuccessPar9[i], SatiPar9[i]])
    NPt.append([Vio_accept9[i], Vio_success9[i], Vio_satify9[i]])
    SPt_norm= Normalizing(SPt)
    NPt_norm=Normalizing(NPt)
SP.append(SPt_norm)
NP.append(NPt_norm)
SP2.append(SPt)
NP2.append(NPt)
Fail_t=[]
for item in range(len(NPt)):
    Fail_t.append((SPt[item][1]/1800)*3600)

SPt_info = []
NPt_info = []
for i in range(len(SPt)):
    SPt_info.append({"id": i, "SLA_value": SPt[i]})

for i in range(len(NPt)):
    NPt_info.append({"id": i, "SLAVio_value": NPt[i]})

