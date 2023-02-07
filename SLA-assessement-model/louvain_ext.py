#Py 2/3 Compatibility
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division # use // to specify int div.


from function import get_expected_edges
from function import get_expected_edges_ml
from function import get_sum_internal_edges
from PartitionEnsemble import PartitionEnsemble
from plot_domain import plot_multiplex_community

import sys, os
import tempfile
from contextlib import contextmanager
from multiprocessing import Pool,cpu_count
import itertools
import igraph as ig
import louvain
import numpy as np
import tqdm
from time import time
import warnings
import logging
import operator
import networkx as nx
#logging.basicConfig(format=':%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format=':%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)


iswin = os.name == 'nt'
is_py3 = sys.version_info >= (3, 0)


try:
	import cpickle as pickle
except ImportError:
	import pickle as pickle

@contextmanager
def terminating(obj):
	'''
	Context manager to handle appropriate shutdown of processes
	:param obj: obj to open
	:return:
	'''
	try:
		yield obj
	finally:
		obj.terminate()

'''
Extension of Traag's implementation of louvain in python to use multiprocessing \
and allow for randomization.  Defines PartitionEnsemble a class for storage of \
partitions and coefficients as well as dominant domains.
'''


##### STATIC METHODS FOR LOUVAIN EXT######

def rev_perm(perm):
	'''
	Calculate the reverse of a permuation vector
	:param perm: permutation vector
	:type perm: list
	:return: reverse of permutation
	'''
	rperm=list(np.zeros(len(perm)))
	for i,v in enumerate(perm):
		rperm[v]=i
	return rperm

def permute_vector(rev_order, membership):
	'''
	Rearrange community membership vector according to permutation
	Used to realign community vector output after node permutation.
	:param rev_order: new indices of each nodes
	:param membership: community membership vector to be rearranged
	:return: rearranged membership vector.
	'''
	new_member=[-1 for i in range(len(rev_order))]

	for i,val in enumerate(rev_order):
		new_member[val]=membership[i]
	assert(-1 not in new_member) #Something didn't get switched

	return new_member

def permute_memvec(permutation,membership):
	outvec=np.array([-1 for _ in range(len(membership))])
	for i,val in enumerate(permutation):
		outvec[val]=membership[i]

	return outvec

def run_louvain_windows(graph,gamma,nruns,weight=None,node_subset=None,attribute=None,output_dictionary=False):
	'''
	Call the louvain method with igraph as input directly.  This is needed for windows system\
	because tmp files cannot be closed and reopened
	This takes as input a graph file (instead of the graph object) to avoid duplicating
	references in the context of parallelization.  To allow for flexibility, it allows for
	subsetting of the nodes each time.
	:param graph: igraph
	:param node_subset: Subeset of nodes to keep (either the indices or list of attributes)
	:param gamma: resolution parameter to run louvain
	:param nruns: number of runs to conduct
	:param weight: optional name of weight attribute for the edges if network is weighted.
	:param output_dictionary: Boolean - output a dictionary representation without attached graph.
	:return: list of partition objects
	'''

	np.random.seed() #reset seed for each process

	#Load the graph from the file
	g = graph
	#have to have a node identifier to handle permutations.
	#Found it easier to load graph from file each time than pass graph object among process
	#This means you do have to filter out shared nodes and realign graphs.
	# Can avoid for g1 by passing None

	#
	if node_subset!=None:
		# subset is index of vertices to keep
		if attribute==None:
			gdel=node_subset
		# check to keep nodes with given attribute
		else:
			gdel=[ i for i,val in enumerate(g.vs[attribute]) if val not in node_subset]

		#delete from graph
		g.delete_vertices(gdel)

	if weight is True:
		weight='weight'


	outparts=[]
	for i in range(nruns):
		rand_perm = list(np.random.permutation(g.vcount()))
		rperm = rev_perm(rand_perm)
		gr=g.permute_vertices(rand_perm) #This is just a labelling switch.  internal properties maintined.

		#In louvain > 0.6, change in the way the different methods are called.
		#modpart=louvain.RBConfigurationVertexPartition(gr,resolution_parameter=gamma)
		rp = louvain.find_partition(gr,louvain.RBConfigurationVertexPartition,weights=weight,
									resolution_parameter=gamma)

		#store the coefficients in return object.
		A=get_sum_internal_edges(rp,weight)
		P=get_expected_edges(rp,weight,directed=g.is_directed())


		outparts.append({'partition': permute_vector(rperm, rp.membership),
						 'resolution':gamma,
						 'orig_mod': rp.quality(),
						 'int_edges':A,
						 'exp_edges':P})

	if not output_dictionary:
		return PartitionEnsemble(graph=g,listofparts=outparts)
	else:
		return outparts
	return part_ensemble


def run_louvain(g,gamma,nruns,weight=None,node_subset=None,attribute=None,output_dictionary=False):
	'''
	Call the louvain method for a given graph file.
	This takes as input a graph file (instead of the graph object) to avoid duplicating
	references in the context of parallelization.  To allow for flexibility, it allows for
	subsetting of the nodes each time.
	:param gfile: igraph file.  Must be GraphMlz (todo: other extensions)
	:param node_subset: Subeset of nodes to keep (either the indices or list of attributes)
	:param gamma: resolution parameter to run louvain
	:param nruns: number of runs to conduct
	:param weight: optional name of weight attribute for the edges if network is weighted.
	:param output_dictionary: Boolean - output a dictionary representation without attached graph.
	:return: list of partition objects
	'''

	np.random.seed() #reset seed for each process

	#Load the graph from the file
	#g = ig.Graph.Read_GraphMLz(gfile)
	#have to have a node identifier to handle permutations.
	#Found it easier to load graph from file each time than pass graph object among process
	#This means you do have to filter out shared nodes and realign graphs.
	# Can avoid for g1 by passing None

	#
	if node_subset!=None:
		# subset is index of vertices to keep
		if attribute==None:
			gdel=node_subset
		# check to keep nodes with given attribute
		else:
			gdel=[ i for i,val in enumerate(g.vs[attribute]) if val not in node_subset]

		#delete from graph
		g.delete_vertices(gdel)

	if weight is True:
		weight='weight'


	outparts=[]
	for i in range(nruns):
		rand_perm = list(np.random.permutation(g.vcount()))
		rperm = rev_perm(rand_perm)
		gr=g.permute_vertices(rand_perm) #This is just a labelling switch.  internal properties maintined.

		#In louvain > 0.6, change in the way the different methods are called.
		#modpart=louvain.RBConfigurationVertexPartition(gr,resolution_parameter=gamma)
		rp = louvain.find_partition(gr,louvain.RBConfigurationVertexPartition,weights=weight,
									resolution_parameter=gamma)

		#old way of calling
		# rp = louvain.find_partition(gr, method='RBConfiguration',weight=weight,  resolution_parameter=gamma)

		#store the coefficients in return object.
		A=get_sum_internal_edges(rp,weight)
		P=get_expected_edges(rp,weight,directed=g.is_directed())


		outparts.append({'partition': permute_vector(rperm, rp.membership),
						 'resolution':gamma,
						 'orig_mod': rp.quality(),
						 'int_edges':A,
						 'exp_edges':P})

	if not output_dictionary:
		return PartitionEnsemble(graph=g,listofparts=outparts)
	else:
		return outparts
	return part_ensemble





def _run_louvain_parallel(gfile_gamma_nruns_weight_subset_attribute):
	'''
	Parallel wrapper with single argument input for calling :meth:`louvain_ext.run_louvain`
	:param gfile_att_2_id_dict_shared_gamma_runs_weight: tuple or list of arguments to supply
	:returns: PartitionEnsemble of graph stored in gfile
	'''
	#unpack
	gfile,gamma,nruns,weight,node_subset,attribute=gfile_gamma_nruns_weight_subset_attribute
	t=time()
	outparts=run_louvain(gfile,gamma,nruns=nruns,weight=weight,node_subset=node_subset,attribute=attribute,output_dictionary=True)

	# if progress is not None:
	# 	if progress%update==0:
	# 		print("Run %d at gamma = %.3f.  Return time: %.4f" %(progress,gamma,time()-t))

	return outparts

def parallel_louvain(graph,start=0,fin=1,numruns=200,maxpt=None,nrepeats=1,uselogspace=False,
					 numprocesses=None, attribute=None,weight=None,node_subset=None,progress=None,
                     calc_sim_mat=True):
	'''
	Generates arguments for parallel function call of louvain on graph
	:param graph: igraph object to run Louvain on
	:param start: beginning of range of resolution parameter :math:`\\gamma` . Default is 0.
	:param fin: end of range of resolution parameter :math:`\\gamma`.  Default is 1.
	:param numruns: number of intervals to divide resolution parameter, :math:`\\gamma` range into
	:param maxpt: Cutoff off resolution for domains when applying CHAMP. Default is None
	:type maxpt: int
	:param numprocesses: the number of processes to spawn.  Default is number of CPUs.
	:param weight: If True will use 'weight' attribute of edges in runnning Louvain and calculating modularity.
	:param node_subset:  Optionally list of indices or attributes of nodes to keep while partitioning
	:param attribute: Which attribute to filter on if node_subset is supplied.  If None, node subset is assumed \
	:param nrepeats : int - number of partitions to discover at each value of gamma (default=1)
	:param uselogspace: bool- should runs be linearly spaced (default) or if uselogspace=True, spaced evenly in log10space
	 to be node indices.
	:param progress:  Print progress in parallel execution every `n` iterations.
	:param calc_sim_mat: Should the pairwise comparison of all the champ sets be calculated.  Default is true.  This can take some time for larger champ sets (O(n^2)).  It is used in visualizing.
	:return: PartitionEnsemble of all partitions identified.
	'''
	if uselogspace:
		if start==0: #can't technically be zero for creating log space
			start+=np.power(10.0,-8) #use small value
		gammas=np.logspace(np.log10(start),np.log10(fin),numruns,base=10)
	else:
		gammas=np.linspace(start,fin,numruns)

	if iswin: #on a windows system
		warnings.warn("Parallel Louvain function is not available of windows system.  Running in serial",
					  UserWarning)
		for i,gam in enumerate(gammas):
			cpart_ens=run_louvain_windows(graph=graph,nruns=nrepeats,gamma=gam,node_subset=node_subset,
										attribute=attribute,weight=weight)
			if i==0:
				outpart_ens=cpart_ens
			else:
				outpart_ens=outpart_ens.merge_ensemble(cpart_ens,new=False) #merge current run with new
		return outpart_ens

	parallel_args=[]
	if numprocesses is None:
		numprocesses=cpu_count()

	if weight is True:
		weight='weight'

	tempf=tempfile.NamedTemporaryFile('wb')
	graphfile=tempf.name
	#filter before calling parallel
	if node_subset != None:
		# subset is index of vertices to keep
		if attribute == None:
			gdel = node_subset
		# check to keep nodes with given attribute
		else:
			gdel = [i for i, val in enumerate(graph.vs[attribute]) if val not in node_subset]

		# delete from graph
		graph.delete_vertices(gdel)

	graph.write_graphmlz(graphfile)
	for i,curg in enumerate(gammas):
		# curg = start + ((fin - start) / (1.0 * numruns)) * i
		parallel_args.append((graphfile, curg, nrepeats, weight, None, None))

	parts_list_of_list=[]
	# use a context manager so pools properly shut down
	with terminating(Pool(processes=numprocesses)) as pool:
		if progress:
			tot = len(parallel_args)
			with tqdm.tqdm(total=tot) as pbar:
				# parts_list_of_list=pool.imap(_parallel_run_louvain_multimodularity,args)
				for i, res in tqdm.tqdm(enumerate(pool.imap(_run_louvain_parallel, parallel_args)), miniters=tot):
					# if i % 100==0:
					pbar.update()
					parts_list_of_list.append(res)
		else:
			parts_list_of_list=pool.map(_run_louvain_parallel, parallel_args )

	#for debugging
	# parts_list_of_list=list(map(_run_louvain_parallel,parallel_args))

	all_part_dicts=[pt for partrun in parts_list_of_list for pt in partrun]
	tempf.close()
	outensemble=PartitionEnsemble(graph,listofparts=all_part_dicts,maxpt=maxpt,
                                  calc_sim_mat=calc_sim_mat,all_coefs_present=True)
	return outensemble



