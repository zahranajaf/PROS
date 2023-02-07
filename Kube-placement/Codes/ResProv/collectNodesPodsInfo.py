import numpy
from operator import itemgetter, attrgetter
import networkx as nx
import yaml
import subprocess as commands
import json
import sys
import time
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect()

#tup = commands.getstatusoutput("docker run sina88/ubuntu-encoding:amd64")
#splittt = str(tup[1]).splitlines()
###print(commands.getstatusoutput("kubectl describe pod termination-demo"))

#cpu_util = {'gateway': 0.66, 'node1': 0.66, 'node2': 0.66,  'node3': 0.66, 'node4': 0.66,
#          'node5': 0.66, 'node6': 0.66, 'node7': 0.66,  'node8': 0.66, 'node9': 0.66, 'node10': 0.66}

rank = {'gateway':[0,0,0,0,0,0],  'node1': [0,0,0,0,0,0],   'node1': [0,0,0,0,0,0],   'node2': [0,0,0,0,0,0],   'node3': [0,0,0,0,0,0],  'node4': [0,0,0,0,0,0],
        'node5': [0,0,0,0,0,0],   'node6': [0,0,0,0,0,0],   'node7': [0,0,0,0,0,0],   'node8': [0,0,0,0,0,0],   'node9': [0,0,0,0,0,0],  'node10':[0,0,0,0,0,0]}

print("Nodes status")
#kube_nodes = 'Nodes status   NAME      STATUS                        ROLES                  AGE    VERSION\ngateway   Ready                         control-plane,master   561d   v1.20.4\nnode1     Ready                         worker                 512d   v1.21.0\nnode10    NotReady                      <none>                 497d   v1.21.0\nnode2     Ready                         worker                 511d   v1.21.0\nnode22    NotReady,SchedulingDisabled   <none>                 497d   v1.21.0\nnode23    NotReady,SchedulingDisabled   <none>                 497d   v1.21.0\nnode24    NotReady,SchedulingDisabled   <none>                 497d   v1.21.0\nnode4     Ready                         worker                 511d   v1.21.0\nnode5     NotReady                      worker                 511d   v1.21.0\nnode6     Ready                         worker                 512d   v1.21.0\nnode7     Ready                         <none>                 497d   v1.21.0\nnode8     Ready                         <none>                 497d   v1.21.0\nnode9     Ready                         <none>                 497d   v1.21.0'#
cpu_util = prom.custom_query(query="sort_desc((instance:node_cpu_utilisation:rate1m))")
avg_cpu = 0
for i in range(len(cpu_util)):
        avg_cpu = (avg_cpu + (numpy.round(float(cpu_util[i]['value'][1]),5))) / (i + 1)
#print(cpu_util[0]['metric']['node']," ",cpu_util[0]['metric']['pod']," ",(avg_cpu))

kube_nodes = commands.getstatusoutput(".\kubectl.exe --kubeconfig .\.kube\config get nodes")
split_nodes = str(kube_nodes).split('\n')
#print(split_nodes)
for i in range(len(split_nodes)):
        list0  = split_nodes[i].split('\t')
        node = str(list0[0]).split(' ')
        for j in range (len(node)):
                if (node[j] == "Ready"):
                        print (node[0])
                        if(cpu_util[0]['metric']['node'] <= 0.66):
                                rank[node[0]][0] = rank[node[0]][0] + 1
                                print("Pods status")
                                #kube_pods ='NAME                                    READY   STATUS             RESTARTS   AGE\n0encoding-64c55778f9-8rhhp              0/1     ImagePullBackOff   0          4d7h\n1framing-77655d8d4b-c4j4l               0/1     Terminating        0          4d7h\n1framing-77655d8d4b-k5qj6               0/1     Terminating        0          4d7h\n2inferencehigh-568d84d96-v42tf          0/1     CrashLoopBackOff   1187       4d7h\n3traininghigh-7f5dc9c874-q4gwv          0/1     ImagePullBackOff   1          4d9h\nflask-k8s-deployment-7bd77c5f85-xsfw5   1/1     Running            0          13d\ngrafana-6488594599-lgffw                1/1     Running            0          8d\npingtest-64f9cb6b84-4fcng               1/1     Terminating        1          496d\npingtest-64f9cb6b84-bd9fv               1/1     Running            0          8d\npingtest-64f9cb6b84-dzt7n               1/1     Running            9          496d\npingtest-64f9cb6b84-g758m               1/1     Running            0          8d\npingtest-64f9cb6b84-m452w               1/1     Running            0          8d\npingtest-64f9cb6b84-tb7ms               1/1     Running            4          357d\ntest-kl-kube-latency-2s4ht              1/1     Running            9295       442d\ntest-kl-kube-latency-7m885              0/1     CrashLoopBackOff   9065       496d\ntest-kl-kube-latency-9vnmz              1/1     Running            15         496d\ntest-kl-kube-latency-9xlnm              1/1     Running            14         446d\ntest-kl-kube-latency-b6j6s              1/1     Running            5648       496d\ntest-kl-kube-latency-bf5qq              1/1     Running            294        498d\ntest-kl-kube-latency-csvd7              1/1     Running            10         496d\ntest-kl-kube-latency-dztsc              0/1     CrashLoopBackOff   15688      496d\ntest-kl-kube-latency-gq6j2              1/1     Running            12         496d\ntest-kl-kube-latency-kd9lf              1/1     Running            0          496d\ntest-kl-kube-latency-t98gd              1/1     Running            1537       498d\ntest-kl-kube-latency-wwk72              0/1     Error              14         498d'
                                kube_pods = commands.getstatusoutput(".\kubectl.exe --kubeconfig .\.kube\config get pods")
                                split_pods = str(kube_pods).split('\n')
                                for i in range(len(split_pods)):
                                        list0  = split_pods[i].split('\t')
                                        pod = str(list0[0]).split(' ')
                                        #print((pod))
                                        for j in range (len(pod)):
                                                if (pod[j] == "Running" or pod[j] == "Completed" or pod[j] == "ErrImagePull" or  pod[j] == "CrashLoopBackOff" or pod[j] == "Terminating"):
                                                        print (pod[0], " ", pod[j], " ", pod[15])
                                                        #rank[pod[0]][1] = rank[pod[0]][1] + 1


#print(rank)