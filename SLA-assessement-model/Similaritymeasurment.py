from math import*
import networkx as nx
import numpy as np

def Eulidean_distance(x,y):
    dist= sqrt(sum(pow(a-b,2) for a,b in zip(x,y)))
    #print(dist)
    return dist
def Euclidean_similarity(x,y):
    dist= Eulidean_distance(x,y)
    sim = 1/(1+dist)
    return sim

def SLA_Sim_graph(SLAvalue):
    sim = np.zeros((len(SLAvalue), len(SLAvalue)))
    for i in range(len(SLAvalue)):
        for j in range(len(SLAvalue)):
          if(i != j):
            s= Euclidean_similarity([SLAvalue[i]],[SLAvalue[j]])

            if (s > 0.8):
                sim[i, j] = s
            else:
                sim[i, j] = 0.0
    #print("This is similarity matrix based on the SLA value: ", sim)
    nodes=[]
    G = nx.Graph()
    for i in range(len(sim)):
        nodes.append(i)

    G.add_nodes_from(nodes)
    for i in range(len(sim)):
        for j in range(len(sim)):
            if sim[i][j] > 0.0:
                G.add_edge(i, j)
    for e in G.edges:
        G[e[0]][e[1]]['weight'] = sim[e[0]][e[1]]
        #print("The weight from node  ", e[0], " to ", e[1], G[e[0]][e[1]]['weight'])
    return G

def layer_creation(layer_name, devices):

  network_size = (len(devices))
  print(network_size)
  sim = np.zeros((network_size,network_size))

  for i in range(network_size):
     for j in range(network_size):

          if(i != j):
            if(layer_name == 'cpu'):
                k=0
                sim_value= Euclidean_similarity([devices[i]['cpu']['core_num'],devices[i]['cpu']['cache'],devices[i]['cpu']['speed']], [devices[j]['cpu']['core_num'],devices[j]['cpu']['cache'],devices[j]['cpu']['speed']])
                if (sim_value >= 0.5):
                    sim[i, j] = sim_value
                else:
                    sim[i, j] = 0.0
            elif(layer_name == 'network'):
                k = 0
                sim_value = Euclidean_similarity([devices[i]['network']['up_Bw'], devices[i]['network']['down_Bw']]\
                                                 , [devices[j]['network']['up_Bw'], devices[j]['network']['down_Bw']])
                if(sim_value>= 0.5):
                    sim[i, j] = sim_value
                else:
                    sim[i, j] = 0.0
            elif(layer_name == 'storage'):
                sim_value= Euclidean_similarity([devices[i]['storage']], [devices[j]['storage']])
                if(sim_value>= 0.5):
                    sim[i, j] = sim_value
                else:
                    sim[i, j] = 0.0
            elif(layer_name == 'RAM'):
                sim_value= Euclidean_similarity([devices[i]['RAM']], [devices[j]['RAM']])
                if(sim_value>= 0.5):
                    sim[i, j] = sim_value
                else:
                    sim[i, j] = 0.0
            elif (layer_name == 'location'):
                sim[i, j] = Euclidean_similarity([devices[i]['location']['latitude']], [devices[j]['location']['longitude']])

  return sim