#### MULTI-LAYER Louvain static methods

#MUTLILAYER GRAPH CREATION

def _create_interslice(interlayer_edges, layer_vec, directed=False):
	"""
	"""
	weights=[]
	print("This is inter-slice")
	print(interlayer_edges)
	layers = np.unique(layer_vec)
	layer_edges = set()
	for e in interlayer_edges:
		ei,ej=e[0],e[1]
		lay_i = layer_vec[ei]
		lay_j = layer_vec[ej]
		if len(e)>2:
			weights.append(e[2])
		assert lay_i != lay_j #these shoudl be interlayer edges
		if lay_i < lay_j:
			layer_edges.add((lay_i, lay_j))
		else:
			layer_edges.add((lay_j, lay_i))


	slice_couplings = ig.Graph(n=len(layers), edges=list(layer_edges), directed=directed)
	if len(weights) == 0:
		weights=1
	slice_couplings.es['weight']=weights
	#print(slice_couplings)
	return slice_couplings


def _create_multilayer_igraphs_from_super_adj_igraph(intralayer_igraph,layer_vec):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""

	adj=np.array(intralayer_igraph.get_adjacency().data)
	#print("rearranged intralayer_graph:  ")
	#print(adj)
	layer_vals = np.unique(layer_vec)

	layers=[]
	i=0
	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for layer in layer_vals:
		#

		cinds=np.where(layer_vec==layer)[0]
		cedges=set()
		for v in cinds:
			cedges.update(intralayer_igraph.incident(v))

		cedges=list(cedges)
		cgraph=intralayer_igraph.subgraph_edges(edges=cedges,delete_vertices=False)
		layers.append(cgraph)

		#print(layers.__getitem__(i))
		i = i + 1

	return layers


def _create_all_layers_single_igraph(intralayer_edges, layer_vec, directed=False):
	"""
	"""
	#create a single igraph
	layers, cnts = np.unique(layer_vec, return_counts=True)
	layer_elists = []
	layer_weights=[ ]
	# we divide up the edges by layer
	for e in intralayer_edges:
		ei,ej=e[0],e[1]
		if not directed: #switch order to preserve uniqness
			if ei>ej:
				#ei,ej=e[1],e[0]
				ei, ej = e[0], e[1]

		layer_elists.append((ei, ej))
		if len(e)>2:
			layer_weights.append(e[2])
	layer_graphs = []
	print(layer_elists)
	cgraph = ig.Graph(n=len(layer_vec), edges=layer_elists, directed=directed)
	if len(layer_weights) > 0:  # attempt to set the intralayer weights
		cgraph.es['weight'] = layer_weights
	else:
		cgraph.es['weight']=1
	cgraph.vs['nid']=range(cgraph.vcount())
	cgraph.vs['layer_vec']=layer_vec
	return cgraph
	# layer_graphs.append(cgraph)
	# return layer_graphs

def _create_all_layer_igraphs_multi(intralayer_edges, layer_vec, directed=False):
	"""
	"""

	layers, cnts = np.unique(layer_vec, return_counts=True)
	layer_elists = [[] for _ in range(len(layers))]
	layer_weights=[[] for _ in range(len(layers))]
	# we divide up the edges by layer
	for e in intralayer_edges:
		ei,ej=e[0],e[1]
		if not directed: #switch order to preserve uniqness
			if ei>ej:
				ei,ej=e[1],e[0]

		# these should all be intralayer edges
		lay_i, lay_j = layer_vec[ei], layer_vec[ej]
		assert lay_i == lay_j

		coffset=np.sum(cnts[:lay_i])#indexing for edges must start with 0 for igraph

		layer_elists[lay_i].append((ei-coffset, ej-coffset))
		if len(e)>2:
			layer_weights[lay_i].append(e[2])

	layer_graphs = []
	tot = 0
	for i, layer_elist in enumerate(layer_elists):
		if not directed:
			layer_elist=list(set(layer_elist)) #prune out non-unique
		#you have adjust the elist to start with 0 for first node
		cnts[i]
		cgraph = ig.Graph(n=cnts[i], edges=layer_elist, directed=directed)
		assert cgraph.vcount()==cnts[i],'edges indicated more nodes within graph than the layer_vec'
		cgraph.vs['nid'] = range(tot , tot +cnts[i])  # each node in each layer gets a unique id
		if len(layer_weights[i])>0: #attempt to set the intralayer weights
			cgraph.es['weight']=layer_weights[i]
		tot += cnts[i]
		layer_graphs.append(cgraph)

	return layer_graphs


def _label_nodes_by_identity(intralayer_graphs, interlayer_edges, layer_vec):
	"""Go through each of the nodes and determine which ones are shared across multiple slices.\
	We create an attribute on each of the graphs to indicate the shared identity \
	of that node.  This is done through tracking the predecessors of the node vi the interlayer\
	connections
	"""

	namedict = {}
	backedges = {}

	# For each node we hash if it has any neighbors in the layers behind it.

	for e in interlayer_edges:
		ei,ej=e[0],e[1]
		if ei < ej:
			backedges[ej] = backedges.get(ej, []) + [ei]
		else:
			backedges[ei] = backedges.get(ei, []) + [ej]

	offset = 0  # duplicate names used
	for i, lay in enumerate(layer_vec):

		if i not in backedges:  # node doesn't have a predecessor
			namedict[i] = i - offset
		else:
			pred = backedges[i][0] #get one of the predecessors
			namedict[i] = namedict[pred]  # get the id of the predecessor
			offset += 1

	for graph in intralayer_graphs:
		graph.vs['shared_id'] = list(map(lambda x: namedict[x], graph.vs['nid']))
		assert len(set(graph.vs['shared_id']))==len(graph.vs['shared_id']), "IDs within a slice must all be unique"


def create_multilayer_igraph_from_edgelist(intralayer_edges, interlayer_edges, layer_vec, inter_directed=False,
										   intra_directed=False):
	"""
	   We create an igraph representation used by the louvain package to represents multi-slice graphs.  \
	   For this method only two graphs are created :
	   intralayer_graph : all edges withis this graph are treated equally though the null model is adjusted \
	   based on each slice's degree distribution
	   interlayer_graph:  single graph that contains only interlayer connections between all nodes
	:param intralayer_edges: edges representing intralayer connections.  Note each node should be assigned a unique\
	index.
	:param interlayer_edges: connection across layers.
	:param layer_vec: indication of which layer each node is in.  This important in computing the modulary modularity\
	null model.
	:param directed: If the network is directed or not
	:return: intralayer_graph,interlayer_graph
	"""
	t=time()
	interlayer_graph = _create_all_layers_single_igraph(interlayer_edges, layer_vec=layer_vec, directed=inter_directed)
	# interlayer_graph=interlayer_graph[0]
	logging.debug("create interlayer : {:.4f}".format(time()-t))
	t=time()
	intralayer_graph = _create_all_layers_single_igraph(intralayer_edges, layer_vec, directed=intra_directed)
	logging.debug("create intrallayer : {:.4f}".format(time()-t))
	t=time()
	return intralayer_graph,interlayer_graph


def call_slices_to_layers_from_edge_list(intralayer_edges, interlayer_edges, layer_vec, directed=False):
	"""
	   We create an igraph representation used by the louvain package to represents multi-slice graphs.  This returns \
	   three values:
		layers : list of igraphs each one representing a single slice in the network (all nodes across all layers \
		are present but only the edges in that slice)
		interslice_layer: igraph representing interlayer connectiosn
		G_full : igraph with connections for both inter and intra slice connections across all nodes ( differentiated) \
		by igraph.es attribute.
	:param intralayer_edges:
	:param interlayer_edges:
	:param layer_vec:
	:param directed:
	:return: layers
	"""
	t=time()
	interlayer_graph = _create_interslice(interlayer_edges,layer_vec=layer_vec, directed=directed)
	# interlayer_graph=interlayer_graph[0]
	logging.debug("create interlayer : {:.4f}".format(time()-t))
	t=time()
	intralayer_graphs = _create_all_layer_igraphs_multi(intralayer_edges, layer_vec, directed=directed)
	logging.debug("create intrallayer : {:.4f}".format(time()-t))
	t=time()

	_label_nodes_by_identity(intralayer_graphs, interlayer_edges, layer_vec)
	logging.debug("label nodes : {:.4f}".format(time()-t))
	t=time()
	interlayer_graph.vs['slice'] = intralayer_graphs
	layers, interslice_layer, G_full = louvain.slices_to_layers(interlayer_graph, vertex_id_attr='shared_id')
	logging.debug("louvain call : {:.4f}".format(time()-t))
	t=time()
	return layers, interslice_layer, G_full

def adjacency_to_edges(A):
	nnz_inds = np.nonzero(A)
	nnzvals = np.array(A[nnz_inds])
	if len(nnzvals.shape)>1:
		nnzvals=nnzvals[0] #handle scipy sparse types
	#print(list(zip(nnz_inds[0], nnz_inds[1], nnzvals)))
	#print("hi")
	return list(zip(nnz_inds[0], nnz_inds[1], nnzvals))


def create_multilayer_igraph_from_adjacency(A,C,layer_vec,inter_directed=False,intra_directed=False):
	"""
	Create the multilayer igraph representation necessary to call igraph-louvain \
	in the multilayer context.  Edge list are formed and champ_fucntions.create_multilayer_igraph_from_edgelist \
	is called.  Each edge list includes the weight of the edge \
	as indicated in the appropriate adjacency matrix.
	:param A:
	:param C:
	:param layer_vec:
	:return:
	"""

	nnz_inds = np.nonzero(A)
	nnzvals = np.array(A[nnz_inds])
	if len(nnzvals.shape)>1:
		nnzvals=nnzvals[0] #handle scipy sparse types

	intra_edgelist = adjacency_to_edges(A)
	inter_edgelist = adjacency_to_edges(C)


	return create_multilayer_igraph_from_edgelist(intralayer_edges=intra_edgelist,
												  interlayer_edges=inter_edgelist,
												  layer_vec=layer_vec,intra_directed=intra_directed,
												  inter_directed=inter_directed)

# def _save_ml_graph(intralayer_edges,interlayer_edges,layer_vec,filename=None):
#	 if filename is None:
#		 file=tempfile.NamedTemporaryFile()
#	 filename=file.name
#
#	 outdict={"interlayer_edges":interlayer_edges,
#			  'intralayer_edges':intralayer_edges,
#			  'layer_vec':layer_vec}
#
#	 with gzip.open(filename,'w') as fh:
#		 pickle.dump(outdict,fh)
#	 return file #returns the filehandle


