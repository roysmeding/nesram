import sys
import math
import cairo
import numpy as np
import sklearn.cluster
import sklearn.manifold
import matplotlib.pyplot as plt

sys.stderr.write("Loading data from '%s'...\n" % sys.argv[1])
A = np.genfromtxt(sys.argv[1]+'.vi', delimiter=',')

assert np.size(A,0) == np.size(A,1), "Expected square distance matrix"
n_seqs = np.size(A,0)

ent = np.loadtxt(sys.argv[1]+'.ent')
assert np.size(ent) == n_seqs

sys.stderr.write("Number of datasets: %d\n" % n_seqs)

# fix A
A = A + np.transpose(A) - np.diag(A)

# construct affinity matrix
aff = np.exp(-A)

sys.stderr.write("Clustering...\n")

# cluster
edges = []

mapping = list(range(2048))

while len(mapping) > 2:
    ap = sklearn.cluster.AffinityPropagation(affinity='precomputed')
    ap.fit(aff)
    labels  = ap.labels_
    indices = ap.cluster_centers_indices_

    for node,label in enumerate(labels):
        if mapping[node] != mapping[indices[label]]:
            edges.append((mapping[indices[label]], mapping[node]))

    mapping = [mapping[k] for k in indices]
    aff = aff[indices,:][:,indices]

    sys.stderr.write("clustered to %d\n" % len(indices))

print "digraph g {"
print "root [shape=none];"
for i in range(n_seqs):
    print "n%04d [shape=none, label=\"%03x\"];" % (i,i)

for i,j in edges:
    d = 10.**A[i,j] / 10.
    print "n%04d -> n%04d [len=\"%f\"];" % (i,j,d)

i,j = mapping[0], mapping[1]
print "root -> n%04d [len=\"%f\"];" % (i, A[i,j]/2.)
print "root -> n%04d [len=\"%f\"];" % (j, A[i,j]/2.)

print "}"
