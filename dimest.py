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

print "dim\tstress\trmse"

for n in range(1900,2200,25):
    se = sklearn.manifold.MDS(n_components=n, dissimilarity='precomputed', n_jobs=-1)
    red = se.fit_transform(A)
    red_dist = dist.squareform(dist.pdist(red))
    rms_err = np.sqrt(((A-red_dist)**2).mean())
    print "%2d\t%f\t%f" % (n, se.stress_, rms_err)

print "Done."
