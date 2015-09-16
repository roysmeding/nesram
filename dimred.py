import csv
import sys
import numpy as np
import scipy.cluster.hierarchy
import sklearn.manifold
import matplotlib.pyplot as plt
import scipy.spatial.distance as dist

print "Loading matrix..."
A = np.genfromtxt(sys.argv[1], delimiter=',')
assert np.size(A,0) == np.size(A,1)

A = A + np.transpose(A) - np.diag(A)

print "Constructing MDS embedding..."
se = sklearn.manifold.MDS(dissimilarity='precomputed', n_jobs=-1)
red = se.fit_transform(A)
np.savetxt(sys.argv[2], red)
red_dist = dist.squareform(dist.pdist(red))
rmse = np.sqrt(((A-red_dist)**2).mean())

print "Done. stress = %f, RMS error = %f" % (se.stress_, rmse)
