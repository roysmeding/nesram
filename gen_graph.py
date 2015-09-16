import csv
import sys
import numpy as np
import scipy.cluster.hierarchy

A = np.genfromtxt(sys.argv[1], delimiter=',')

assert np.size(A,0) == np.size(A,1)
n_observations = np.size(A,0)

print 'graph mem {'
print "\tnode [shape=circle, width=0.05, height=0.05];"

for n in range(n_observations):
    print "\tn%04d [label=\"%04x\"];" % (n,n)

print "\tedge [style=invis];"

sys.stderr.write("0000")
for i in range(n_observations):
    sys.stderr.write("\b\b\b\b%04d" % i)
    for j in range(i-1):
        d = A[i,j]
        if np.isnan(d):
            sys.stderr.write("\nWarning: NaN found at (%4d,%4d)\n%04d" % (i,j,i))
            continue
        w = 0.1+5.*np.clip(d,0.,1.)
        if d < 0.1:
            print "\tn%04d -- n%04d [len=%f,style=\"\"];" % (i,j,w)
        else:
            print "\tn%04d -- n%04d [len=%f];" % (i,j,w)
print '}'
sys.stderr.write("\nDone.\n")