def _save_ml_graph(slice_layers,interslice_layer):
	"""
	We save the layers of the graph as graphml.gz files here
	:param slice_layers:
	:param interslice_layer:
	:param layer_vec:
	:return:
	"""
	filehandles=[]
	filenames=[]
	#interslice couplings will be last
	for layer in slice_layers+[interslice_layer]: #save each graph in it's own file handle
		fh=tempfile.NamedTemporaryFile(mode='wb',suffix='.graphml.gz')
		layer.write_graphmlz(fh.name)
		filehandles.append(fh)
		filenames.append(fh.name)
	return filehandles,filenames


def _get_sum_internal_edges_from_partobj_list(part_obj_list,weight='weight'):
	A=0
	for part_obj in part_obj_list:
		A+=get_sum_internal_edges(part_obj,weight=weight)
	return A


def _get_sum_expected_edges_from_partobj_list(part_obj_list,weight='weight'):
	P=0
	for part_obj in part_obj_list:
		#This is the case where we have to split the intralayer adjacency into multiple
		#partition objects.
		P += get_expected_edges(part_obj,weight=weight)
	return P


def _get_modularity_from_partobj_list(part_obj_list,resolution=None):
	finmod=0
	for part_obj in part_obj_list:
		if resolution is None:
			finmod+=part_obj.quality()
		else:
			finmod+=part_obj.quality(resolution_parameter=resolution)
	return finmod

def run_louvain_multilayer(intralayer_graph,interlayer_graph, layer_vec, weight='weight',
						   resolution=1.0, omega=1.0,nruns=1):
	logging.debug('Shuffling node ids')
	t=time()
	#print("Weight:  ", intralayer_graph.es[weight])
	mu=np.sum(intralayer_graph.es[weight])+interlayer_graph.ecount()

	use_RBCweighted = hasattr(louvain, 'RBConfigurationVertexPartitionWeightedLayers')

	outparts=[]
	for run in range(nruns):
		rand_perm = list(np.random.permutation(interlayer_graph.vcount()))
		#print("rand_perm:   ", rand_perm)
		# rand_perm = list(range(interlayer_graph.vcount()))
		rperm = rev_perm(rand_perm)
		#print("rperm:  ", rperm)
		interslice_layer_rand = interlayer_graph.permute_vertices(rand_perm)
		#print('interslice_layer_rand:  ', interslice_layer_rand)
		rlayer_vec=permute_vector(rand_perm,layer_vec)
		#print("rlayer_vec:  ", rlayer_vec)

		rintralayer_graph=intralayer_graph.permute_vertices(rand_perm)
		#print("rintralayer_graph:  ",rintralayer_graph)
		#
		if use_RBCweighted:

			rlayers = [intralayer_graph]  #  one layer representing all intralayer connections here
		else:
			rlayers = _create_multilayer_igraphs_from_super_adj_igraph(rintralayer_graph, layer_vec=rlayer_vec)


		logging.debug('time: {:.4f}'.format(time()-t))

		t=time()

		#create the partition objects
		layer_partition_objs=[]

		logging.debug('creating partition objects')
		t=time()

		for i,layer in enumerate(rlayers): #these are the shuffled igraph slice objects
			try:
				res=resolution[i]
			except:
				res=resolution

			if use_RBCweighted:

				cpart=louvain.RBConfigurationVertexPartitionWeightedLayers(layer,layer_vec=rlayer_vec,weights=weight,resolution_parameter=res)

			else:
				#This creates individual VertexPartition for each layer.  Much slower to optimize.
				cpart=louvain.RBConfigurationVertexPartition(layer,weights=weight,resolution_parameter=res)


			layer_partition_objs.append(cpart)
			#print("this is layer")
			#print(layer)
			#print("partition in Layers:")
			#print("partition in Layer ", i, " : ")
			#print(cpart)


		coupling_partition=louvain.RBConfigurationVertexPartition(interslice_layer_rand,
																  weights=weight,resolution_parameter=0)
		#print('coupling-partition:')
		#print(coupling_partition)
		#print('layer-partition:')
		#print(layer_partition_objs)
		all_layer_partobjs=layer_partition_objs+[coupling_partition]
		#print('all_layer-partition:')
		#print(all_layer_partobjs)
		optimiser=louvain.Optimiser()
		logging.debug('time: {:.4f}'.format(time()-t))
		logging.debug('running optimiser')
		t=time()


		layer_weights=[1]*len(rlayers)+[omega]
		improvement=optimiser.optimise_partition_multiplex(all_layer_partobjs,layer_weights=layer_weights)

		#the membership for each of the partitions is tied together.
		finalpartition=permute_vector(rperm, all_layer_partobjs[0].membership)
		reversed_partobj = []

		#go back and reverse the graphs associated with each of the partobj.  this allows for properly calculating exp edges with partobj
		#This is not ideal.  Could we just reverse the permutation?
		for layer in layer_partition_objs:
			if use_RBCweighted:

				reversed_partobj.append(louvain.RBConfigurationVertexPartitionWeightedLayers(graph=layer.graph.permute_vertices(rperm),initial_membership=finalpartition,weights=weight,layer_vec=layer_vec,resolution_parameter=layer.resolution_parameter))
			else:
				reversed_partobj.append(louvain.RBConfigurationVertexPartition(graph=layer.graph.permute_vertices(rperm),initial_membership=finalpartition,weights=weight,resolution_parameter=layer.resolution_parameter))
		coupling_partition_rev=louvain.RBConfigurationVertexPartition(graph=coupling_partition.graph.permute_vertices(rperm),initial_membership=finalpartition,weights=weight,resolution_parameter=0)
		#use only the intralayer part objs
		A=_get_sum_internal_edges_from_partobj_list(reversed_partobj,weight=weight)
		if use_RBCweighted: #should only one partobj here representing all layers
			P= get_expected_edges_ml(reversed_partobj[0], layer_vec=layer_vec, weight=weight)
		else:
			P=_get_sum_expected_edges_from_partobj_list(reversed_partobj,weight=weight)
		C=get_sum_internal_edges(coupling_partition_rev,weight=weight)
		outparts.append({'partition': np.array(finalpartition),
						 'resolution': resolution,
						 'part':( np.array(reversed_partobj[0])),
						 'membership': reversed_partobj[0].membership,
						 'coupling':omega,
						 'orig_mod': (.5/mu)*(_get_modularity_from_partobj_list(reversed_partobj)\
											  +omega*coupling_partition_rev.quality()),
						 'int_edges': A,
						 'exp_edges': P,
						'int_inter_edges':C})
	#print("############################################################################")
	#print("Partitions in this conditions:", 'coupling: ', omega, 'orig_mod:', (.5/mu)*(_get_modularity_from_partobj_list(reversed_partobj)\
							#				  +omega*coupling_partition_rev.quality()),'int_edges: ', A, 'exp_edges:  ', P, 'int_inter_edges:  ', C)
	#print('resolution: ', resolution)
	#print("Multi_layer partitions:  ", reversed_partobj[0])
	#print("Multi_layer partitions:  ", reversed_partobj[0].__getitem__(0).__getitem__(0))
	#print("all_layer_partobjs[1]", reversed_partobj[1])
	#print("all_layer_partobjs[2]", reversed_partobj[2])
	#print("inter_slice_partition:  ", coupling_partition_rev)
	#print("############################################################################")
	logging.debug('time: {:.4f}'.format(time()-t))
	#plot_multiplex_community( np.array(finalpartition),layer_vec=layer_vec, ax=None, cmap=None)
	#plot_multiplex_community(all_layer_partobjs[0], layer_vec=layer_vec, ax=None, cmap=None)

	return outparts



def _parallel_run_louvain_multimodularity(files_layervec_gamma_omega):
	logging.debug('running parallel')
	t=time()
	# graph_file_names,layer_vec,gamma,omega=files_layervec_gamma_omega
	np.random.seed() #reset seed in forked process
	# louvain.set_rng_seed(np.random.randint(2147483647)) #max value for unsigned long
	intralayer_graph,interlayer_graph,layer_vec,gamma,omega=files_layervec_gamma_omega

	partition =run_louvain_multilayer(intralayer_graph,interlayer_graph, layer_vec=layer_vec, resolution=gamma, omega=omega)
	#print("intra_layer: ", intralayer_graph)
	#print("inter_layer: ", interlayer_graph)
	#print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",test)
	logging.debug('time: {:.4f}'.format(time()-t))
	return partition


def parallel_multilayer_louvain(intralayer_edges,interlayer_edges,layer_vec,
								gamma_range,ngamma,omega_range,nomega,maxpt=None,numprocesses=2,progress=True,
								intra_directed=False,inter_directed=False):

	"""
	:param intralayer_edges:
	:param interlayer_edges:
	:param layer_vec:
	:param gamma_range:
	:param ngamma:
	:param omega_range:
	:param nomega:
	:param maxpt:
	:param numprocesses:
	:param progress:
	:param intra_directed:
	:param inter_directed:
	:return:
	"""



	logging.debug('creating graphs from edges')
	t=time()
	intralayer_graph,interlayer_graph=create_multilayer_igraph_from_edgelist(
        intralayer_edges=intralayer_edges,
	    interlayer_edges=interlayer_edges,
		layer_vec=layer_vec,inter_directed=inter_directed,
		intra_directed=intra_directed)
	#print("The intralayer edges:")
	#print(intralayer_graph)
	#print("The interlayer edges:")
	#print(interlayer_graph)

	if not hasattr(louvain, 'RBConfigurationVertexPartitionWeightedLayers'):
		warnings.warn(
			"RBConfigurationVertexPartitionWeightedLayers not present in louvain package.  Falling back on creating igraph for each layer.  Note for networks with many layers this can result in considerable slowdown.")


	logging.debug('time {:.4f}'.format(time() - t))
	# logging.debug('graph to file')
	# t = time()
	# fhandles, fnames = _save_ml_graph(slice_layers=[intralayer_graph],
	#								   interslice_layer=interlayer_graph)
	# logging.debug('time {:.4f}'.format(time() - t))

	gammas=np.linspace(gamma_range[0],gamma_range[1],num=ngamma)
	omegas=np.linspace(omega_range[0],omega_range[1],num=nomega)


	args = itertools.product([intralayer_graph],[interlayer_graph], [layer_vec],
							 gammas,omegas)
	#print(args)
	tot=ngamma*nomega
	with terminating(Pool(numprocesses)) as pool:
		parts_list_of_list = []

		if progress:
			with tqdm.tqdm(total=tot) as pbar:
				# parts_list_of_list=pool.imap(_parallel_run_louvain_multimodularity,args)
				for i,res in tqdm.tqdm(enumerate(pool.imap(_parallel_run_louvain_multimodularity,args)),miniters=tot):
					# if i % 100==0:
					pbar.update()
					parts_list_of_list.append(res)
					#print(res[0]['part'])
					#reversed_partobj
		           # partition.append(res)
		else:
			for i, res in enumerate(pool.imap(_parallel_run_louvain_multimodularity, args)):
				parts_list_of_list.append(res)
				#partition.append(res)
			#parts_list_of_list=list(map(_parallel_run_louvain_multimodularity,args)) #testing without parallel.

	# return all_part_dicts

	all_part_dicts=[pt for partrun in parts_list_of_list for pt in partrun]
	#print("all_part_dicts:    ", all_part_dicts)
	outensemble =PartitionEnsemble(graph=intralayer_graph,interlayer_graph=interlayer_graph,
								   layer_vec=layer_vec,all_coefs_present=True, listofparts=all_part_dicts,maxpt=maxpt)
	return all_part_dicts
	#return outensemble

