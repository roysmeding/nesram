import sys
import math
import cairo
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scipy.sparse

sys.stderr.write("Loading data...\n")

edges  = np.loadtxt(sys.argv[1]+".cluster")
ent    = np.loadtxt(sys.argv[1]+".ent")

n_edges = np.size(edges,0)

print '{'
print '"nodes":['
for i in range(0,2048):
    print '{"name":"%04x","ent":%f}%s' % (i,ent[i],',' if i<2047 else '')
print '],'
print '"links":['
for e in range(n_edges):
    i,j,d = edges[e,:]
    print '{"source":%d,"target":%d,"dist":%f}%s' % (i,j,d,',' if e<n_edges-1 else '')
print ']'
print '}'
