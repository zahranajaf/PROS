import numpy
import json


def comp_times(task, dev1, dev2, dev3, num_of_src):
    #print(" ",dev1, " ",dev2, " ", dev3)
    if (type(dev1) == list):
        dev1 = dev1[0]
    alloc_file = "D:\\00Research\\00Fog\\004-Zara\\Her SLA\\TimeIntervals-large - diffStress\\02Heavy\\4\\Pros\\networkDefinition2.json"
    with open(alloc_file, "r") as json_file:
        network = json.load(json_file)
    LAT0=0; BW0=0; LAT20=0; BW20=0; LAT30=0; BW30=0 
    LAT1=0; BW1=0; LAT21=0; BW21=0; LAT31=0; BW31=0
    LAT2=0; BW2=0; LAT22=0; BW22=0; LAT32=0; BW32=0 
    LAT3=0; BW3=0; LAT23=0; BW23=0; LAT33=0; BW33=0 
    LAT4=0; BW4=0; LAT24=0; BW24=0; LAT34=0; BW34=0 
    LAT5=0; BW5=0; LAT25=0; BW25=0; LAT35=0; BW35=0 
    LAT6=0; BW6=0; LAT26=0; BW26=0; LAT36=0; BW36=0 
    LAT7=0; BW7=0; LAT27=0; BW27=0; LAT37=0; BW37=0 
    LAT8=0; BW8=0; LAT28=0; BW28=0; LAT38=0; BW38=0 
    LAT9=0; BW9=0; LAT29=0; BW29=0; LAT39=0; BW39=0 
    LAT10=0; BW10=0; LAT210=0; BW210=0; LAT310=0; BW310=0 
    LAT11=0; BW11=0; LAT211=0; BW211=0; LAT311=0; BW311=0 
    #       0        1          2           3    4          5        6         7       8     10   11     12
    #     Exo(lg)  Exo(med)  Exo(smal) Exo(lg) Exo(lg) Exo(Klag)    EGS     Lenovo  Jetson RPi4 Exo(lg) Exo(lg)
    encode_200 = [0.27,     0.4,      0.44,   0.27, 0.27,     0.28,     0.17,   0.33,    1.9, 2.16, 0.27, 0.27] # encode 200
    encode_1500 = [0.62, 0.65, 1.14, 0.62, 0.62, 0.5, 0.36, 0.42, 2.63, 3.19, 0.43]  # seconds
    encode_3000 = [0.89, 0.9, 1.6, 0.89, 0.89, 0.63, 0.47, 0.59, 3.48, 4.4, 0.55]  # seconds
    encode_6500 = [2.58, 2.7, 4.9, 2.58, 2.58, 1.45, 1.22, 1.59, 9.68, 11.8, 1.3]  # seconds
    encode_20000 = [6.1, 6.2, 11, 6.1, 6.1, 3.1,2.7, 3.16, 20.64, 28, 2.6]  # seconds

    #       0        1          2           3    4          5        6         7       8     10   11
    #     Exo(lg)  Exo(med)  Exo(smal) Exo(lg) Exo(lg) Exo(Klag)    EGS     Lenovo  Jetson RPi4 Exo(lg)
    frame_200 = [0.41,     0.42,     0.44,   0.41, 0.41,     0.5,      0.39,   0.35,      2,  3.8,   0.41,   0.41] # frame 200
    frame_1500 = [1.7,1.8,2,1.8, 2,2.46,2.1, 9.4, 11, 1.83]
    frame_3000 = [2.5,2.6,2.8, 2.5, 2.5, 2.9,3.8,3.2, 14, 14, 2]
    frame_6500 = [8.6,9.4,9.8,8.7, 8.7, 9.9,14.2,11.8, 55, 49, 8.4, 8.7, 8.7]
    frame_20000 = [18,18.2,21,18.5,18.5, 20.9,31,26, 117, 112, 17.5,18.5,18.5]

    #       0        1          2           3    4          5        6         7       8     10   11
    #     Exo(lg)  Exo(med)  Exo(smal) Exo(lg) Exo(lg) Exo(Klag)    EGS     Lenovo  Jetson RPi4 Exo(lg)
    inference = [0.25,     0.26,     0.29,   0.25, 0.25,     0.28,     0.225,  0.282,   1.94, 1.05, 0.25, 0.25] # inference
    lowtrain = [0.001,    0.001,    0.001,  0.001, 0.001,     0.001,    0.001,   0.001,  0.001, 0.001, 0.001, 0.001] #Low-acc. training
    hightrain = [0.001,    0.001,    0.001,  0.001, 0.001,     0.001,    0.001,   0.001,  0.001, 0.001, 0.001, 0.001]  #High-acc. training
    #print(len(lowtrain))
    # https://aws.amazon.com/kinesis/data-firehose/pricing/?nc=sn&loc=3

    # seg_size = 80000 #(10KB)
    # video_size = 8000000000 #(1GB)
    index_of_segment = 0
    seg_size = [286720, 2457600, 3440640, 14400000, 20971520]  # bits
    video_size = [2000000, 14000000, 28000000, 60000000, 204800000]  # bits

    # tasks0 = sys.argv[1].strip("][").split(",")
    ####print(tasks0)

    # resources = sys.argv[3].strip("][").split(",")

    # Converting string to list
    tasks0 = ["encode_20000", "frame_20000", "lowtrain", "hightrain", "inference", "transcode", "package"]  # sys.argv[1].strip("][").split(",")
    # print(type(tasks0))

    num_of_apps = 1
    newtasks = [0 for i in range(len(tasks0) * num_of_apps)]
    for k in range(num_of_apps):
        for i in range(len(tasks0)):
            newtasks[i + (k * len(tasks0))] = tasks0[i] + str(k)

    #              0	       1	      2      		3      4        5        6       7		8      9      10
    resources = ["V-Exo(large)", "V-Exo(large)", "V-Exo(med)",  "V-Exo(small)", "Z-Exo(large)", "M-Exo(large)", "Edge-kla", "AAU(large)", "Lenovo",  "NJN",   "RPi4",   "S-Exo(large)",   "S-Exo(large)"]
    # resources = sys.argv[2].strip("][").split(",")

    for i in range(len((network["link"]))):
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 0 ) or (int(network["link"][i]["s"]/10) == 0 and network["link"][i]["d"] == dev1 )):
                        LAT0 = network["link"][i]["PR"]
                        BW0 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 1 ) or (int(network["link"][i]["s"]/10) == 1 and network["link"][i]["d"] == dev1 )) :
                        LAT1 = network["link"][i]["PR"]
                        BW1 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 2 ) or (int(network["link"][i]["s"]/10) == 2 and network["link"][i]["d"] == dev1 )):
                        LAT2 = network["link"][i]["PR"]
                        BW2 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 3 ) or (int(network["link"][i]["s"]/10) == 3 and network["link"][i]["d"] == dev1 )):
                        LAT3 = network["link"][i]["PR"]
                        BW3 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 4 ) or (int(network["link"][i]["s"]/10) == 4 and network["link"][i]["d"] == dev1 )):
                        LAT4 = network["link"][i]["PR"]
                        BW4 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 5 ) or (int(network["link"][i]["s"]/10) == 5 and network["link"][i]["d"] == dev1 )):
                        LAT5 = network["link"][i]["PR"]
                        BW5 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 6 ) or (int(network["link"][i]["s"]/10) == 6 and network["link"][i]["d"] == dev1 )):
                        LAT6 = network["link"][i]["PR"]
                        BW6 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 7 ) or (int(network["link"][i]["s"]/10) == 7 and network["link"][i]["d"] == dev1 )):
                        LAT7 = network["link"][i]["PR"]
                        BW7 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 8 ) or (int(network["link"][i]["s"]/10) == 8 and network["link"][i]["d"] == dev1 )):
                        LAT8 = network["link"][i]["PR"]
                        BW8 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 9 ) or (int(network["link"][i]["s"]/10) == 9 and network["link"][i]["d"] == dev1 )):
                        LAT9 = network["link"][i]["PR"]
                        BW9 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 10 ) or (int(network["link"][i]["s"]/10) == 10 and network["link"][i]["d"] == dev1 )):
                        LAT10 = network["link"][i]["PR"]
                        BW10 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev1 and int(network["link"][i]["d"]/10) == 11 ) or (int(network["link"][i]["s"]/10) == 11 and network["link"][i]["d"] == dev1 )):
                        LAT11 = network["link"][i]["PR"]
                        BW11 = network["link"][i]["BW"]

                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 0 ) or (int(network["link"][i]["s"]/10) == 0 and network["link"][i]["d"] == dev2 )):
                        LAT20 = network["link"][i]["PR"]
                        BW20 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 1 ) or (int(network["link"][i]["s"]/10) == 1 and network["link"][i]["d"] == dev2 )) :
                        LAT21 = network["link"][i]["PR"]
                        BW21 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 2 ) or (int(network["link"][i]["s"]/10) == 2 and network["link"][i]["d"] == dev2 )):
                        LAT22 = network["link"][i]["PR"]
                        BW22 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 3 ) or (int(network["link"][i]["s"]/10) == 3 and network["link"][i]["d"] == dev2 )):
                        LAT23 = network["link"][i]["PR"]
                        BW23 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 4 ) or (int(network["link"][i]["s"]/10) == 4 and network["link"][i]["d"] == dev2 )):
                        LAT24 = network["link"][i]["PR"]
                        BW24 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 5 ) or (int(network["link"][i]["s"]/10) == 5 and network["link"][i]["d"] == dev2 )):
                        LAT25 = network["link"][i]["PR"]
                        BW25 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 6 ) or (int(network["link"][i]["s"]/10) == 6 and network["link"][i]["d"] == dev2 )):
                        LAT26 = network["link"][i]["PR"]
                        BW26 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 7 ) or (int(network["link"][i]["s"]/10) == 7 and network["link"][i]["d"] == dev2 )):
                        LAT27 = network["link"][i]["PR"]
                        BW27 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 8 ) or (int(network["link"][i]["s"]/10) == 8 and network["link"][i]["d"] == dev2 )):
                        LAT28 = network["link"][i]["PR"]
                        BW28 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 9 ) or (int(network["link"][i]["s"]/10) == 9 and network["link"][i]["d"] == dev2 )):
                        LAT29 = network["link"][i]["PR"]
                        BW29 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 10 ) or (int(network["link"][i]["s"]/10) == 10 and network["link"][i]["d"] == dev2 )):
                        LAT210 = network["link"][i]["PR"]
                        BW210 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev2 and int(network["link"][i]["d"]/10) == 11 ) or (int(network["link"][i]["s"]/10) == 11 and network["link"][i]["d"] == dev2 )):
                        LAT211 = network["link"][i]["PR"]
                        BW211 = network["link"][i]["BW"]

                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 0 ) or (int(network["link"][i]["s"]/10) == 0 and network["link"][i]["d"] == dev3 )):
                        LAT30 = network["link"][i]["PR"]
                        BW30 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 1 ) or (int(network["link"][i]["s"]/10) == 1 and network["link"][i]["d"] == dev3 )) :
                        LAT31 = network["link"][i]["PR"]
                        BW31 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 2 ) or (int(network["link"][i]["s"]/10) == 2 and network["link"][i]["d"] == dev3 )):
                        LAT32 = network["link"][i]["PR"]
                        BW32 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 3 ) or (int(network["link"][i]["s"]/10) == 3 and network["link"][i]["d"] == dev3 )):
                        LAT33 = network["link"][i]["PR"]
                        BW33 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 4 ) or (int(network["link"][i]["s"]/10) == 4 and network["link"][i]["d"] == dev3 )):
                        LAT34 = network["link"][i]["PR"]
                        BW34 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 5 ) or (int(network["link"][i]["s"]/10) == 5 and network["link"][i]["d"] == dev3 )):
                        LAT35 = network["link"][i]["PR"]
                        BW35 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 6 ) or (int(network["link"][i]["s"]/10) == 6 and network["link"][i]["d"] == dev3 )):
                        LAT36 = network["link"][i]["PR"]
                        BW36 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 7 ) or (int(network["link"][i]["s"]/10) == 7 and network["link"][i]["d"] == dev3 )):
                        LAT37 = network["link"][i]["PR"]
                        BW37 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 8 ) or (int(network["link"][i]["s"]/10) == 8 and network["link"][i]["d"] == dev3 )):
                        LAT38 = network["link"][i]["PR"]
                        BW38 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 9 ) or (int(network["link"][i]["s"]/10) == 9 and network["link"][i]["d"] == dev3 )):
                        LAT39 = network["link"][i]["PR"]
                        BW39 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 10 ) or (int(network["link"][i]["s"]/10) == 10 and network["link"][i]["d"] == dev3 )):
                        LAT310 = network["link"][i]["PR"]
                        BW310 = network["link"][i]["BW"]
                if ((network["link"][i]["s"] == dev3 and int(network["link"][i]["d"]/10) == 11 ) or (int(network["link"][i]["s"]/10) == 11 and network["link"][i]["d"] == dev3 )):
                        LAT311 = network["link"][i]["PR"]
                        BW311 = network["link"][i]["BW"]


    if (dev1 == 0 ):
                LAT0 = 0.5e-3
                BW0 = 13000
    if (dev1 == 1 ):
                LAT1 = 0.5e-3
                BW1 = 13000
    if (dev1 == 2 ):
                LAT2 = 0.5e-3
                BW2 = 13000
    if (dev1 == 3 ):
                LAT3 = 0.5e-3
                BW3 = 13000
    if (dev1 == 4 ):
                LAT4 = 0.5e-3
                BW4 = 13000
    if (dev1 == 5 ):
                LAT5 = 0.5e-3
                BW5 = 13000
    if (dev1 == 6 ):
                LAT6 = 0.5e-3
                BW6 = 13000
    if (dev1 == 7 ):
                LAT7 = 0.5e-3
                BW7 = 13000
    if (dev1 == 8 ):
                LAT8 = 0.5e-3
                BW8 = 13000
    if (dev1 == 9 ):
                LAT9 = 0.5e-3
                BW9 = 13000
    if (dev1 == 10 ):
                LAT10 = 0.5e-3
                BW10 = 13000
    if (dev1 == 11 ):
                LAT11 = 0.5e-3
                BW11 = 13000



    if (dev2 == 0 ):
                LAT20 = 0.5e-3
                BW20 = 13000
    if (dev2 == 1 ):
                LAT21 = 0.5e-3
                BW21 = 13000
    if (dev2 == 2 ):
                LAT22 = 0.5e-3
                BW22 = 13000
    if (dev2 == 3 ):
                LAT23 = 0.5e-3
                BW23 = 13000
    if (dev2 == 4 ):
                LAT24 = 0.5e-3
                BW24 = 13000
    if (dev2 == 5 ):
                LAT25 = 0.5e-3
                BW25 = 13000
    if (dev2 == 6 ):
                LAT26 = 0.5e-3
                BW26 = 13000
    if (dev2 == 7 ):
                LAT27 = 0.5e-3
                BW27 = 13000
    if (dev2 == 8 ):
                LAT28 = 0.5e-3
                BW28 = 13000
    if (dev2 == 9 ):
                LAT29 = 0.5e-3
                BW29 = 13000
    if (dev2 == 10 ):
                LAT210 = 0.5e-3
                BW210 = 13000
    if (dev2 == 11 ):
                LAT211 = 0.5e-3
                BW211 = 13000

    if (dev3 == 0 ):
                LAT30 = 0.5e-3
                BW30 = 13000
    if (dev3 == 1 ):
                LAT31 = 0.5e-3
                BW31 = 13000
    if (dev3 == 2 ):
                LAT32 = 0.5e-3
                BW32 = 13000
    if (dev3 == 3 ):
                LAT33 = 0.5e-3
                BW33 = 13000
    if (dev3 == 4 ):
                LAT34 = 0.5e-3
                BW34 = 13000
    if (dev3 == 5 ):
                LAT35 = 0.5e-3
                BW35 = 13000
    if (dev3 == 6 ):
                LAT36 = 0.5e-3
                BW36 = 13000
    if (dev3 == 7 ):
                LAT37 = 0.5e-3
                BW37 = 13000
    if (dev3 == 8 ):
                LAT38 = 0.5e-3
                BW38 = 13000
    if (dev3 == 9 ):
                LAT39 = 0.5e-3
                BW39 = 13000
    if (dev3 == 10 ):
                LAT310 = 0.5e-3
                BW310 = 13000
    if (dev3 == 11 ):
                LAT311 = 0.5e-3
                BW311 = 13000

    T = [0 for i in range(len(resources))]
    Tm = [0 for i in range(len(resources))]
    Tr = [0 for i in range(len(resources))]
    Tq = [0 for i in range(len(resources))] #for j in range(num_of_src)] # Queuing of Data cells.

    # print (type(Tm))
    # print (type(Tr))
    if (task == "encode_200"):
        ###print(encode_200[0]," ",type(rec))

 
        Tm[0] = encode_200[0]  # data size: 8sec video.
        Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0) 
        Tq[0] = num_of_src*Tr[0]
        T[0]  = numpy.round(numpy.round(Tm[0],4) + numpy.round(Tq[0],4) + numpy.round(Tr[0],4),4)
        #print (T[0])

        Tm[1] = encode_200[1]
        Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1)   
        Tq[1] = num_of_src*Tr[1]
        T[1] = numpy.round(numpy.round(Tm[1],4) + numpy.round(Tq[1],4) + numpy.round(Tr[1],4),4)
        #print (T[1])

        Tm[2] = encode_200[2]
        Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2)
        Tq[2] = num_of_src*Tr[2]
        T[2] = numpy.round(numpy.round(Tm[2],4) + numpy.round(Tq[2],4) + numpy.round(Tr[2],4),4)
        #print (T[2])

        Tm[3] = encode_200[3]
        Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)  
        Tq[3] = num_of_src*Tr[3]
        T[3] = numpy.round(numpy.round(Tm[3],4) + numpy.round(Tq[3],4) + numpy.round(Tr[3],4),4)
        #print (T[3])

        Tm[4] = encode_200[4]
        Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4) 
        Tq[4] = num_of_src*Tr[4]
        T[4] = numpy.round(numpy.round(Tm[4],4) + numpy.round(Tq[4],4) + numpy.round(Tr[4],4),4)
        #print (T[4])

        Tm[5] = encode_200[5]
        Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)  
        Tq[5] = num_of_src*Tr[5]
        T[5] = numpy.round(numpy.round(Tm[5],4) + numpy.round(Tq[5],4) + numpy.round(Tr[5],4),4)
        #print (T[5])

        Tm[6] = encode_200[6]
        Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6)  
        Tq[6] = num_of_src*Tr[6]
        T[6] = numpy.round(numpy.round(Tm[6],4) + numpy.round(Tq[6],4) + numpy.round(Tr[6],4),4)
        #print (T[6])

        Tm[7] = encode_200[7]
        Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7)
        Tq[7] = num_of_src*Tr[7]
        T[7] = numpy.round(numpy.round(Tm[7],4) + numpy.round(Tq[7],4) + numpy.round(Tr[7],4),4)

        Tm[8] = encode_200[8]
        Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8)  
        Tq[8] = num_of_src*Tr[8]
        T[8] = numpy.round(numpy.round(Tm[8],4) + numpy.round(Tq[8],4) + numpy.round(Tr[8],4),4)


        Tm[9] = encode_200[9]
        Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9) 
        Tq[9] = num_of_src*Tr[9]
        T[9] = numpy.round(numpy.round(Tm[9],4) + numpy.round(Tq[9],4) + numpy.round(Tr[9],4),4)


        Tm[10] = encode_200[10]
        Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)
        Tq[10] = num_of_src*Tr[10]
        T[10] = numpy.round(numpy.round(Tm[10],4) + numpy.round(Tq[10],4) + numpy.round(Tr[10],4),4)
        # print (T[10])

        Tm[11] = encode_200[11]
        Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11) 
        Tq[11] = num_of_src*Tr[11]
        T[11] = numpy.round(numpy.round(Tm[11],4) + numpy.round(Tq[11],4) + numpy.round(Tr[11],4),4)
        # print (T[11])

    elif (task == "frame_200"):
        ###print(frame_200[0]," ",type(rec))
        Tm[0] = frame_200[0]  # data size: 8sec video.
        Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0) 
        Tq[0] = num_of_src*Tr[0]
        T[0]  = numpy.round(numpy.round(Tm[0],4) + numpy.round(Tq[0],4) + numpy.round(Tr[0],4),4)
        # print (T[0][0])

        Tm[1] = frame_200[1]
        Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1)
        Tq[1] = num_of_src*Tr[1]
        T[1] = numpy.round(numpy.round(Tm[1],4) + numpy.round(Tq[1],4) + numpy.round(Tr[1],4),4)
        # print (T[1])

        Tm[2] = frame_200[2]
        Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2) 
        Tq[2] = num_of_src*Tr[2]
        T[2] = numpy.round(numpy.round(Tm[2],4) + numpy.round(Tq[2],4) + numpy.round(Tr[2],4),4)
        # print (T[2])

        Tm[3] = frame_200[3]
        Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)
        Tq[3] = num_of_src*Tr[3]
        T[3] = numpy.round(numpy.round(Tm[3],4) + numpy.round(Tq[3],4) + numpy.round(Tr[3],4),4)
        # print (T[3])

        Tm[4] = frame_200[4]
        Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4)
        Tq[4] = num_of_src*Tr[4]
        T[4] = numpy.round(numpy.round(Tm[4],4) + numpy.round(Tq[4],4) + numpy.round(Tr[4],4),4)
        # print (T[4])

        Tm[5] = frame_200[5]
        Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)
        Tq[5] = num_of_src*Tr[5]
        T[5] = numpy.round(numpy.round(Tm[5],4) + numpy.round(Tq[5],4) + numpy.round(Tr[5],4),4)
        # print (T[5])

        Tm[6] = frame_200[6]
        Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6) 
        Tq[6] = num_of_src*Tr[6]
        T[6] = numpy.round(numpy.round(Tm[6],4) + numpy.round(Tq[6],4) + numpy.round(Tr[6],4),4)
        # print (T[6])

        Tm[7] = frame_200[7]
        Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7) 
        Tq[7] = num_of_src*Tr[7]
        T[7] = numpy.round(numpy.round(Tm[7],4) + numpy.round(Tq[7],4) + numpy.round(Tr[7],4),4)

        Tm[8] = frame_200[8]
        Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8) 
        Tq[8] = num_of_src*Tr[8]
        T[8] = numpy.round(numpy.round(Tm[8],4) + numpy.round(Tq[8],4) + numpy.round(Tr[8],4),4)

        Tm[9] = frame_200[9]
        Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9) 
        Tq[9] = num_of_src*Tr[9]
        T[9] = numpy.round(numpy.round(Tm[9],4) + numpy.round(Tq[9],4) + numpy.round(Tr[9],4),4)

        Tm[10] = frame_200[10]
        Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10) 
        Tq[10] = num_of_src*Tr[10]
        T[10] = numpy.round(numpy.round(Tm[10],4) + numpy.round(Tq[10],4) + numpy.round(Tr[10],4),4)
        # print (T[10])
                
        Tm[11] = frame_200[11]
        Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11) 
        Tq[11] = num_of_src*Tr[11]
        T[11] = numpy.round(numpy.round(Tm[11],4) + numpy.round(Tq[11],4) + numpy.round(Tr[11],4),4)
        # print (T[11])

    elif (task == "hightrain"):
        # print(hightrain[0]," ",type(rec))
        if (num_of_src == 0):
            Tm[0] = hightrain[0] # data size: 8sec video.
            Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0)        
            Tq[0] = num_of_src*Tr[0]
        else:
            Tm[0] = 0.1
            Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0)        
            Tq[0] = num_of_src*Tr[0] 
        
        T[0]  = numpy.round(numpy.round(Tm[0],4) + numpy.round(Tq[0],4) + numpy.round(Tr[0],4),4)
        # print (T[0][0])

        if (num_of_src == 0):
            Tm[1] = hightrain[1] 
            Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1)        
            Tq[1] = num_of_src*Tr[1]
        else:
            Tm[1] = 0.1
            Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1)        
            Tq[1] = num_of_src*Tr[1] 
        
        T[1] = numpy.round(numpy.round(Tm[1],4) + numpy.round(Tq[1],4) + numpy.round(Tr[1],4),4)
        # print (T[1])

        if (num_of_src == 0):
            Tm[2] = hightrain[2]
            Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2)        
            Tq[2] = num_of_src*Tr[2]
        else:
            Tm[2] = 0.1
            Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2)        
            Tq[2] = num_of_src*Tr[2] 
        
        T[2] = numpy.round(numpy.round(Tm[2],4) + numpy.round(Tq[2],4) + numpy.round(Tr[2],4),4)
        # print (T[2])

        if (num_of_src == 0):
            Tm[3] = hightrain[3]
            Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)        
            Tq[3] = num_of_src*Tr[3]
        else:
            Tm[3] = 0.1
            Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)        
            Tq[3] = num_of_src*Tr[3] 
        
        T[3] = numpy.round(numpy.round(Tm[3],4) + numpy.round(Tq[3],4) + numpy.round(Tr[3],4),4)
        # print (T[3])

        if (num_of_src == 0):
            Tm[4] = hightrain[4]
            Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4)        
            Tq[4] = num_of_src*Tr[4] 
        else:
            Tm[4] = 0.1
            Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4)        
            Tq[4] = num_of_src*Tr[4] 
        
        T[4] = numpy.round(numpy.round(Tm[4],4) + numpy.round(Tq[4],4) + numpy.round(Tr[4],4),4)
        # print (T[4])

        if (num_of_src == 0):
            Tm[5] = hightrain[5]
            Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)        
            Tq[5] = num_of_src*Tr[5]
        else:
            Tm[5] = 0.1
            Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)        
            Tq[5] = num_of_src*Tr[5] 
        
        T[5] = numpy.round(numpy.round(Tm[5],4) + numpy.round(Tq[5],4) + numpy.round(Tr[5],4),4)
        # print (T[5])

        if (num_of_src == 0):
            Tm[6] = hightrain[6] 
            Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6)        
            Tq[6] = num_of_src*Tr[6]
        else:
            Tm[6] = 0.1
            Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6)        
            Tq[6] = num_of_src*Tr[6] 
        T[6] = numpy.round(numpy.round(Tm[6],4) + numpy.round(Tq[6],4) + numpy.round(Tr[6],4),4)
        # print (T[6])


        if (num_of_src == 0):
            Tm[7] = hightrain[7]
            Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7)        
            Tq[7] = num_of_src*Tr[7]
        else:
            Tm[7] = 0.1
            Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7)        
            Tq[7] = num_of_src*Tr[7]  
        
        T[7] = numpy.round(numpy.round(Tm[7],4) + numpy.round(Tq[7],4) + numpy.round(Tr[7],4),4)

        if (num_of_src == 0):
            Tm[8] = hightrain[8]
            Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8)        
            Tq[8] = num_of_src*Tr[8]
        else:
            Tm[8] = 0.1
            Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8)        
            Tq[8] = num_of_src*Tr[8]
        T[8] = numpy.round(numpy.round(Tm[8], 4)  + numpy.round(Tq[8],4) +  numpy.round(Tr[8], 4), 4)

        if (num_of_src == 0):
            Tm[9] = hightrain[9]
            Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9)        
            Tq[9] = num_of_src*Tr[9]
        else:
            Tm[9] = 0.1
            Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9)        
            Tq[9] = num_of_src*Tr[9]
        T[9] = numpy.round(numpy.round(Tm[9], 4)  + numpy.round(Tq[9],4)  + numpy.round(Tr[9], 4), 4)

        if (num_of_src == 0):
            Tm[10] = hightrain[10]
            Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)        
            Tq[10] = num_of_src*Tr[10]
        else:
            Tm[10] = 0.1
            Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)        
            Tq[10] = num_of_src*Tr[10] 
        T[10] = numpy.round(numpy.round(Tm[10], 4)  + numpy.round(Tq[10],4) +  numpy.round(Tr[10], 4), 4)
        # print (T[10])


        if (num_of_src == 0):
            Tm[11] = hightrain[11]
            Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11)        
            Tq[11] = num_of_src*Tr[11]
        else:
            Tm[11] = 0.1
            Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11)        
            Tq[11] = num_of_src*Tr[11] 
        T[11] = numpy.round(numpy.round(Tm[11], 4)  + numpy.round(Tq[11],4) +  numpy.round(Tr[11], 4), 4)
        # print (T[11])

    elif (task == "lowtrain"):
        # print(lowtrain[0]," ",type(rec))
        if (num_of_src == 0):
            Tm[0] = lowtrain[0] # data size: 8sec video.
            Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0)        
            Tq[0] = num_of_src*Tr[0]
        else:
            Tm[0] = 0.1
            Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0)        
            Tq[0] = num_of_src*Tr[0]  
        T[0] = numpy.round(numpy.round(Tm[0], 4) + numpy.round(Tq[0],4) +  numpy.round(Tr[0], 4), 4)
        # print (T[0][0])

        if (num_of_src == 0):
            Tm[1] = lowtrain[1] 
            Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1)        
            Tq[1] = num_of_src*Tr[1]
        else:
            Tm[1] = 0.1
            Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1)        
            Tq[1] = num_of_src*Tr[1]  
        T[1] = numpy.round(numpy.round(Tm[1], 4) + numpy.round(Tq[1],4) +  numpy.round(Tr[1], 4), 4)
        # print (T[1])

        if (num_of_src == 0):
            Tm[2] = lowtrain[2]
            Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2) 
            Tq[2] = num_of_src*Tr[2]
        else:
            Tm[2] = 0.1
            Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2) 
            Tq[2] = num_of_src*Tr[2]         
        T[2] = numpy.round(numpy.round(Tm[2], 4) + numpy.round(Tq[2],4) +  numpy.round(Tr[2], 4), 4)
        # print (T[2])


        if (num_of_src == 0):
            Tm[3] = lowtrain[3]
            Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)
            Tq[3] = num_of_src*Tr[3]
        else:
            Tm[3] = 0.1
            Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)        
            Tq[3] = num_of_src*Tr[3]  
        T[3] = numpy.round(numpy.round(Tm[3], 4) + numpy.round(Tq[3],4) +  numpy.round(Tr[3], 4), 4)
        # print (T[3])

        if (num_of_src == 0):
            Tm[4] = lowtrain[4] 
            Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4)
            Tq[4] = num_of_src*Tr[4]
        else:
            Tm[4] = 0.1
            Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4)
            Tq[4] = num_of_src*Tr[4]
        T[4] = numpy.round(numpy.round(Tm[4], 4) + numpy.round(Tq[4],4) +  numpy.round(Tr[4], 4), 4)
        # print (T[4])

        if (num_of_src == 0):
            Tm[5] = lowtrain[5]
            Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)
            Tq[5] = num_of_src*Tr[5]
        else:
            Tm[5] = 0.1
            Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)
            Tq[5] = num_of_src*Tr[5]
        T[5] = numpy.round(numpy.round(Tm[5], 4) + numpy.round(Tq[5],4) + numpy.round(Tr[5], 4), 4)
        # print (T[5])

        if (num_of_src == 0):
            Tm[6] = lowtrain[6]
            Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6)    
            Tq[6] = num_of_src*Tr[6]
        else:
            Tm[6] = 0.1
            Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6)    
            Tq[6] = num_of_src*Tr[6]
        T[6] = numpy.round(numpy.round(Tm[6], 4) + numpy.round(Tq[6],4) + numpy.round(Tr[6], 4), 4)
        # print (T[6])


        if (num_of_src == 0):
            Tm[7] = lowtrain[7]
            Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7)        
            Tq[7] = num_of_src*Tr[7]
        else:
            Tm[7] = 0.1
            Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7)        
            Tq[7] = num_of_src*Tr[7]  
        T[7] = numpy.round(numpy.round(Tm[7], 4) + numpy.round(Tq[7],4) + numpy.round(Tr[7], 4), 4)


        if (num_of_src == 0):
            Tm[8] = lowtrain[8]
            Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8)        
            Tq[8] = num_of_src*Tr[8]
        else:
            Tm[8] = 0.1
            Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8)        
            Tq[8] = num_of_src*Tr[8]  
        T[8] = numpy.round(numpy.round(Tm[8], 4) + numpy.round(Tq[8],4)  +  numpy.round(Tr[8], 4), 4)

        if (num_of_src == 0):
            Tm[9] = lowtrain[9]
            Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9) 
            Tq[9] = num_of_src*Tr[9]
        else:
            Tm[9] = 0.1
            Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9) 
            Tq[9] = num_of_src*Tr[9]         
        T[9] = numpy.round(numpy.round(Tm[9], 4)  + numpy.round(Tq[9],4) + numpy.round(Tr[9], 4), 4)

        if (num_of_src == 0):
            Tm[10] = lowtrain[10] 
            Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)        
            Tq[10] = num_of_src*Tr[10]
        else:
            Tm[10] = 0.1
            Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)        
            Tq[10] = num_of_src*Tr[10]  
        
        T[10] = numpy.round(numpy.round(Tm[10], 4)  + numpy.round(Tq[10],4) +  numpy.round(Tr[10], 4), 4)
        # print (T[10])


        if (num_of_src == 0):
            Tm[11] = lowtrain[11] 
            Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11)        
            Tq[11] = num_of_src*Tr[11]
        else:
            Tm[11] = 0.1
            Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11)        
            Tq[11] = num_of_src*Tr[11]  
        
        T[11] = numpy.round(numpy.round(Tm[11], 4) + numpy.round(Tq[11],4)  +  numpy.round(Tr[11], 4), 4)
        # print (T[11])

    elif (task == "inference"):
        # print(inference[0]," ",type(rec))
        Tm[0] = inference[0]  # data size: 8sec video.
        Tr[0] = max(((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0),
                ((0.000001) * (seg_size[index_of_segment]) / BW20) + ((0.000001) *LAT20))  
        Tq[0] = num_of_src*Tr[0]
        T[0] = numpy.round(numpy.round(Tm[0], 4)  + numpy.round(Tq[0],4) +  numpy.round(Tr[0], 4), 4)
        # print (T[0][0])

        Tm[1] = inference[1]
        Tr[1] = max(((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1),
                ((0.000001) * (seg_size[index_of_segment]) / BW21) + ((0.000001) *LAT21))         
        Tq[1] = num_of_src*Tr[1]        
        T[1] = numpy.round(numpy.round(Tm[1], 4)  + numpy.round(Tq[1],4) +  numpy.round(Tr[1], 4), 4)
        # print (T[1])

        Tm[2] = inference[2]
        Tr[2] = max(((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2),
                ((0.000001) * (seg_size[index_of_segment]) / BW22) + ((0.000001) *LAT22))         
        Tq[2] = num_of_src*Tr[2]        
        T[2] = numpy.round(numpy.round(Tm[2], 4)  + numpy.round(Tq[2],4) +  numpy.round(Tr[2], 4), 4)
        # print (T[2])

        Tm[3] = inference[3]
        Tr[3] = max(((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3),
                ((0.000001) * (seg_size[index_of_segment]) / BW23) + ((0.000001) *LAT23))  
        Tq[3] = num_of_src*Tr[3]       
        T[3] = numpy.round(numpy.round(Tm[3], 4)  + numpy.round(Tq[3],4) +  numpy.round(Tr[3], 4), 4)
        # print (T[3])

        Tm[4] = inference[4]
        Tr[4] = max(((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4),
                ((0.000001) * (seg_size[index_of_segment]) / BW24) + ((0.000001) *LAT24))
        Tq[4] = num_of_src*Tr[4]        
        T[4] = numpy.round(numpy.round(Tm[4], 4)  + numpy.round(Tq[4],4) +  numpy.round(Tr[4], 4), 4)
        # print (T[4])

        Tm[5] = inference[5]
        Tr[5] = max(((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5),
                ((0.000001) * (seg_size[index_of_segment]) / BW25) + ((0.000001) *LAT25))
        Tq[5] = num_of_src*Tr[5]
        T[5] = numpy.round(numpy.round(Tm[5], 4)  + numpy.round(Tq[5],4) +  numpy.round(Tr[5], 4), 4)
        # print (T[5])

        Tm[6] = inference[6]
        Tr[6] = max(((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6),
                ((0.000001) * (seg_size[index_of_segment]) / BW26) + ((0.000001) *LAT26)) 
        Tq[6] = num_of_src*Tr[6]
        T[6] = numpy.round(numpy.round(Tm[6], 4)  + numpy.round(Tq[6],4) +  numpy.round(Tr[6], 4), 4)
        # print (T[6])

        Tm[7] = inference[7]
        Tr[7] = max(((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7),
                ((0.000001) * (seg_size[index_of_segment]) / BW27) + ((0.000001) *LAT27))
        Tq[7] = num_of_src*Tr[7] 
        T[7] = numpy.round(numpy.round(Tm[7], 4)  + numpy.round(Tq[7],4) +  numpy.round(Tr[7], 4), 4)
        # print (T[7])


        Tm[8] = inference[8]
        Tr[8] = max(((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8),
                ((0.000001) * (seg_size[index_of_segment]) / BW28) + ((0.000001) *LAT28))
        Tq[8] = num_of_src*Tr[8]
        T[8] = numpy.round(numpy.round(Tm[8], 4)  + numpy.round(Tq[8],4) +  numpy.round(Tr[8], 4), 4)
        # print (T[8])

        Tm[9] = inference[9]
        Tr[9] = max(((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9),
                ((0.000001) * (seg_size[index_of_segment]) / BW29) + ((0.000001) *LAT29))
        Tq[9] = num_of_src*Tr[9]
        T[9] = numpy.round(numpy.round(Tm[9], 4)  + numpy.round(Tq[9],4) + numpy.round(Tr[9], 4), 4)
        # print (T[9])

        Tm[10] = inference[10]
        Tr[10] = max(((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10),
                ((0.000001) * (seg_size[index_of_segment]) / BW210) + ((0.000001) *LAT210))  
        Tq[10] = num_of_src*Tr[10]      
        T[10] = numpy.round(numpy.round(Tm[10], 4)  + numpy.round(Tq[10],4) +  numpy.round(Tr[10], 4), 4)
        # print (T[10])

        
        Tm[11] = inference[11]
        Tr[11] = max(((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11),
                ((0.000001) * (seg_size[index_of_segment]) / BW211) + ((0.000001) *LAT211))  
        Tq[11] = num_of_src*Tr[11]      
        T[11] = numpy.round(numpy.round(Tm[11], 4)  + numpy.round(Tq[11],4) +  numpy.round(Tr[11], 4), 4)
        # print (T[11])

    elif (task == "transcode"):
        ###print(encode_200[0]," ",type(rec))
        Tm[0] = encode_200[0]  # data size: 8sec video.
        Tr[0] = max(((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0),
                ((0.000001) * (seg_size[index_of_segment]) / BW20) + ((0.000001) *LAT20),
                ((0.000001) * (seg_size[index_of_segment]) / BW30) + ((0.000001) *LAT30))
        Tq[0] = num_of_src*Tr[0]
        T[0] = numpy.round(numpy.round(Tm[0], 4)  + numpy.round(Tq[0],4) +  numpy.round(Tr[0], 4), 4)
        #print (Tr[0])

        Tm[1] = encode_200[1]
        Tr[1] = max(((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1),
                ((0.000001) * (seg_size[index_of_segment]) / BW21) + ((0.000001) *LAT21),
                ((0.000001) * (seg_size[index_of_segment]) / BW31) + ((0.000001) *LAT31))
        Tq[1] = num_of_src*Tr[1]
        T[1] = numpy.round(numpy.round(Tm[1], 4)  + numpy.round(Tq[1],4) +  numpy.round(Tr[1], 4), 4)
        #print (Tr[1])

        Tm[2] = encode_200[2]
        Tr[2] = max(((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2),
                ((0.000001) * (seg_size[index_of_segment]) / BW22) + ((0.000001) *LAT22),
                ((0.000001) * (seg_size[index_of_segment]) / BW32) + ((0.000001) *LAT32))
        Tq[2] = num_of_src*Tr[2]
        T[2] = numpy.round(numpy.round(Tm[2], 4)  + numpy.round(Tq[2],4) +  numpy.round(Tr[2], 4), 4)
        #print(seg_size[index_of_segment]," ",BW32," ",(0.000001) * (seg_size[index_of_segment]) / BW32 )
        #print((0.000001) *(seg_size[index_of_segment]) / BW32)
        #print(LAT32)
        #print() 
        #print()

        Tm[3] = encode_200[3]
        Tr[3] = max(((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3),
                ((0.000001) * (seg_size[index_of_segment]) / BW23) + ((0.000001) *LAT23),
                ((0.000001) * (seg_size[index_of_segment]) / BW33) + ((0.000001) *LAT33))
        Tq[3] = num_of_src*Tr[3]
        T[3] = numpy.round(numpy.round(Tm[3], 4)  + numpy.round(Tq[3],4) +  numpy.round(Tr[3], 4), 4)
        #print (T[3])

        Tm[4] = encode_200[4]
        Tr[4] = max(((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4),
                ((0.000001) * (seg_size[index_of_segment]) / BW24) + ((0.000001) *LAT24),
                ((0.000001) * (seg_size[index_of_segment]) / BW34) + ((0.000001) *LAT34))
        Tq[4] = num_of_src*Tr[4]
        T[4] = numpy.round(numpy.round(Tm[4], 4)  + numpy.round(Tq[4],4) +  numpy.round(Tr[4], 4), 4)
        #print (Tr[4])

        Tm[5] = encode_200[5]
        Tr[5] = max(((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5),
                ((0.000001) * (seg_size[index_of_segment]) / BW25) + ((0.000001) *LAT25),
                ((0.000001) * (seg_size[index_of_segment]) / BW35) + ((0.000001) *LAT35))
        Tq[5] = num_of_src*Tr[5]
        T[5] = numpy.round(numpy.round(Tm[5], 4)  + numpy.round(Tq[5],4) +  numpy.round(Tr[5], 4), 4)
        #print (Tr[5])

        Tm[6] = encode_200[6]
        Tr[6] = max(((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6),
                ((0.000001) * (seg_size[index_of_segment]) / BW26) + ((0.000001) *LAT26),
                ((0.000001) * (seg_size[index_of_segment]) / BW36) + ((0.000001) *LAT36))
        Tq[6] = num_of_src*Tr[6]
        T[6] = numpy.round(numpy.round(Tm[6], 4)  + numpy.round(Tq[6],4) +  numpy.round(Tr[6], 4), 4)
        #print (Tr[6])

        Tm[7] = encode_200[7]
        Tr[7] = max(((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7),
                ((0.000001) * (seg_size[index_of_segment]) / BW27) + ((0.000001) *LAT27),
                ((0.000001) * (seg_size[index_of_segment]) / BW37) + ((0.000001) *LAT37))
        Tq[7] = num_of_src*Tr[7]
        T[7] = numpy.round(numpy.round(Tm[7], 4)  + numpy.round(Tq[7],4) +  numpy.round(Tr[7], 4), 4)
        #print (Tr[8])

        Tm[8] = encode_200[8]
        Tr[8] = max(((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8),
                ((0.000001) * (seg_size[index_of_segment]) / BW28) + ((0.000001) *LAT28),
                ((0.000001) * (seg_size[index_of_segment]) / BW38) + ((0.000001) *LAT38))
        Tq[8] = num_of_src*Tr[8]
        T[8] = numpy.round(numpy.round(Tm[8], 4)  + numpy.round(Tq[8],4) +  numpy.round(Tr[8], 4), 4)
        #print (Tr[8])

        Tm[9] = encode_200[9]
        Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9)
        Tq[9] = num_of_src*Tr[9]
        T[9] = numpy.round(numpy.round(Tm[9], 4)  + numpy.round(Tq[9],4) + numpy.round(Tr[9], 4), 4)
        #print (Tr[9])

        Tm[10] = encode_200[10]
        Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)
        Tq[10] = num_of_src*Tr[10]
        T[10] = numpy.round(numpy.round(Tm[10], 4)  + numpy.round(Tq[10],4) + numpy.round(Tr[10], 4), 4)
        #print (Tr[10])

        Tm[11] = encode_200[11]
        Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11)
        Tq[11] = num_of_src*Tr[11]
        T[11] = numpy.round(numpy.round(Tm[11], 4)  + numpy.round(Tq[11],4) + numpy.round(Tr[11], 4), 4)
        #print (Tr[11])

    elif (task == "package"):
        ###print(encode_200[0]," ",type(rec))
        Tm[0] = encode_200[0]  # data size: 8sec video.
        Tr[0] = ((0.000001) * (seg_size[index_of_segment]) / BW0) + ((0.000001) *LAT0)
        Tq[0] = num_of_src*Tr[0]
        T[0] = numpy.round(numpy.round(Tm[0], 4)  + numpy.round(Tq[0],4)  +  numpy.round(Tr[0], 4), 4)
        #print (T[0])

        Tm[1] = encode_200[1]
        Tr[1] = ((0.000001) * (seg_size[index_of_segment]) / BW1) + ((0.000001) *LAT1) 
        Tq[1] = num_of_src*Tr[1]       
        T[1] = numpy.round(numpy.round(Tm[1], 4)  + numpy.round(Tq[1],4)  +  numpy.round(Tr[1], 4), 4)
        #print (T[1])

        Tm[2] = encode_200[2]
        Tr[2] = ((0.000001) * (seg_size[index_of_segment]) / BW2) + ((0.000001) *LAT2)        
        Tq[2] = num_of_src*Tr[2]
        T[2] = numpy.round(numpy.round(Tm[2], 4)  + numpy.round(Tq[2],4)  +  numpy.round(Tr[2], 4), 4)
        #print (T[2])

        Tm[3] = encode_200[3]
        Tr[3] = ((0.000001) * (seg_size[index_of_segment]) / BW3) + ((0.000001) *LAT3)        
        Tq[3] = num_of_src*Tr[3]
        T[3] = numpy.round(numpy.round(Tm[3], 4)  + numpy.round(Tq[3],4)  +  numpy.round(Tr[3], 4), 4)
        #print (T[3])

        Tm[4] = encode_200[4]
        Tr[4] = ((0.000001) * (seg_size[index_of_segment]) / BW4) + ((0.000001) *LAT4)        
        Tq[4] = num_of_src*Tr[4]
        T[4] = numpy.round(numpy.round(Tm[4], 4)  + numpy.round(Tq[4],4)  +  numpy.round(Tr[4], 4), 4)
        #print (T[4])

        Tm[5] = encode_200[5]
        Tr[5] = ((0.000001) * (seg_size[index_of_segment]) / BW5) + ((0.000001) *LAT5)        
        Tq[5] = num_of_src*Tr[5]
        T[5] = numpy.round(numpy.round(Tm[5], 4)  + numpy.round(Tq[5],4)  +  numpy.round(Tr[5], 4), 4)
        #print (T[5])

        Tm[6] = encode_200[6]
        Tr[6] = ((0.000001) * (seg_size[index_of_segment]) / BW6) + ((0.000001) *LAT6)        
        Tq[6] = num_of_src*Tr[6]
        T[6] = numpy.round(numpy.round(Tm[6], 4)  + numpy.round(Tq[6],4)  +  numpy.round(Tr[6], 4), 4)
        #print (T[6])

        Tm[7] = encode_200[7]
        Tr[7] = ((0.000001) * (seg_size[index_of_segment]) / BW7) + ((0.000001) *LAT7)        
        Tq[7] = num_of_src*Tr[7]
        T[7] = numpy.round(numpy.round(Tm[7], 4)  + numpy.round(Tq[7],4)  +  numpy.round(Tr[7], 4), 4)

        Tm[8] = encode_200[8]
        Tr[8] = ((0.000001) * (seg_size[index_of_segment]) / BW8) + ((0.000001) *LAT8)        
        Tq[8] = num_of_src*Tr[8]
        T[8] = numpy.round(numpy.round(Tm[8], 4)  + numpy.round(Tq[8],4)  +  numpy.round(Tr[8], 4), 4)


        Tm[9] = encode_200[9]
        Tr[9] = ((0.000001) * (seg_size[index_of_segment]) / BW9) + ((0.000001) *LAT9)        
        Tq[9] = num_of_src*Tr[9]
        T[9] = numpy.round(numpy.round(Tm[9], 4)  + numpy.round(Tq[9],4)  + numpy.round(Tr[9], 4), 4)


        Tm[10] = encode_200[10]
        Tr[10] = ((0.000001) * (seg_size[index_of_segment]) / BW10) + ((0.000001) *LAT10)
        Tq[10] = num_of_src*Tr[10]
        T[10] = numpy.round(numpy.round(Tm[10], 4)  + numpy.round(Tq[10],4)  +  numpy.round(Tr[10], 4), 4)
        # print (T[10])


        Tm[11] = encode_200[11]
        Tr[11] = ((0.000001) * (seg_size[index_of_segment]) / BW11) + ((0.000001) *LAT11)
        Tq[11] = num_of_src*Tr[11]
        T[11] = numpy.round(numpy.round(Tm[11], 4)  + numpy.round(Tq[11],4)  +  numpy.round(Tr[11], 4), 4)
        # print (T[11])


    return (Tm, Tr, Tq, T)