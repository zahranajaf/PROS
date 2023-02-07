import numpy
import json


def comp_times_ecommerce(task,dev_new, dev1, dev2, dev3, num_of_src):
        #print(dev_new, " ",dev1, " ",dev2, " ", dev3)
        LAT1=0; BW1=0; LAT2=0; BW2=0; LAT3=0; BW3=0 
        alloc_file = "D:\\00Research\\00Fog\\004-Zara\\Her SLA\\TimeIntervals-large - diffStress\\02Heavy\\3\\No\\networkDefinition2.json"
        with open(alloc_file, "r") as json_file:
                network = json.load(json_file)
        for i in range(len((network["link"]))):
                if ((network["link"][i]["s"] == dev1 and network["link"][i]["d"] == dev_new ) or (network["link"][i]["s"] == dev_new and network["link"][i]["d"] == dev1 )):
                        #print(dev1," ",dev_new)
                        LAT1 = network["link"][i]["PR"]
                        BW1 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and network["link"][i]["d"] == dev_new ) or (network["link"][i]["s"] == dev_new and network["link"][i]["d"] == dev2 )) :
                        LAT2 = network["link"][i]["PR"]
                        BW2 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and network["link"][i]["d"] == dev_new ) or (network["link"][i]["s"] == dev_new and network["link"][i]["d"] == dev3 )):
                        LAT3 = network["link"][i]["PR"]
                        BW3 = network["link"][i]["BW"]
        if (dev1 == dev_new ):
                LAT1 = 0.5e-3
                BW1 = 13000
        if (dev2 == dev_new ):
                LAT2 = 0.5e-3
                BW2 = 13000
        if (dev3 == dev_new ):
                LAT3 = 0.5e-3
                BW3 = 13000
        #####################################SockShop####################################
        
        #       0        1          2           3    4          5        6         7       8     10   11      12
        #     Exo(lg)  Exo(med)  Exo(smal) Exo(lg) Exo(lg) Exo(Klag)    EGS     Lenovo  Jetson RPi4  Exo(lg) Exo(lg)
        '''time =[  [0.27,     0.4,      0.44,   0.27, 0.27,     0.28,     0.17,   0.33,    1.9, 2.16,   0.27, 0.27], # encode 200
                [0.41,     0.42,     0.44,   0.41, 0.41,     0.5,      0.39,   0.35,      2,  3.8,   0.41, 0.41], # frame 200
                [0.25,     0.26,     0.29,   0.25, 0.25,     0.28,     0.225,  0.282,   1.94, 1.05,   0.25, 0.25], # inference
                [0.001,    0.001,    0.001,  0.001, 0.001,     0.001,    0.001,   0.001,  0.001, 0.001,  0.001, 0.001], #Low-acc. training
                [0.001,    0.001,    0.001,  0.001, 0.001,     0.001,    0.001,   0.001,  0.001, 0.001,  0.001, 0.001]  #High-acc. training
        ]'''
        time = [[0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153],
                [0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153],
                [0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153],
                [0.055556, 0.056338, 0.108108, 0.055556, 0.055556, 0.033333, 0.006897, 0.018433, 0.098039, 0.078431, 0.013889],
                [0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153],
                [0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153],
                [0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153],
                [0.048611, 0.049296, 0.094595, 0.048611, 0.048611, 0.029167, 0.006034, 0.016129, 0.085784, 0.068627, 0.012153]]
        
        index_of_segment = 3
        data_size = [6.22*1024*8, 8.48*1024*8, 11.25*1024*8, 22.48*1024*8] # bits
        SIZE = 1

        # Converting string to list
        tasks0 = ["Web-UI", "Login", "Orders", "Shopping-cart", "Catalogue", "Accounts", "Payment", "Shipping"]  # sys.argv[1].strip("][").split(",")
        #print((tasks0.index(task)))

        T = [1 for i in range(len(time[0]))]
        Tm = [1 for i in range(len(time[0]))]
        Tr = [1 for i in range(len(time[0]))]    
        Tq = [1 for i in range(len(time[0]))]

        #print(dev_new, " ", int(dev_new/10))

        Tm[int(dev_new/10)] = time[tasks0.index(task)][int(dev_new/10)]  # data size: 8sec video.
        #print(Tm[int(dev_new/10)])
        Tr[int(dev_new/10)] = max(((0.000001) * (SIZE*data_size[index_of_segment]) / BW1) + ((0.000001) *LAT1),
                                        ((0.000001) * (SIZE*data_size[index_of_segment]) / BW2) + ((0.000001) *LAT2),
                                        ((0.000001) * (SIZE*data_size[index_of_segment]) / BW3) + ((0.000001) *LAT3))
        
        Tq[int(dev_new/10)] = num_of_src*Tr[int(dev_new/10)] 
        T[int(dev_new/10)] = numpy.round(numpy.round(Tm[int(dev_new/10)], 4) + Tq[int(dev_new/10)] + numpy.round(Tr[int(dev_new/10)], 4), 4)
      
        return (Tm, Tr, Tq, T)
#comp_times_ecommerce(0,0,0,0,0)