def parallel_multilayer_louvain_from_adj(intralayer_adj,interlayer_adj,layer_vec,
								gamma_range,ngamma,omega_range,nomega,maxpt=None,numprocesses=2,progress=True,
								intra_directed=False, inter_directed=False):

	"""Call parallel multilayer louvain with adjacency matrices """
	#print(intralayer_adj)
	#print(interlayer_adj)
	intralayer_edges=adjacency_to_edges(intralayer_adj)
	interlayer_edges=adjacency_to_edges(interlayer_adj)

	return parallel_multilayer_louvain(intralayer_edges=intralayer_edges,interlayer_edges=interlayer_edges,
									   layer_vec=layer_vec,numprocesses=numprocesses,ngamma=ngamma,nomega=nomega,
									   gamma_range=gamma_range,omega_range=omega_range,progress=progress,maxpt=maxpt,
									   intra_directed=intra_directed,inter_directed=inter_directed)


#############################################################################################################################


#############################################################################################################################
def _create_multilayer_igraphs_from_super_adj_igraph1(new_nodes, del_nodes, intralayer_igraph, prepartition,
													  premembership, layer_vec):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""
	del_size = len(del_nodes)
	del_ids = []
	init_par = []
	layer_vals = np.unique(layer_vec)

	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	#print("There are ", len(prepartition), "initial partitions.")
	#print("The initial partitions: ", prepartition)
	#print("Pre_membership:", premembership)
	all_nodes = 0
	count = 0

	Graph_nodes = []
	for i in range(partition_num):
		init_par.append(prepartition[i])
	# print(init_par)

	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(del_size):
		l = 0
		d_ids = []
		for layer in layer_vals:

			cinds = np.where(layer_vec == layer)[0]
			cedges = set()
			node_count = len(cinds)
			all_nodes = all_nodes + node_count
			pre_node_num = len(cinds) + del_size
			if l == 0:
				del_id = del_nodes[node]
			else:
				del_id = del_id + (len(cinds) + del_size)
			d_ids.append(del_id)
			for p in range(len(init_par)):
				if (del_id in init_par[p]):
					init_par[p].remove(del_id)
			for v in cinds:
				cedges.update(intralayer_igraph.incident(v))

			cedges = list(cedges)
			# print(cedges)
			cgraph = intralayer_igraph.subgraph_edges(edges=cedges, delete_vertices=False)
			l = l + 1
		del_ids.append(d_ids)
		p = 0
		for i in range(len(init_par)):
			if len(init_par[i - p]) == 0:
				init_par.pop(i - p)
				p = p + 1

	#print("initpar", init_par)
	par_dict = []
	sorted_Par = []
	for p in range(len(init_par)):
		item = 0
		for i in range(int(len(init_par[p]) / 3)):
			Len = int(len(init_par[p]) / 3)
			par_dict.append({'id': p, 'firstitem': init_par[p][item],
							 'par': [init_par[p][item], init_par[p][item + Len], init_par[p][item + 2 * Len]]})
			item = item + 1

	for items in sorted(par_dict, key=operator.itemgetter("firstitem")):
		sorted_Par.append(items)
	#print(sorted_Par)

	l = 0
	for layer in layer_vals:
		for p in range(len(par_dict)):
			for d in range(len(del_ids)):
				if (sorted_Par[p]['par'][l] < del_ids[d][l]):
					sorted_Par[p]['par'][l] = sorted_Par[p]['par'][l] - (d + (del_size * (l)))
					break
				elif (d == len(del_ids) - 1):
					sorted_Par[p]['par'][l] = sorted_Par[p]['par'][l] - ((d + 1) + (del_size * (l)))
					break
		l = l + 1
	#print(sorted_Par)

	par_dict = []
	for items in sorted(sorted_Par, key=operator.itemgetter("id")):
		par_dict.append(items)
	#print(par_dict)
	id = -1
	new_i = -1
	new_par = []
	for p in range(len(par_dict)):
		if par_dict[p]['id'] == id:
			new_par[new_i] = new_par[new_i] + par_dict[p]['par']
			new_par[new_i].sort()
			id = par_dict[p - 1]['id']
		else:
			new_i = new_i + 1
			new_par.append(par_dict[p]['par'])
			id = par_dict[p]['id']

	#print(new_par)
	#print("premembership size: ", len(premembership))
	#print("deleted nodes:", del_ids)
	for d in range(len(del_ids)):
		for nodes in range(len(d_ids)):
			# premembership.pop(del_ids[d][nodes]-(((nodes)*(d))))
			premembership.pop(del_ids[d][nodes] - ((nodes) + (nodes * d) + d))

	new_membership = premembership
	#print( "New membership size:", len(new_membership))
	for p in range(len(new_par)):
		for i in range(len(new_par[p])):
			new_membership[new_par[p][i]] = p

	for layer in layer_vals:
		for i in range(node_count):
			Graph_nodes.append(count)
			count = count + 1

	new_membership = premembership
	#print("Graph_nodes: ", Graph_nodes)
	#print("new_membership: ", new_membership)
	#print("Partitions:  ", new_par)
	partition_dict = dict(zip(Graph_nodes, new_membership))
	#print(partition_dict)

	return new_membership, new_par


def _create_all_layers_single_igraph1(intralayer_edges, layer_vec, directed=False):
	"""
	"""
	# create a single igraph
	layers, cnts = np.unique(layer_vec, return_counts=True)
	layer_elists = []
	layer_weights = []
	# we divide up the edges by layer
	for e in intralayer_edges:
		ei, ej = e[0], e[1]
		if not directed:  # switch order to preserve uniqness
			if ei > ej:
				# ei,ej=e[1],e[0]
				ei, ej = e[0], e[1]

		layer_elists.append((ei, ej))
		if len(e) > 2:
			layer_weights.append(e[2])
	layer_graphs = []
	# print(layer_elists)
	cgraph = ig.Graph(n=len(layer_vec), edges=layer_elists, directed=directed)
	if len(layer_weights) > 0:  # attempt to set the intralayer weights
		cgraph.es['weight'] = layer_weights
	else:
		cgraph.es['weight'] = 1
	cgraph.vs['nid'] = range(cgraph.vcount())
	cgraph.vs['layer_vec'] = layer_vec
	# print("output of _create_all_layers_single_igraph function:  ")
	# print(cgraph)

	return cgraph


def run_louvain_multilayer1(new_nodes, del_nodes, intralayer_graph, interlayer_graph, prepartition, premembership,
							layer_vec, weight='weight',
							resolution=1.0, omega=1.0, nruns=1):
	logging.debug('Shuffling node ids')
	t = time()
	# print("Weight:  ", intralayer_graph.es[weight])
	mu = np.sum(intralayer_graph.es[weight]) + interlayer_graph.ecount()

	use_RBCweighted = hasattr(louvain, 'RBConfigurationVertexPartitionWeightedLayers')

	outparts = []

	new_mem, new_par = _create_multilayer_igraphs_from_super_adj_igraph1(new_nodes, del_nodes, intralayer_graph,
																		 prepartition, premembership,
																		 layer_vec=layer_vec)

	outparts.append({'partition': new_par,
					 'new_membership': new_mem})

	return outparts


def create_multilayer_igraph_from_edgelist1(intralayer_edges, interlayer_edges, layer_vec, inter_directed=False,
											intra_directed=False):
	"""
	   We create an igraph representation used by the louvain package to represents multi-slice graphs.  \
	   For this method only two graphs are created :
	   intralayer_graph : all edges withis this graph are treated equally though the null model is adjusted \
	   based on each slice's degree distribution
	   interlayer_graph:  single graph that contains only interlayer connections between all nodes
	:param intralayer_edges: edges representing intralayer connections.  Note each node should be assigned a unique\
	index.
	:param interlayer_edges: connection across layers.
	:param layer_vec: indication of which layer each node is in.  This important in computing the modulary modularity\
	null model.
	:param directed: If the network is directed or not
	:return: intralayer_graph,interlayer_graph
	"""
	t = time()
	interlayer_graph = _create_all_layers_single_igraph1(interlayer_edges, layer_vec=layer_vec, directed=inter_directed)
	# interlayer_graph=interlayer_graph[0]
	logging.debug("create interlayer : {:.4f}".format(time() - t))
	t = time()
	intralayer_graph = _create_all_layers_single_igraph1(intralayer_edges, layer_vec, directed=intra_directed)
	logging.debug("create intrallayer : {:.4f}".format(time() - t))
	t = time()
	return intralayer_graph, interlayer_graph


def _parallel_run_louvain_multimodularity1(files_layervec_gamma_omega):
	logging.debug('running parallel')
	t = time()
	# graph_file_names,layer_vec,gamma,omega=files_layervec_gamma_omega
	np.random.seed()  # reset seed in forked process
	# louvain.set_rng_seed(np.random.randint(2147483647)) #max value for unsigned long
	new_nodes, del_nodes, intralayer_graph, interlayer_graph, layer_vec, gamma, omega, prepartition, premembership = files_layervec_gamma_omega

	partition = run_louvain_multilayer1(new_nodes, del_nodes, intralayer_graph, interlayer_graph, prepartition,
										premembership, layer_vec=layer_vec, resolution=gamma, omega=omega)
	# print("intra_layer: ", intralayer_graph)
	# print("inter_layer: ", interlayer_graph)
	# print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",test)
	logging.debug('time: {:.4f}'.format(time() - t))
	return partition


def parallel_multilayer_louvain1(new_nodes, del_nodes, intralayer_edges, interlayer_edges, prepartition, premembership,
								 layer_vec,
								 gamma_range, ngamma, omega_range, nomega, maxpt=None, numprocesses=2, progress=True,
								 intra_directed=False, inter_directed=False):
	"""
	:param intralayer_edges:
	:param interlayer_edges:
	:param layer_vec:
	:param gamma_range:
	:param ngamma:
	:param omega_range:
	:param nomega:
	:param maxpt:
	:param numprocesses:
	:param progress:
	:param intra_directed:
	:param inter_directed:
	:return:
	"""

	logging.debug('creating graphs from edges')
	t = time()
	intralayer_graph, interlayer_graph = create_multilayer_igraph_from_edgelist1(
		intralayer_edges=intralayer_edges,
		interlayer_edges=interlayer_edges,
		layer_vec=layer_vec, inter_directed=inter_directed,
		intra_directed=intra_directed)
	# print("The intralayer edges:")
	# print(intralayer_graph)
	# print("The interlayer edges:")
	# print(interlayer_graph)

	if not hasattr(louvain, 'RBConfigurationVertexPartitionWeightedLayers'):
		warnings.warn(
			"RBConfigurationVertexPartitionWeightedLayers not present in louvain package.  Falling back on creating igraph for each layer.  Note for networks with many layers this can result in considerable slowdown.")

	logging.debug('time {:.4f}'.format(time() - t))
	# logging.debug('graph to file')
	# t = time()
	# fhandles, fnames = _save_ml_graph(slice_layers=[intralayer_graph],
	#								   interslice_layer=interlayer_graph)
	# logging.debug('time {:.4f}'.format(time() - t))

	gammas = np.linspace(gamma_range[0], gamma_range[1], num=ngamma)
	omegas = np.linspace(omega_range[0], omega_range[1], num=nomega)
	args = itertools.product([new_nodes], [del_nodes], [intralayer_graph], [interlayer_graph], [layer_vec],
							 gammas, omegas, [prepartition], [premembership])
	# print(args)
	tot = ngamma * nomega
	with terminating(Pool(numprocesses)) as pool:
		parts_list_of_list = []

		if progress:
			with tqdm.tqdm(total=tot) as pbar:
				# parts_list_of_list=pool.imap(_parallel_run_louvain_multimodularity,args)
				for i, res in tqdm.tqdm(enumerate(pool.imap(_parallel_run_louvain_multimodularity1, args)),
										miniters=tot):
					# if i % 100==0:
					pbar.update()
					parts_list_of_list.append(res)
			# print(res[0]['part'])
			# reversed_partobj
		# partition.append(res)
		else:
			for i, res in enumerate(pool.imap(_parallel_run_louvain_multimodularity1, args)):
				parts_list_of_list.append(res)
		# partition.append(res)
	# parts_list_of_list=list(map(_parallel_run_louvain_multimodularity,args)) #testing without parallel.

	# return all_part_dicts

	all_part_dicts = [pt for partrun in parts_list_of_list for pt in partrun]

	return all_part_dicts


