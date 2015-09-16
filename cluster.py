import csv
import sys
import numpy as np
import scipy.cluster.hierarchy
import matplotlib.pyplot as plt

sys.stderr.write("Loading data from '%s'...\n" % sys.argv[1])
A = np.genfromtxt(sys.argv[1], delimiter=',')

assert np.size(A,0) == np.size(A,1), "Expected square distance matrix"
n_observations = np.size(A,0)

sys.stderr.write("Number of datasets: %d\n" % n_observations)

sys.stderr.write("Constructing reduced distance vector...\n")
# turn (triangular) distance matrix into the reduced form that scipy wants
reduced = []

for j in range(1,np.size(A,0)):
    for i in range(j+1,np.size(A,1)):
        reduced.append(A[i,j])

reduced = np.clip(reduced, 0., 1.)

sys.stderr.write("Clustering...\n")
# cluster that form to get a hierarchical binary tree of clusterings
Z = scipy.cluster.hierarchy.linkage(reduced)

# create a more useful binary tree structure for traversal
tree = {i:i for i in range(n_observations)}

for idx,(i,j,d,n) in enumerate(Z):
    lhs = tree.pop(int(i))
    rhs = tree.pop(int(j))

    tree[idx+n_observations] = ([lhs, rhs], d)

assert len(tree) == 2

tree = ([tree[tree.keys()[0]], tree[tree.keys()[1]]], 0.)

# simplify that binary tree to an N-ary tree where needed
# we merge nodes where one child is a leaf node,
# the other isn't but has a leaf node child too,
# and they are close distance-wise

sys.stderr.write("Before simplification: %d nodes, %d edges\n" % (len(Z)+n_observations, len(Z)*2))

sys.stderr.write("Simplifying...\n")

nodes = []
edges = []
idx = n_observations

def simplify(l, parent):
    global idx, nodes, edges
    c,d = l

    if isinstance(c[0], (int,long)) and isinstance(c[1], (int,long)):
        # two leaf nodes. add them to the parent
        edges.append((parent, c[0], d))
        edges.append((parent, c[1], d))

        
    elif not (isinstance(c[0], (int,long))  or  isinstance(c[1], (int,long))):
        # neither child is leaf node. preserve node for children and simplify children
        new_parent = idx
        idx += 1
        nodes.append(new_parent)
        edges.append((parent, new_parent, d))

        simplify(c[0], new_parent)
        simplify(c[1], new_parent)

    else:
        # one leaf node, one not. remove node, attach children to parent

        lc,ic = None,None
        if isinstance(c[0], (int,long)):
            lc,ic = c[1], c[0]
        else:
            lc,ic = c[0], c[1]

        simplify(lc, parent)
        edges.append((parent, ic, d))

root = idx
idx += 1
nodes.append(root)
simplify(tree, root)

sys.stderr.write("After simplification: %d nodes, %d edges\n" % (len(nodes)+n_observations, len(edges)))

# print it in DOT format
print 'digraph mem {'
print "\tnode [shape=none];"

for n in range(n_observations):
    print "\tn%04d [label=\"%04x\"];" % (n,n)

print "\tnode [shape=none, width=0.02, height=0.02, label=\"\"];"

for n in nodes:
    print "\tn%04d;" % n

for a,b,d in edges:
    print "n%04d -> n%04d [len=%f];" % (a,b,d+0.01)

print '}'

sys.stderr.write("Done.\n")
