import math
# This calculates the SLA assurance of devices in one network partition at one time interval
import numpy as np


SLAList=[]
SLApar=3
SLAassurance1=[] #Matrix of SLA assurance of devices base on the acceptence parameters in a network partition at differnet time intervals
SLAassurance2=[] #Matrix of SLA assurance of devices base on the succcess parameters in a network partition at differnet time intervals
SLAassurance3=[] #Matrix of  SLA assurance of devices base on the satisfaction parameters in a network partition at differnet time intervals
SLAvalue=[] #matrix of SLA values of devices in a partition
SV=[]# list of final SLA assurance value of different devices in a partition


def SigmoidSLA(i,SP,NP):
    credit = 1 / (1 + np.exp(-(SP - NP)))
    return credit


def sigma(first, last):
    sum = 0
    for t in range(first, last + 1):
        sum += (1-(1/(t+1)))
    return sum

def EntropyCalulation(j,SLAvalue,par):
    sum=0.0
    #print("This SLAValue: ",SLAvalue)
    for i in range(len(par)):
        #print("This SLAValue for i: ",i,"and j: ",j,SLAvalue[i][j])
        sum= sum+(SLAvalue[i][j]*(math.log(SLAvalue[i][j])))
    Entropy= (1/SLApar)*(sum)
    Dv=1-Entropy
    return Dv


def weightCalculation(SLAvalue,par):
    weight = []
    DV=[]
    SumDV=0.0
    for j in range(SLApar):
        deviation= EntropyCalulation(j,SLAvalue,par)
        DV.append(deviation)
    for j in range(SLApar):
        SumDV=SumDV+DV[j]
    for j in range(SLApar):
        weight.append(DV[j]/SumDV)
    return weight


def SLACalculation(par,i,SP,NP, SLAassurance1,SLAassurance2,SLAassurance3):
    #This function gives the general value for SLA assurance at time t regarding previous SLA values, and SLA values at this time interval

    #i is the number of partition that its SLA assurance will be calculated
    SLAvalue = []  # matrix of SLA values of devices in a partition
    SV = []  # list of final SLA assurance value of different devices in a partition
    SLAList = []
    SLApar = 3
    #SLAassurance1 = []  # Matrix of SLA assurance of devices base on the acceptence parameters in a network partition at differnet time intervals
    #SLAassurance2 = []  # Matrix of SLA assurance of devices base on the succcess parameters in a network partition at differnet time intervals
    #SLAassurance3 = []  #Matrix of  SLA assurance of devices base on the satisfaction parameters in a network partition at differnet time intervals
    SAt1=[]
    SAt2=[]
    SAt3=[]
    SA1 = [0.0]*len(par)
    SA2 = [0.0]*len(par)
    SA3 = [0.0]*len(par)
    W=[]
    for i in (par):
        for j in range(SLApar):
            if j==0:
                #print(par)
                #print('This is i: ', i)
                SAt1.append(SigmoidSLA(i,SP[i][j],NP[i][j]))
            elif j==1:
                SAt2.append(SigmoidSLA(i,SP[i][j],NP[i][j]))
            elif j==2:
                SAt3.append(SigmoidSLA(i,SP[i][j],NP[i][j]))
    #add the SLA assurance value of devices in the network partition at time t
    SLAassurance1.append(SAt1)
    SLAassurance2.append(SAt2)
    SLAassurance3.append(SAt3)
    for t in range(len(SLAassurance1)):
        i=t+1
        W.append((1-(1/(i+1)))/sigma(1,len(SLAassurance1)))
    #print(SLAassurance1)
    #calulate the SLA assurance of each device in the partition in time t based on previous time intervals
    for j in range(SLApar):
        for i in range(len(par)):
            for t in range(len(SLAassurance1)):
                if j==0:
                    SA1[i]= SA1[i]+ (W[t]* SLAassurance1[t][i])
                elif j==1:
                    SA2[i]= SA2[i]+ (W[t]* SLAassurance2[t][i])
                elif j==2:
                    SA3[i]= SA3[i]+ (W[t]* SLAassurance3[t][i])

    for i in range(len(par)):
        SLAvalue.append([SA1[i],SA2[i],SA3[i]])
    Y=weightCalculation(SLAvalue,par)
    # calculate weight of different parameters
    # calulate the general SLA assurance of each device in the partition at time t
    for i in range(len(par)):
        GSV=0.0
        for j in range(SLApar):
            GSV=GSV+(Y[j]*SLAvalue[i][j])
        SV.append(GSV)
    return SV,SAt1, SAt2, SAt3


#SLAvalue= SLACalculation(partition[0],SP, NP) # The general SLA assurance of each device in the partition at time t based on SLA value in previous time intervals
#SLAList.append(SLAvalue)
#print (SLAvalue)