def update_multilayer_partitions(intralayer_adj, new_nodes, del_nodes, interlayer_adj, prepartition,
										  premembership, layer_vec,
										  gamma_range, ngamma, omega_range, nomega, maxpt=None, numprocesses=2,
										  progress=True,
										  intra_directed=False, inter_directed=False):
	"""Call parallel multilayer louvain with adjacency matrices """
	# print(intralayer_adj)
	# print(interlayer_adj)
	intralayer_edges = adjacency_to_edges(intralayer_adj)
	interlayer_edges = adjacency_to_edges(interlayer_adj)

	return parallel_multilayer_louvain1(new_nodes=new_nodes, del_nodes=del_nodes, intralayer_edges=intralayer_edges,
										interlayer_edges=interlayer_edges, prepartition=prepartition,
										premembership=premembership,
										layer_vec=layer_vec, numprocesses=numprocesses, ngamma=ngamma, nomega=nomega,
										gamma_range=gamma_range, omega_range=omega_range, progress=progress,
										maxpt=maxpt,
										intra_directed=intra_directed, inter_directed=inter_directed)

#############################################################################################################################


#############################################################################################################################

def _create_multilayer_igraphs_from_super_adj_igraph2(new_nodes,intralayer_igraph,prepartition,premembership,layer_vec):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""
	add_size=new_nodes
	adj=np.array(intralayer_igraph.get_adjacency().data)
	#print("rearranged intralayer_graph:  ")
	#print(adj)
	#intralayer_igraph.neighbors(34)
	init_par=[]
	Graph=[]
	multilayer_nodes=[]
	layer_vals = np.unique(layer_vec)
	layers=[]
	P_strength = np.zeros((len(prepartition)))
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	#print("There are ",len(prepartition),"initial partitions.")
	#print("The initial partitions: ",prepartition)
	all_nodes=0
	Graph_nodes=[]
	partition_info = []
	sorted_par_inf = []
	for i in range(partition_num):
		init_par.append(prepartition[i])
	#print(init_par)
	l=0
	node_count=0
	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(1,add_size):
		for layer in layer_vals:
			#

			shift=add_size*l

			cinds=np.where(layer_vec==layer)[0]
			n= len(cinds)-node
			new_node=cinds[n]

			neighbors=intralayer_igraph.neighbors(new_node)

			#print("neighbors of node ",new_node," : ", neighbors)
			cedges = set()
			node_count = len(cinds)
			all_nodes= all_nodes+node_count

			for v in neighbors:
				cedges.update(intralayer_igraph.incident(v))

			cedges = list(cedges)
			#print(cedges)
			cgraph = intralayer_igraph.subgraph_edges(edges=cedges, delete_vertices=False)
			#convert igraph to networkx graph
			A = [edge.tuple for edge in cgraph.es]
			g = nx.Graph(A)
			Graph.append(g.nodes)
			for v in neighbors:
				if(v!=new_node):

					w1=cgraph.es.select(_source=new_node, _target=v)['weight']
					#w1 = g[n][v]['weight']
					#print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1[0])
					v=v-shift
					for p in range(partition_num):
						if (v in init_par[p]):
							#print(init_par[p])
							P_strength[p] = P_strength[p] + w1[0]
			layers.append(cgraph)
			l = l + 1
			#print("layer", l, " :", cgraph)

		for i in range(partition_num):
			partition_info.append({'id': i, 'strength': P_strength[i]})

		for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
			sorted_par_inf.append(sorted_inf)
		count=0
		#print(sorted_par_inf)
	for layer in layer_vals:
		for i in range(node_count):
			Graph_nodes.append(count)
			count=count+1
	#print("Graph Nodes:  ",Graph_nodes)
	#for i in range(len(Graph)):
		#for j in range(len(Graph[i])):
			#multilayer_nodes.append(Graph[i][j])

	#print("Pre_membership:",premembership)
	membership = premembership
	new_membership=[]

	# print("Layers:")
	# print(layers.__getitem__(i))

	for p in range(len(sorted_par_inf)):
		l = 0
		for layer in layer_vals:

			l = l + 1
			#init_modularity = partition.recalculate_modularity()
			#print("modularity:  ", init_modularity)
			#print(partition)
			#init_membership_0 = partition.membership
			#init_membership_0.append(partition_num)
			for i in range(node_count):
				if i >= (node_count-add_size):
					new_membership.append(sorted_par_inf[p]['id'])
					prepartition[sorted_par_inf[p]['id']].append((i+add_size)*l)
				else:
					new_membership.append(membership[i])
				#prepartition[sorted_par_inf[p]['id']].append()


		#print("Graph_nodes: ",Graph_nodes)
		#print("new_membership: ",new_membership)
		#print(prepartition)
		partition_dict = dict(zip(Graph_nodes, new_membership))
		print(partition_dict)
		#new_modularity_0 = community_louvain.modularity(partition_dict_0, G)
		#new_modularity = community_louvain.modularity(partition_dict, Graph)
		#print("new_modularity if we consider new node in a seperate partition:  ", new_modularity_0)
		#print("new_modularity:  ", new_modularity)
		break
	new_par = prepartition
	for i in range(len(new_membership)):
		Par[new_membership[i]].append(Graph_nodes[i])
	#for i in range(len(new_membership)):
		#Par[new_membership[i]].append(Graph_nodes[i])
	#print("partitions:  ", Par)
	return new_membership, Par
	# print("intralayer_igraph:  ",intralayer_igraph)
     # print("layers:", layers)



def _create_all_layers_single_igraph2(intralayer_edges, layer_vec, directed=False):
	"""
	"""
	#create a single igraph
	layers, cnts = np.unique(layer_vec, return_counts=True)
	layer_elists = []
	layer_weights=[ ]
	# we divide up the edges by layer
	for e in intralayer_edges:
		ei,ej=e[0],e[1]
		if not directed: #switch order to preserve uniqness
			if ei>ej:
				#ei,ej=e[1],e[0]
				ei, ej = e[0], e[1]

		layer_elists.append((ei, ej))
		if len(e)>2:
			layer_weights.append(e[2])
	layer_graphs = []
	#print(layer_elists)
	cgraph = ig.Graph(n=len(layer_vec), edges=layer_elists, directed=directed)
	if len(layer_weights) > 0:  # attempt to set the intralayer weights
		cgraph.es['weight'] = layer_weights
	else:
		cgraph.es['weight']=1
	cgraph.vs['nid']=range(cgraph.vcount())
	cgraph.vs['layer_vec']=layer_vec
	#print("output of _create_all_layers_single_igraph function:  ")
	#print(cgraph)

	return cgraph


def run_louvain_multilayer2(new_nodes,intralayer_graph,interlayer_graph,prepartition, premembership,layer_vec, weight='weight',
						   resolution=1.0, omega=1.0,nruns=1):
	logging.debug('Shuffling node ids')
	t=time()
	#print("Weight:  ", intralayer_graph.es[weight])
	mu=np.sum(intralayer_graph.es[weight])+interlayer_graph.ecount()

	use_RBCweighted = hasattr(louvain, 'RBConfigurationVertexPartitionWeightedLayers')

	outparts=[]

	new_mem, new_par = _create_multilayer_igraphs_from_super_adj_igraph2(new_nodes,intralayer_graph,prepartition,premembership,layer_vec=layer_vec)

	outparts.append({'partition': new_par,
						'new_membership': new_mem})


	return outparts



def create_multilayer_igraph_from_edgelist2(intralayer_edges, interlayer_edges, layer_vec, inter_directed=False,
										   intra_directed=False):
	"""
	   We create an igraph representation used by the louvain package to represents multi-slice graphs.  \
	   For this method only two graphs are created :
	   intralayer_graph : all edges withis this graph are treated equally though the null model is adjusted \
	   based on each slice's degree distribution
	   interlayer_graph:  single graph that contains only interlayer connections between all nodes
	:param intralayer_edges: edges representing intralayer connections.  Note each node should be assigned a unique\
	index.
	:param interlayer_edges: connection across layers.
	:param layer_vec: indication of which layer each node is in.  This important in computing the modulary modularity\
	null model.
	:param directed: If the network is directed or not
	:return: intralayer_graph,interlayer_graph
	"""
	t=time()
	interlayer_graph = _create_all_layers_single_igraph2(interlayer_edges, layer_vec=layer_vec, directed=inter_directed)
	# interlayer_graph=interlayer_graph[0]
	logging.debug("create interlayer : {:.4f}".format(time()-t))
	t=time()
	intralayer_graph = _create_all_layers_single_igraph2(intralayer_edges, layer_vec, directed=intra_directed)
	logging.debug("create intrallayer : {:.4f}".format(time()-t))
	t=time()
	return intralayer_graph,interlayer_graph


def _parallel_run_louvain_multimodularity2(files_layervec_gamma_omega):
	logging.debug('running parallel')
	t=time()
	# graph_file_names,layer_vec,gamma,omega=files_layervec_gamma_omega
	np.random.seed() #reset seed in forked process
	# louvain.set_rng_seed(np.random.randint(2147483647)) #max value for unsigned long
	new_nodes,intralayer_graph,interlayer_graph,layer_vec,gamma,omega, prepartition,premembership=files_layervec_gamma_omega

	partition =run_louvain_multilayer2(new_nodes,intralayer_graph,interlayer_graph,prepartition, premembership,layer_vec=layer_vec,resolution=gamma, omega=omega)
	#print("intra_layer: ", intralayer_graph)
	#print("inter_layer: ", interlayer_graph)
	#print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",test)
	logging.debug('time: {:.4f}'.format(time()-t))
	return partition



