import numpy
import json
import sys
sys.path.append('./diff_times')
from diff_times import  comp_times
sys.path.append('./diff_times_ecommerce')
from diff_times_ecommerce import  comp_times_ecommerce

import warnings
warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning) 


num_of_src = 10
res_num=12
app_num=30
for tt in range(1):
    alloc_file = "D:\\00Research\\00Fog\\TimeIntervals-large - diffStress\\00Light\\2\\Pros\\allocDefinition2.json"
    with open(alloc_file, "r") as json_file:
        content_app = json.load(json_file)
    #print(len(content_app['initialAllocation']))
    app1 = ["Web-UI", "Login", "Orders", "Shopping-cart", "Catalogue", "Accounts", "Payment", "Shipping"]
    service_num_app1=8
    T_1 = [[[[0] for k in range(res_num)] for i in range(service_num_app1)] for j in range(app_num)]
    Tm_1 = [[[[0] for k in range(res_num)] for i in range(service_num_app1)] for j in range(app_num)]
    Tq_1 = [[[[0] for k in range(res_num)] for i in range(service_num_app1)] for j in range(app_num)]
    Tr_1 = [[[[0] for k in range(res_num)] for i in range(service_num_app1)] for j in range(app_num)]
    dev_1 = [[[0] for i in range(service_num_app1)] for j in range(app_num)]
    compl_time = [0 for k in range(app_num)]

    app2 = ["encode_20000", "frame_20000", "lowtrain", "hightrain", "inference", "transcode", "package"]
    service_num_app2=7
    T_2 = [[[[0] for k in range(res_num)] for i in range(service_num_app2)] for j in range(app_num)]
    Tm_2 = [[[[0] for k in range(res_num)] for i in range(service_num_app2)] for j in range(app_num)]
    Tq_2 = [[[[0] for k in range(res_num)] for i in range(service_num_app2)] for j in range(app_num)]
    Tr_2 = [[[[0] for k in range(res_num)] for i in range(service_num_app2)] for j in range(app_num)]
    dev_2 = [[[0] for i in range(service_num_app2)] for j in range(app_num)]
    #compl_time_2 = 0
    #print(len(content_app['initialAllocation']))
    for service in range(len(content_app['initialAllocation'])):
        if (service < 120):
            #print(service)
            m=content_app['initialAllocation'][service]["module_name"]
            part1 = int(m.split('_')[1])
            task =(part1) % service_num_app1
            #print(content_app['initialAllocation'][service])
            #print(app1[task])
            ###print(task)
            
            app = int(content_app['initialAllocation'][service]["app"])
            dev_1[app][task] = content_app['initialAllocation'][service]["id_resource"]
            if dev_1[app][task]==1000:
                dev_1[app][task]=10
            #print(dev_1[app][task])
            if (task == 0):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], 7, 7, 7, num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] #+ max(T_1[app][task][int(numpy.floor(dev_1[app][task]/10))],T_1[app][task][int(numpy.floor(dev_1[app][task]/10))],T_1[app][task][int(numpy.floor(dev_1[app][task]/10))],T_1[app][task][int(numpy.floor(dev_1[app][task]/10))])
            elif(task == 1):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-1], dev_1[app][task-1], dev_1[app][task-1], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-1][int(numpy.floor(dev_1[app][task-1]/10))],T_1[app][task-1][int(numpy.floor(dev_1[app][task-1]/10))],T_1[app][task-1][int(numpy.floor(dev_1[app][task-1]/10))])
            elif(task == 2):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-2], dev_1[app][task-2], dev_1[app][task-2], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-2][int(numpy.floor(dev_1[app][task-2]/10))],T_1[app][task-2][int(numpy.floor(dev_1[app][task-2]/10))],T_1[app][task-2][int(numpy.floor(dev_1[app][task-2]/10))])
            elif(task == 3):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-1], dev_1[app][task-3], dev_1[app][task-3], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-1][int(numpy.floor(dev_1[app][task-1]/10))],T_1[app][task-3][int(numpy.floor(dev_1[app][task-3]/10))],T_1[app][task-3][int(numpy.floor(dev_1[app][task-3]/10))])
            elif(task == 4):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-4], dev_1[app][task-4], dev_1[app][task-4], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))],T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))],T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))])
            elif(task == 5):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-3], dev_1[app][task-4], dev_1[app][task-5], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-3][int(numpy.floor(dev_1[app][task-3]/10))],T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))],T_1[app][task-5][int(numpy.floor(dev_1[app][task-5]/10))])
            elif(task == 6):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-4], dev_1[app][task-4], dev_1[app][task-4], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))],T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))],T_1[app][task-4][int(numpy.floor(dev_1[app][task-4]/10))])
            elif(task == 7):
                Tm_1[app][task], Tr_1[app][task], Tq_1[app][task], T_1[app][task] = comp_times_ecommerce(app1[task],dev_1[app][task], dev_1[app][task-5], dev_1[app][task-5], dev_1[app][task-5], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]= T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + T_1[app][task][int(numpy.floor(dev_1[app][task]/10))]
                compl_time[app] +=  T_1[app][task][int(numpy.floor(dev_1[app][task]/10))] + max(T_1[app][task-5][int(numpy.floor(dev_1[app][task-5]/10))],T_1[app][task-5][int(numpy.floor(dev_1[app][task-5]/10))],T_1[app][task-5][int(numpy.floor(dev_1[app][task-5]/10))])
                #print(app," ",compl_time[app])
            #dev_1[app][task] = content_app['initialAllocation'][service]["id_resource"]
            #if dev_1[app][task]==1000:
            #    #dev_1[app][task]=10
            #    print(app," ",task," ",10," ",T_1[app][task][10])
            #else:
            ############print(app," ",task," ",dev_1[app][task]," ",T_1[app][task][int(numpy.floor(dev_1[app][task]/10))])
        else:
            m=content_app['initialAllocation'][service]["module_name"]
            part1 = int(m.split('_')[1])
            task =( part1 - 120) % service_num_app2
            #print(content_app['initialAllocation'][service])
            #print(app2[task])
            #print(t1)
            
            app = int(content_app['initialAllocation'][service]["app"])
            #print(app)
            if (task == 0):
                Tm_2[app][task], Tr_2[app][task], Tq_1[app][task], T_2[app][task] = comp_times(app2[task], 7, 7, 7, num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]= T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]
                compl_time[app] +=  T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]
                #print(task, " ",app," ",Tm_2[app][task][int(numpy.floor(dev_1[app][task]/10))]," ", Tr_2[app][task][int(numpy.floor(dev_1[app][task]/10))], " ",T_2[app][task][int(numpy.floor(dev_1[app][task]/10))])
            elif(task == 4):
                Tm_2[app][task], Tr_2[app][task], Tq_1[app][task], T_2[app][task] = comp_times(app2[task], dev_2[app][task-1], dev_2[app][task-2], dev_2[app][task-2], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]= T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]
                compl_time[app] +=  T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + max(T_2[app][task-1][int(numpy.floor(dev_1[app][task-1][0]/10))],T_2[app][task-2][int(numpy.floor(dev_1[app][task-2][0]/10))],T_2[app][task-2][int(numpy.floor(dev_1[app][task-2][0]/10))])
                #print(task, " ",app," ",Tm_2[app][task][int(numpy.floor(dev_1[app][task]/10))]," ", Tr_2[app][task][int(numpy.floor(dev_1[app][task]/10))], " ",T_2[app][task][int(numpy.floor(dev_1[app][task]/10))])                
            elif(task == 5):
                #print(task, " ",app)
                Tm_2[app][task], Tr_2[app][task], Tq_1[app][task], T_2[app][task] = comp_times(app2[task], dev_2[app][task-1], dev_2[app][task-2], dev_2[app][task-3], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]= T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]
                compl_time[app] +=  T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + max(T_2[app][task-1][int(numpy.floor(dev_1[app][task-1][0]/10))],T_2[app][task-2][int(numpy.floor(dev_1[app][task-2][0]/10))],T_2[app][task-3][int(numpy.floor(dev_1[app][task-3][0]/10))])
                #print(task, " ",app," ", Tm_2[app][task][int(numpy.floor(dev_1[app][task]/10))]," ", Tr_2[app][task][int(numpy.floor(dev_1[app][task]/10))], " ",T_2[app][task][int(numpy.floor(dev_1[app][task]/10))])
            else:
                Tm_2[app][task], Tr_2[app][task], Tq_1[app][task], T_2[app][task] = comp_times(app2[task], dev_2[app][task-1], dev_2[app][task-1], dev_2[app][task-1], num_of_src)
                if (content_app['initialAllocation'][service]["Status"] == "Crashed"):
                    T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]= T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))]
                compl_time[app] +=  T_2[app][task][int(numpy.floor(dev_1[app][task][0]/10))] + max(T_2[app][task-1][int(numpy.floor(dev_1[app][task-1][0]/10))],T_2[app][task-1][int(numpy.floor(dev_1[app][task-1][0]/10))],T_2[app][task-1][int(numpy.floor(dev_1[app][task-1][0]/10))])
                #print(task, " ",app, " ", Tm_2[app][task][int(numpy.floor(dev_1[app][task]/10))]," ", Tr_2[app][task][int(numpy.floor(dev_1[app][task]/10))], " ",T_2[app][task][int(numpy.floor(dev_1[app][task]/10))])
                #if(task == 6):
                #    print(app," ",compl_time[app])
            dev_2[app][task] = content_app['initialAllocation'][service]["id_resource"]
            '''if dev_2[app][task]==1000:
                dev_2[app][task]=10
                print(app," ",task," ",10," ",T_2[app][task][10])
            #else:
                print(app," ",task," ",dev_2[app][task]," ",T_2[app][task][int(numpy.floor(dev_1[app][task]/10))])'''

