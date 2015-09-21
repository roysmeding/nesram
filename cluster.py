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

prev_clusters = 2048

n = 0

while len(mapping) > 2:
    preference = np.median(aff) - 0.1*n*np.std(aff)
    ap = sklearn.cluster.AffinityPropagation(affinity='precomputed', preference=preference)
    ap.fit(aff)
    labels  = ap.labels_
    indices = ap.cluster_centers_indices_

    clusters = len(indices)

    sys.stderr.write("clustered to %d\n" % clusters)

    if clusters == prev_clusters:
        n += 1
        sys.stderr.write("\tRetrying with %f standard deviations lower preference\n" % (0.1*n))
        prev_clusters = clusters
    else:
        if n > 0:
            sys.stderr.write("\tSituation normalized at %f stdevs\n" % (0.1*n))
            n = 0
    prev_clusters = clusters

    # add edges to centers
    for node,label in enumerate(labels):
        if mapping[node] != mapping[indices[label]]:
            i,j = mapping[indices[label]], mapping[node]
            edges.append((i,j,A[i,j]))

    mapping = [mapping[k] for k in indices]
    aff = aff[indices,:][:,indices]

if len(mapping) == 2:
    if ent[mapping[0]] > ent[mapping[1]]:
        j,i = mapping[0], mapping[1]
    else:
        i,j = mapping[0], mapping[1]

    edges.append((i,j,A[i,j]))

sys.stderr.write("Produced %d edges.\n" % len(edges))

# output
sys.stderr.write("Writing output...\n")

np.savetxt(sys.argv[2], np.array(edges), fmt=["%d", "%d", "%f"])

sys.stderr.write("done.\n")