def parallel_multilayer_louvain2(new_nodes,intralayer_edges,interlayer_edges, prepartition,premembership,layer_vec,
								gamma_range,ngamma,omega_range,nomega,maxpt=None,numprocesses=2,progress=True,
								intra_directed=False,inter_directed=False):

	"""
	:param intralayer_edges:
	:param interlayer_edges:
	:param layer_vec:
	:param gamma_range:
	:param ngamma:
	:param omega_range:
	:param nomega:
	:param maxpt:
	:param numprocesses:
	:param progress:
	:param intra_directed:
	:param inter_directed:
	:return:
	"""



	logging.debug('creating graphs from edges')
	t=time()
	intralayer_graph,interlayer_graph=create_multilayer_igraph_from_edgelist2(
        intralayer_edges=intralayer_edges,
	    interlayer_edges=interlayer_edges,
		layer_vec=layer_vec,inter_directed=inter_directed,
		intra_directed=intra_directed)
	#print("The intralayer edges:")
	#print(intralayer_graph)
	#print("The interlayer edges:")
	#print(interlayer_graph)



	if not hasattr(louvain, 'RBConfigurationVertexPartitionWeightedLayers'):
		warnings.warn(
			"RBConfigurationVertexPartitionWeightedLayers not present in louvain package.  Falling back on creating igraph for each layer.  Note for networks with many layers this can result in considerable slowdown.")


	logging.debug('time {:.4f}'.format(time() - t))


	gammas=np.linspace(gamma_range[0],gamma_range[1],num=ngamma)
	omegas=np.linspace(omega_range[0],omega_range[1],num=nomega)



	args = itertools.product([new_nodes],[intralayer_graph],[interlayer_graph], [layer_vec],
							 gammas,omegas,[prepartition],[premembership])
	#print(args)
	tot=ngamma*nomega
	with terminating(Pool(numprocesses)) as pool:
		parts_list_of_list = []

		if progress:
			with tqdm.tqdm(total=tot) as pbar:
				# parts_list_of_list=pool.imap(_parallel_run_louvain_multimodularity,args)
				for i,res in tqdm.tqdm(enumerate(pool.imap(_parallel_run_louvain_multimodularity2,args)),miniters=tot):
					# if i % 100==0:
					pbar.update()
					parts_list_of_list.append(res)
					#print(res[0]['part'])
					#reversed_partobj
		           # partition.append(res)
		else:
			for i, res in enumerate(pool.imap(_parallel_run_louvain_multimodularity2, args)):
				parts_list_of_list.append(res)
				#partition.append(res)
			#parts_list_of_list=list(map(_parallel_run_louvain_multimodularity,args)) #testing without parallel.

	# return all_part_dicts

	all_part_dicts=[pt for partrun in parts_list_of_list for pt in partrun]

	return all_part_dicts


def update_add_multilayer_partition(intralayer_adj,new_nodes,interlayer_adj,prepartition,premembership,layer_vec,
								gamma_range,ngamma,omega_range,nomega,maxpt=None,numprocesses=2,progress=True,
								intra_directed=False, inter_directed=False):

	"""Call parallel multilayer louvain with adjacency matrices """
	#print(intralayer_adj)
	#print(interlayer_adj)
	intralayer_edges=adjacency_to_edges(intralayer_adj)
	interlayer_edges=adjacency_to_edges(interlayer_adj)

	return parallel_multilayer_louvain2(new_nodes=new_nodes,intralayer_edges=intralayer_edges,interlayer_edges=interlayer_edges,prepartition=prepartition,premembership=premembership,
									   layer_vec=layer_vec,numprocesses=numprocesses,ngamma=ngamma,nomega=nomega,
									   gamma_range=gamma_range,omega_range=omega_range,progress=progress,maxpt=maxpt,
									   intra_directed=intra_directed,inter_directed=inter_directed)

########################################################################################################################


########################################################################################################################