#{"module_name": "0_0", "app": "0", "id_resource": 6},
print(numpy.round(compl_time[0],4),",",numpy.round(compl_time[1],4),",",numpy.round(compl_time[2],4),",",numpy.round(compl_time[3],4),",",numpy.round(compl_time[4],4),",",numpy.round(compl_time[5],4),",",numpy.round(compl_time[6],4),",",numpy.round(compl_time[7],4),",",numpy.round(compl_time[8],4),",",numpy.round(compl_time[9],4),",")
print(numpy.round(compl_time[10],4),",",numpy.round(compl_time[11],4),",",numpy.round(compl_time[12],4),",",numpy.round(compl_time[13],4),",",numpy.round(compl_time[14],4),",",numpy.round(compl_time[15],4),",",numpy.round(compl_time[16],4),",",numpy.round(compl_time[17],4),",",numpy.round(compl_time[18],4),",",numpy.round(compl_time[19],4),",")
print(numpy.round(compl_time[20],4),",",numpy.round(compl_time[21],4),",",numpy.round(compl_time[22],4),",",numpy.round(compl_time[23],4),",",numpy.round(compl_time[24],4),",",numpy.round(compl_time[25],4),",",numpy.round(compl_time[26],4),",",numpy.round(compl_time[27],4),",",numpy.round(compl_time[28],4),",",numpy.round(compl_time[29],4))

print(numpy.round(numpy.average(compl_time),4))
