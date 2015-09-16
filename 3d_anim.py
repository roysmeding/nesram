import sys
import math
import numpy as np
import scipy.cluster.hierarchy
import sklearn.manifold
import sklearn.cluster
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.spatial.distance as dist

from mpl_toolkits.mplot3d import Axes3D

sys.stderr.write("Loading data from '%s'...\n" % sys.argv[1])
A = np.genfromtxt(sys.argv[1]+'.vi', delimiter=',')

assert np.size(A,0) == np.size(A,1), "Expected square distance matrix"
n_seqs = np.size(A,0)

ent = np.loadtxt(sys.argv[1]+'.ent')
assert np.size(ent) == n_seqs


sys.stderr.write("Number of datasets: %d\n" % n_seqs)

# reduce
THRESHOLD = 0.1
mask = ent>THRESHOLD
ent = ent[mask]
A = A[mask,:][:,mask]

n_seqs = np.size(A,0)
sys.stderr.write("After reduction: %d\n" % n_seqs)

A = A + np.transpose(A) - np.diag(A)

sys.stderr.write("Constructing MDS embedding...\n")
se = sklearn.manifold.MDS(n_components=3, dissimilarity='precomputed', n_jobs=-1)
dimred = se.fit_transform(A)

sys.stderr.write("Done. stress = %f\n" % (se.stress_))

# cluster
sys.stderr.write("Clustering...\n")
aff = -A - np.transpose(A) + np.diag(A) # construct affinity matrix

ap = sklearn.cluster.AffinityPropagation(affinity='precomputed')
labels = ap.fit_predict(aff)

# plot
sys.stderr.write("Plotting...\n")

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

cm = plt.cm.get_cmap('gist_rainbow')    # colormap for for nodes/edges based on index

# edges
# for j in range(1,n_seqs-1):
#     for i in range(j+1,n_seqs):
#         if labels[i] != labels[j]:
#             continue
# 
#         x1,y1,z1 = dimred[i,:]
#         x2,y2,z2 = dimred[j,:]
# 
#         if math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) > 0.2:
#             continue
# 
#         r1,g1,b1,_    = cm(float(i)/n_seqs)
#         r2,g2,b2,_    = cm(float(j)/n_seqs)
# 
#         w1 = ent[i]/(80./9.) + 0.1
#         w2 = ent[j]/(80./9.) + 0.1
# 
#         color = ((r1+r2)/2, (g1+g2)/2, (b1+b2)/2, (w1+w2)/2)
# 
#         ax.plot([x1,x2], [y1,y2], [z1,z2], c=color)

# nodes
for i in range(n_seqs):
    x,y,z = dimred[i,:]
    r,g,b,_ = cm(float(i)/n_seqs)
    w = ent[i]/(80./9.) + 0.1

    ax.scatter(x,y,z, 'o', c=(r,g,b,w))

sys.stderr.write("Saving...\n")
for ii in xrange(0,360,1):
    print "\t%03d" % ii
    ax.view_init(elev=10., azim=ii)
    plt.savefig("anim/movie%03d"%ii+".png")