def monolaye_update_partition_del(del_nodes,pre_graph,graph,prepartition,pre_membership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
"""
	premembership=[]
	for i in range(len(pre_membership)):
		premembership.append(pre_membership[i])
	del_size=len(del_nodes)
	#print("")
	init_par=[]
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	#print("There are ",len(prepartition),"initial partitions.")
	#print("The initial partitions: ",prepartition)
	#print("Pre_membership:", premembership)
	all_nodes=0
	count=0

	Graph_nodes=[]
	for i in range(partition_num):
		init_par.append(prepartition[i])
	#print(init_par)

	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(del_size):
			d_ids=[]
			node_count = graph.vcount()
			all_nodes= all_nodes+node_count
			pre_node_num = node_count+ del_size
			del_id= del_nodes[node]
			for p in range(len(init_par)):
				if (del_id in init_par[p]):
						init_par[p].remove(del_id)
			p=0
			for i in range(len(init_par)):
				if len(init_par[i-p])==0:
					init_par.pop(i-p)
					p = p +1


	new_par=init_par

	for p in range(len(init_par)):
		s=0
		for d in range(len(del_nodes)):
			for i in range(len(init_par[p])):
				if i>s:
					if new_par[p][i]<del_nodes[d]:
						new_par[p][i] = init_par[p][i] - d
					elif d==len(del_nodes)-1:
						new_par[p][i] = init_par[p][i] - (d+1)
					else:
						s=i-1
						break

	#print(new_par)


	#print("deleted nodes:", del_nodes)
	d=0
	for nodes in range(len(del_nodes)):
		premembership.pop(del_nodes[nodes]-d)
		d=d+1


	new_membership = premembership

	for p in range(len(new_par)):
		for i in range(len(new_par[p])):
			new_membership[new_par[p][i]]= p


	for i in range(node_count):
		Graph_nodes.append(count)
		count = count + 1

	#print("Graph_nodes: ",Graph_nodes)
	#print("new_membership: ",new_membership)
	#print("Partitions11:  ", new_par)
	partition_dict = dict(zip(Graph_nodes, new_membership))
	#print(partition_dict)

	return new_par,new_membership



########################################################################################################################

########################################################################################################################
def monolaye_update_partition_del1(del_nodes,pre_graph,graph,prepartition,pre_membership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
"""
	premembership=[]
	for i in range(len(pre_membership)):
		premembership.append(pre_membership[i])
	del_size=len(del_nodes)
	#print("")
	init_par=[]
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	#print("There are ",len(prepartition),"initial partitions.")
	#print("The initial topo partitions: ",prepartition)
	#print("Pre_membership:", premembership)
	all_nodes=0
	count=0
	cedges=[]
	pre_neighbors_list=[]
	Graph_nodes=[]
	for i in range(partition_num):
		init_par.append(prepartition[i])
	#print(init_par)

	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(del_size):
			node_count = graph.vcount()
			all_nodes= all_nodes+node_count
			pre_node_num = node_count+ del_size
			del_id= del_nodes[node]
			for p in range(len(init_par)):
				if (del_id in init_par[p]):
						init_par[p].remove(del_id)
			p=0
			for i in range(len(init_par)):
				if len(init_par[i-p])==0:
					init_par.pop(i-p)
					p = p +1

			neighbors = pre_graph.neighbors(del_id)
			#neighbors.remove(del_id)
			#print("The previous neighbors of deleted node ",del_id,":  ", neighbors)
			neighbors.sort()
			pre_neighbors_list.append(neighbors)
	neighbors_list=pre_neighbors_list
	for j in range(len(neighbors_list)):
		s = -1
		p=0
		for d in range(len(del_nodes)):
			for i in range(len(neighbors_list[j])):
				if i>s:
					if neighbors_list[j][i-p]==del_nodes[d]:
					   neighbors_list[j].remove(neighbors_list[j][i-p])
					   p=p+1
					elif neighbors_list[j][i-p]<del_nodes[d]:
						neighbors_list[j][i-p] = pre_neighbors_list[j][i-p] - d
					elif d==len(del_nodes)-1:
						neighbors_list[j][i-p] = pre_neighbors_list[j][i-p] - (d+1)
					else:
						s=i-p-1
						break
	#print(neighbors_list)
	#print("neighbors of node ", del_id, " : ", list(neighbors))


	new_par=init_par

	for p in range(len(init_par)):
		s=0
		for d in range(len(del_nodes)):
			for i in range(len(init_par[p])):
				if i>s:
					if new_par[p][i]<del_nodes[d]:
						new_par[p][i] = init_par[p][i]-d
					elif d==len(del_nodes)-1:
						new_par[p][i] = init_par[p][i]-(d+1)
					else:
						s=i-1
						break

	#print(new_par)
	dev=0
	sep=[]
	for i in range(len(neighbors_list)):
		for v in neighbors_list[i]:
			edges=graph.incident(v)
			#print("This is v: ", v)
			if len(edges)==0:
				dev=dev+1
				#print("This is v that should be moved to a new partition: ", v)
				if v not in sep:
					new_par.append([v])
					sep.append(v)
					for p in range(len(new_par)-dev):
						if (v in new_par[p]):
							new_par[p].remove(v)
	#print(new_par)
	#print("deleted nodes:", del_nodes)
	d=0
	for nodes in range(len(del_nodes)):
		premembership.pop(del_nodes[nodes]-d)
		d=d+1


	new_membership = premembership

	for p in range(len(new_par)):
		for i in range(len(new_par[p])):
			new_membership[new_par[p][i]]= p


	for i in range(node_count):
		Graph_nodes.append(count)
		count = count + 1

	#print("Graph_nodes: ",Graph_nodes)
	#print("new_membership: ",new_membership)
	#print("Partitions11:  ", new_par)
	partition_dict = dict(zip(Graph_nodes, new_membership))
	#print(partition_dict)

	return new_par,new_membership



########################################################################################################################

########################################################################################################################

def monolaye_update_partition_del2(del_nodes,pre_graph,graph,G,prepartition,pre_membership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
"""
	premembership=[]
	for i in range(len(pre_membership)):
		premembership.append(pre_membership[i])
	del_size=len(del_nodes)
	init_par=[]
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	#print("There are ",len(prepartition),"initial partitions.")
	#print("The initial topo partitions: ",prepartition)
	#print("Pre_membership:", premembership)
	all_nodes=0
	count=0
	cedges=[]
	pre_neighbors_list=[]
	Graph_nodes=[]
	for i in range(partition_num):
		init_par.append(prepartition[i])
	#print(init_par)

	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(del_size):
			node_count = graph.vcount()
			all_nodes= all_nodes+node_count
			pre_node_num = node_count+ del_size
			del_id= del_nodes[node]
			for p in range(len(init_par)):
				if (del_id in init_par[p]):
						init_par[p].remove(del_id)
			p=0
			for i in range(len(init_par)):
				if len(init_par[i-p])==0:
					init_par.pop(i-p)
					p = p +1

			neighbors = pre_graph.neighbors(del_id)

			d = 0
			for i in range(len(neighbors)):
				for j in range(del_size):
					if neighbors[i-d]==del_nodes[j]:
						neighbors.pop(i-d)
						d=d+1

			#neighbors.remove(del_id)
			#print("The previous neighbors of deleted node ",del_id,":  ", neighbors)
			neighbors.sort()
			pre_neighbors_list.append(neighbors)
	neighbors_list=pre_neighbors_list
	for j in range(len(neighbors_list)):
		s = 0
		p = 0
		for d in range(len(del_nodes)):
			for i in range(len(neighbors_list[j])):
				if s <= i:
					if neighbors_list[j][i-p]==del_nodes[d]:
						#print("This node shold be deleted from the list of neighbors:", neighbors_list[j][i-p])
						neighbors_list[j].pop(i-p)
						#print("the neighbors ",j, "after deleting from the deleted nodes:", neighbors_list[j])
						p=p+1
						s = i - p + 1
					elif neighbors_list[j][i-p]<del_nodes[d]:
						neighbors_list[j][i-p] = pre_neighbors_list[j][i-p] - d
						s = i - p + 1
					elif d==len(del_nodes)-1:
						neighbors_list[j][i-p] = pre_neighbors_list[j][i-p] - (d+1)
						s = i - p + 1
					else:
						s=i-p
						break
	#print(neighbors_list)
	#print("neighbors of node ", del_id, " : ", list(neighbors))




	new_par=init_par
	#print("new partitions before shifting: ", new_par)
	for p in range(len(init_par)):
		s=0
		for d in range(len(del_nodes)):
			for i in range(len(init_par[p])):
				if i>=s:
					if new_par[p][i]<del_nodes[d]:
						new_par[p][i] = init_par[p][i]-d
						s = i+1
						#print(" The algorithm came here for ",new_par[p][i])
					elif d==len(del_nodes)-1:
						new_par[p][i] = init_par[p][i]-(d+1)
						s = i+1
					else:
						s=i
						break
		#print("new partitions before shifting1: ", new_par)
	#print(new_par)
	dev=0
	sep=[]
	for i in range(len(neighbors_list)):
		for v in neighbors_list[i]:
			edges=graph.incident(v)
			if len(edges)==0:
				dev=dev+1
				#print("This is", v ,"that should be moved to a new partition ")
				if v not in sep:
					new_par.append([v])
					sep.append(v)
					for p in range(len(new_par)-dev):
						if (v in new_par[p]):
							new_par[p].remove(v)
							
	g=0
	for p in range(len(new_par)):
		if len(new_par[p-g]) == 0:
			new_par.pop(p-g)
			g=g+1

	#print(new_par)
	#print("deleted nodes:", del_nodes)
	d=0
	for nodes in range(len(del_nodes)):
		premembership.pop(del_nodes[nodes]-d)
		d=d+1


	new_membership = premembership

	for p in range(len(new_par)):
		for i in range(len(new_par[p])):
			new_membership[new_par[p][i]]= p
	#print("new membership before changing the seperated nodes partitions: ", new_membership)
	#print("new partitions before changing the seperated nodes partitions: ", new_par)
	for j in range(len(neighbors_list)):
		for i in range(len(neighbors_list[j])):
			div_par = False
			div_flag=False
			new_com=False
			par_id=new_membership[neighbors_list[j][i]]
			for k in new_par[par_id]:
				if k!=neighbors_list[j][i]:
					if nx.has_path(G, source=k, target=neighbors_list[j][i]) == False:
						div_flag = True # the node deletion created a partition in this community
						break
			if  div_flag==True:
				d=0
				for k in new_par[par_id]:
					if k != neighbors_list[j][i]:
						if nx.has_path(G, source=k, target=neighbors_list[j][i]) == False:
							if div_par==False:
								if new_com==False:
									new_par.append([neighbors_list[j][i]])
									#print("The node ", neighbors_list[j][i], " should be moved to new par")
									new_par[par_id].remove(neighbors_list[j][i])
									new_membership[neighbors_list[j][i]]= len(new_par)-1
									#print("The node ",neighbors_list[j][i], "moved to new par")
									div_par=True
									d = d + 1
								else:
									new_par[len(new_par) - 1].append(neighbors_list[j][i])
									#print("The node ",neighbors_list[j][i], " should be moved to new par")
									new_par[par_id].remove(neighbors_list[j][i])
									new_membership[neighbors_list[j][i]] = len(new_par) - 1
									#print("The node ", neighbors_list[j][i], "moved to new par")
									div_par = True
									d = d + 1

						else:
							if div_par==True:
								#print("The node ", k, "with node",neighbors_list[j][i], "moved to new par")
								new_par[len(new_par)-1].append(k)
								new_par[par_id].remove(k)
								new_membership[k] = len(new_par)-1
								d=d+1
							else:
								#print("The node ", k, "with node", neighbors_list[j][i], "moved to new par")
								new_par.append([k])
								new_par[par_id].remove(k)
								new_membership[k] = len(new_par)-1
								new_com= True
								d = d + 1



	for i in range(node_count):
		Graph_nodes.append(count)
		count = count + 1

	#print("Graph_nodes: ",Graph_nodes)
	#print("new_membership after deleting: ",new_membership)
	#print("Partitions11:  ", new_par)
	partition_dict = dict(zip(Graph_nodes, new_membership))
	print(partition_dict)

	return new_par,new_membership



########################################################################################################################

########################################################################################################################
def monolaye_update_partition_add(new_nodes,graph,prepartition,premembership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""
	add_size=new_nodes
	#adj=np.array(graph.get_adjacency().data)
	#print("rearranged intralayer_graph:  ")
	#print(adj)
	print("")
	#intralayer_igraph.neighbors(34)
	init_par=[]
	Graph=[]
	P_strength = np.zeros((len(prepartition)))
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	#print("There are ",len(prepartition),"initial partitions.")
	#print("The initial partitions: ",prepartition)
	all_nodes=0
	Graph_nodes=[]
	partition_info = []
	sorted_par_inf = []

	for i in range(partition_num):
		init_par.append(prepartition[i])
	#print(init_par)
	print(new_nodes)
	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(1,add_size+1):
			shift=add_size
			n= graph.vcount()-node
			new_node=n
			print("the graph lenght:", graph.vcount())

			neighbors=graph.neighbors(new_node)

			print("neighbors of node ",new_node," : ", list(neighbors))
			cedges = set()
			node_count = graph.vcount()
			all_nodes= all_nodes+node_count

			for v in neighbors:
				cedges.update(graph.incident(v))

			cedges = list(cedges)
			#print(cedges)
			cgraph = graph.subgraph_edges(edges=cedges, delete_vertices=False)
			#convert igraph to networkx graph
			A = [edge.tuple for edge in cgraph.es]
			g = nx.Graph(A)
			Graph.append(g.nodes)
			for v in neighbors:
				if(v!=new_node):

					#w1=cgraph.es.select(_source=new_node, _target=v)
					w1=1
					#print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1)
					v=v-shift
					for p in range(partition_num):
						if (v in init_par[p]):
							P_strength[p] = P_strength[p] + w1

			for i in range(partition_num):
				partition_info.append({'id': i, 'strength': P_strength[i]})

			for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
				sorted_par_inf.append(sorted_inf)
			count=0
			sorted_par_inf.append(sorted_par_inf)
			print(sorted_par_inf)

	for i in range(node_count):
		Graph_nodes.append(count)
		count=count+1
	#print("Graph Nodes:  ",Graph_nodes)
	#for i in range(len(Graph)):
		#for j in range(len(Graph[i])):
			#multilayer_nodes.append(Graph[i][j])

	#print("Pre_membership:",premembership)
	membership = premembership
	new_membership=[]

	# print("Layers:")
	# print(layers.__getitem__(i))
	for item in range(len(sorted_par_inf)):

				#init_modularity = partition.recalculate_modularity()
				#print("modularity:  ", init_modularity)
				#print(partition)
				#init_membership_0 = partition.membership
				#init_membership_0.append(partition_num)
			for i in range(node_count):
				if i >= (node_count-add_size):
					new_membership.append(sorted_par_inf[item][p]['id'])
					#prepartition[sorted_par_inf[p]['id']].append((i+add_size))
				else:
					new_membership.append(membership[i])
					#prepartition[sorted_par_inf[p]['id']].append()


			print("Graph_nodes: ",Graph_nodes)
			print("new_membership: ",new_membership)
			print(prepartition)
			partition_dict = dict(zip(Graph_nodes, new_membership))
			print(partition_dict)
			#new_modularity_0 = community_louvain.modularity(partition_dict_0, G)
			#new_modularity = community_louvain.modularity(partition_dict, Graph)
			#print("new_modularity if we consider new node in a seperate partition:  ", new_modularity_0)
			#print("new_modularity:  ", new_modularity)
			break
	new_par = prepartition
	for i in range(len(new_membership)):
		Par[new_membership[i]].append(Graph_nodes[i])
	#for i in range(len(new_membership)):
		#Par[new_membership[i]].append(Graph_nodes[i])
	print("partitions:  ", Par)
	return Par,new_membership


########################################################################################################################

########################################################################################################################
def monolaye_update_partition_add1(new_nodes, graph, prepartition, premembership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""
	add_size = new_nodes
	# adj=np.array(graph.get_adjacency().data)
	# print("rearranged intralayer_graph:  ")
	# print(adj)
	print("")
	# intralayer_igraph.neighbors(34)
	init_par = []
	Graph = []
	#P_strength = np.zeros((len(prepartition)))
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	# print("There are ",len(prepartition),"initial partitions.")
	# print("The initial partitions: ",prepartition)
	all_nodes = 0
	Graph_nodes = []

	sorted_par_inf = []

	for i in range(partition_num):
		init_par.append(prepartition[i])
	# print(init_par)
	print(new_nodes)
	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(add_size):
		P_strength = np.zeros((len(prepartition)))
		sorted_par = []
		partition_info = []
		#shift = add_size
		shift=0
		n = graph.vcount() - add_size + node
		new_node = n
		print("the graph lenght:", graph.vcount())

		neighbors = graph.neighbors(new_node)

		print("neighbors of node ", new_node, " : ", list(neighbors))
		cedges = set()
		node_count = graph.vcount()
		all_nodes = all_nodes + node_count

		for v in neighbors:
			cedges.update(graph.incident(v))

		cedges = list(cedges)
		# print(cedges)
		cgraph = graph.subgraph_edges(edges=cedges, delete_vertices=False)
		# convert igraph to networkx graph
		A = [edge.tuple for edge in cgraph.es]
		g = nx.Graph(A)
		Graph.append(g.nodes)
		for v in neighbors:
			if (v != new_node):

				# w1=cgraph.es.select(_source=new_node, _target=v)
				w1 = 1
				# print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1)
				v = v - shift
				for p in range(partition_num):
					if (v in init_par[p]):
						P_strength[p] = P_strength[p] + w1

		for i in range(partition_num):
			partition_info.append({'id': i, 'strength': P_strength[i]})

		for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
			sorted_par.append(sorted_inf)
		count = 0
		sorted_par_inf.append(sorted_par)
		print(sorted_par)

	for i in range(node_count):
		Graph_nodes.append(count)
		count = count + 1
	# print("Graph Nodes:  ",Graph_nodes)
	# for i in range(len(Graph)):
	# for j in range(len(Graph[i])):
	# multilayer_nodes.append(Graph[i][j])

	# print("Pre_membership:",premembership)
	#membership = premembership
	new_membership = premembership
	#print("This is pre membership before adding items: ", premembership)
	# print("Layers:")
	# print(layers.__getitem__(i))
	for item in range(len(sorted_par_inf)):
		for p in range(len(sorted_par_inf[item])):
			# init_modularity = partition.recalculate_modularity()
			# print("modularity:  ", init_modularity)
			# print(partition)
			# init_membership_0 = partition.membership
			# init_membership_0.append(partition_num)

			#print("This is the new membership:  ", sorted_par_inf[item][p]['id'])
			new_membership.append(sorted_par_inf[item][p]['id'])
				# prepartition[sorted_par_inf[p]['id']].append((i+add_size))
			break
			# prepartition[sorted_par_inf[p]['id']].append()

	print("Graph_nodes: ", Graph_nodes)
	print("new_membership: ", new_membership)
	print(prepartition)
	partition_dict = dict(zip(Graph_nodes, new_membership))
	print(partition_dict)
			# new_modularity_0 = community_louvain.modularity(partition_dict_0, G)
			# new_modularity = community_louvain.modularity(partition_dict, Graph)
			# print("new_modularity if we consider new node in a seperate partition:  ", new_modularity_0)
			# print("new_modularity:  ", new_modularity)

	new_par = prepartition
	for i in range(len(new_membership)):
		Par[new_membership[i]].append(Graph_nodes[i])
	# for i in range(len(new_membership)):
	# Par[new_membership[i]].append(Graph_nodes[i])
	print("partitions:  ", Par)
	return Par, new_membership

########################################################################################################################

########################################################################################################################
def monolaye_update_partition_add2(new_nodes, graph, prepartition, premembership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""
	add_size = new_nodes
	# adj=np.array(graph.get_adjacency().data)
	# print("rearranged intralayer_graph:  ")
	# print(adj)
	print("")
	# intralayer_igraph.neighbors(34)
	init_par = []
	Graph = []
	#P_strength = np.zeros((len(prepartition)))
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	# print("There are ",len(prepartition),"initial partitions.")
	# print("The initial partitions: ",prepartition)
	all_nodes = 0
	Graph_nodes = []

	sorted_par_inf = []

	for i in range(partition_num):
		init_par.append(prepartition[i])
	# print(init_par)
	#print(new_nodes)
	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(add_size):
		P_strength = np.zeros((len(prepartition)))
		sorted_par = []
		partition_info = []
		n = graph.vcount() - add_size + node
		new_node = n
		#print("the graph lenght:", graph.vcount())

		neighbors = graph.neighbors(new_node)

		#print("neighbors of node ", new_node, " : ", list(neighbors))
		cedges = set()
		node_count = graph.vcount()
		all_nodes = all_nodes + node_count

		#for v in neighbors:
			#cedges.update(graph.incident(v))

		#cedges = list(cedges)
		# print(cedges)
		#cgraph = graph.subgraph_edges(edges=cedges, delete_vertices=False)
		# convert igraph to networkx graph
		#A = [edge.tuple for edge in cgraph.es]
		#g = nx.Graph(A)
		#Graph.append(g.nodes)
		for v in neighbors:
			if (v != new_node):

				# w1=cgraph.es.select(_source=new_node, _target=v)
				w1=graph.es.select(_source=new_node, _target=v)['weight']
				# print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1)
				for p in range(partition_num):
					if (v in init_par[p]):
						P_strength[p] = P_strength[p] + w1

		for i in range(partition_num):
			partition_info.append({'id': i, 'strength': P_strength[i]})

		for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
			sorted_par.append(sorted_inf)
		count = 0
		sorted_par_inf.append(sorted_par)
		#print(sorted_par)

	for i in range(node_count):
		Graph_nodes.append(count)
		count = count + 1

	new_membership = premembership
	#print("This is pre membership before adding items: ", premembership)
	# print("Layers:")
	# print(layers.__getitem__(i))
	for item in range(len(sorted_par_inf)):
		for p in range(len(sorted_par_inf[item])):
			#print("This is the new membership:  ", sorted_par_inf[item][p]['id'])
			new_membership.append(sorted_par_inf[item][p]['id'])
			break


	for i in range(len(new_membership)):
		Par[new_membership[i]].append(Graph_nodes[i])
	#Par.sort(key=len,reverse=True)
	#for p in range(len(Par)):
	#	for i in range(len(Par[p])):
	sorted_par_inf = []
	for node in range(add_size):
		new_node = graph.vcount() - add_size + node
		neighbors = graph.neighbors(new_node)


		for v in neighbors:
			P_strength = np.zeros((len(Par)))
			sorted_par = []
			partition_info = []

			neighbors1 = graph.neighbors(v) #getting the neighbors of the new nodes neighbors
			#print("The neighbors of node ",v,": ",neighbors1)
			for N in neighbors1:
				if (N != v):
					w1=graph.es.select(_source=new_node, _target=v)['weight']
					# print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1)
					for p in range(partition_num):
						if (N in init_par[p]):
							P_strength[p] = P_strength[p] + w1

			for i in range(partition_num):
						partition_info.append({'pid': i, 'nid':v ,'strength': P_strength[i]})

			for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
						sorted_par.append(sorted_inf)

			sorted_par_inf.append(sorted_par)

			#print("This the neighbors that their partitions should be checked:",sorted_par)
	new_membership1=[]
	for i in range(len(new_membership)):
		new_membership1.append(new_membership[i])
	changed_flag = np.zeros((len(new_membership)))
	#print("new_membership: ", new_membership)
	for item in range(len(sorted_par_inf)):
		for p in range(len(sorted_par_inf[item])):
			#print("This is the new membership:  ", sorted_par_inf[item][p]['pid'])
			if new_membership1[sorted_par_inf[item][p]['nid']]!= sorted_par_inf[item][p]['pid']:
				if sorted_par_inf[item][p]['strength']!=0:
					changed_flag[sorted_par_inf[item][p]['nid']]=1
					new_membership1[sorted_par_inf[item][p]['nid']]=sorted_par_inf[item][p]['pid']
			break
	d=0
	for i in range(len(new_membership)):
		if changed_flag[i]==1:
			#print("the node", i, "should be moved to a partition:", new_membership1[i]-d)
			Par[new_membership1[i]-d].append(Graph_nodes[i])
			Par[new_membership[i]-d].remove(Graph_nodes[i])
			if len(Par[new_membership[i]-d])==0:
				Par.pop(new_membership[i]-d)
				d=d+1
	#print("new_membership: ", new_membership)
	#print("Graph_nodes: ", Graph_nodes)
	#print("new_membership1: ", new_membership1)
	#print(prepartition)
	partition_dict = dict(zip(Graph_nodes, new_membership1))
	print(partition_dict)
	#print("partitions:  ", Par)
	return Par, new_membership1

########################################################################################################################

########################################################################################################################
def monolaye_update_partition_add3(new_nodes, graph, prepartition, premembership):
	"""
	For falling back on the normal louvain method.  We use the single layer intralayer_igraph to\
	 create igraph representations for each of the layers.
	:param intralayer_igraph: igraph.Graph super_adjacency representation
	:param layer_vec: indicator of which layer each node is in.
	:return:
	"""
	add_size = new_nodes
	# adj=np.array(graph.get_adjacency().data)
	# print("rearranged intralayer_graph:  ")
	# print(adj)
	print("")
	# intralayer_igraph.neighbors(34)
	init_par = []
	Graph = []
	#P_strength = np.zeros((len(prepartition)))
	Par = []
	for i in range(len(prepartition)):
		Par.append([])
	partition_num = len(prepartition)
	# print("There are ",len(prepartition),"initial partitions.")
	# print("The initial partitions: ",prepartition)
	all_nodes = 0
	Graph_nodes = []

	sorted_par_inf = []

	for i in range(partition_num):
		init_par.append(prepartition[i])
	# print(init_par)
	#print(new_nodes)
	# We calculate the induced subgraph for each layer by identifying all of the edges
	# in that layer and creating a new igraph object for each (without deleting vertices)
	for node in range(add_size):
		P_strength = np.zeros((len(prepartition)))
		sorted_par = []
		partition_info = []
		n = graph.vcount() - add_size + node
		new_node = n
		#print("the graph lenght:", graph.vcount())

		neighbors = graph.neighbors(new_node)

		#print("neighbors of node ", new_node, " : ", list(neighbors))
		cedges = set()
		node_count = graph.vcount()
		all_nodes = all_nodes + node_count

		#for v in neighbors:
			#cedges.update(graph.incident(v))

		#cedges = list(cedges)
		# print(cedges)
		#cgraph = graph.subgraph_edges(edges=cedges, delete_vertices=False)
		# convert igraph to networkx graph
		#A = [edge.tuple for edge in cgraph.es]
		#g = nx.Graph(A)
		#Graph.append(g.nodes)
		for v in neighbors:
				# w1=cgraph.es.select(_source=new_node, _target=v)
				w1=graph.es.select(_source=new_node, _target=v)['weight']
				# print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1)
				for p in range(partition_num):
					if (v in init_par[p]):
						P_strength[p] = P_strength[p] + w1

		for i in range(partition_num):
			partition_info.append({'id': i, 'strength': P_strength[i]})

		for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
			sorted_par.append(sorted_inf)
		count = 0
		sorted_par_inf.append(sorted_par)
		#print(sorted_par)

	for i in range(node_count):
		Graph_nodes.append(count)
		count = count + 1

	new_membership = premembership
	#print("This is pre membership before adding items: ", premembership)
	# print("Layers:")
	# print(layers.__getitem__(i))
	for item in range(len(sorted_par_inf)):
		for p in range(len(sorted_par_inf[item])):
			#print("This is the new membership:  ", sorted_par_inf[item][p]['id'])
			new_membership.append(sorted_par_inf[item][p]['id'])
			break


	for i in range(len(new_membership)):
		Par[new_membership[i]].append(Graph_nodes[i])
	#Par.sort(key=len,reverse=True)
	#for p in range(len(Par)):
	#	for i in range(len(Par[p])):
	sorted_par_inf = []
	for node in range(add_size):
		new_node = graph.vcount() - add_size + node
		neighbors = graph.neighbors(new_node)


		for v in neighbors:
			P_strength = np.zeros((len(Par)))
			sorted_par = []
			partition_info = []

			neighbors1 = graph.neighbors(v) #getting the neighbors of the new nodes neighbors
			#print("The neighbors of node ",v,": ",neighbors1)
			for N in neighbors1:
				if (N != v):
					w1=graph.es.select(_source=new_node, _target=v)['weight']
					# print("The neighbors weights, the weights from node ",new_node,"to node",v,":  ",w1)
					for p in range(partition_num):
						if (N in init_par[p]):
							P_strength[p] = P_strength[p] + w1

			for i in range(partition_num):
						partition_info.append({'pid': i, 'nid':v ,'strength': P_strength[i]})

			for sorted_inf in sorted(partition_info, key=operator.itemgetter("strength"), reverse=True):
						sorted_par.append(sorted_inf)

			sorted_par_inf.append(sorted_par)

			#print("This the neighbors that their partitions should be checked:",sorted_par)
	new_membership1=[]
	for i in range(len(new_membership)):
		new_membership1.append(new_membership[i])
	changed_flag = np.zeros((len(new_membership)))
	#print("new_membership: ", new_membership)
	for item in range(len(sorted_par_inf)):
		for p in range(len(sorted_par_inf[item])):
			#print("This is the new membership:  ", sorted_par_inf[item][p]['pid'])
			if new_membership1[sorted_par_inf[item][p]['nid']]!= sorted_par_inf[item][p]['pid']:
				if sorted_par_inf[item][p]['strength']!=0:
					changed_flag[sorted_par_inf[item][p]['nid']]=1
					new_membership1[sorted_par_inf[item][p]['nid']]=sorted_par_inf[item][p]['pid']
			break
	d=0
	for i in range(len(new_membership)):
		if changed_flag[i]==1:
			#print("the node", i, "should be moved to a partition:", new_membership1[i]-d)
			Par[new_membership1[i]-d].append(Graph_nodes[i])
			Par[new_membership[i]-d].remove(Graph_nodes[i])
			if len(Par[new_membership[i]-d])==0:
				Par.pop(new_membership[i]-d)
				d=d+1
	#print("new_membership: ", new_membership)
	#print("Graph_nodes: ", Graph_nodes)
	#print("new_membership1: ", new_membership1)
	#print(prepartition)
	partition_dict = dict(zip(Graph_nodes, new_membership1))
	print(partition_dict)
	#print("partitions:  ", Par)
	return Par, new_membership1