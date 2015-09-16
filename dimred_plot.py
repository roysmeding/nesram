import sys
import numpy as np
import matplotlib.pyplot as plt

A = np.loadtxt(sys.argv[1]+'.dimred')
ent = np.loadtxt(sys.argv[1]+'.ent')

plt.figure()

cm = plt.cm.get_cmap('gist_rainbow')
#for i in range(1,np.size(A,0)):
#    c = cm(float(i)/np.size(A,0))
#    c = (c[0], c[1], c[2], 0.2)
#    plt.plot([A[i-1,0],A[i,0]], [A[i-1,1],A[i,1]], color=c)

for i in range(np.size(A,0)):
    w = ent[i]/10.
    plt.plot(A[i,0], A[i,1], '.', markersize=5.*w+10., color=cm(float(i)/np.size(A,0)), alpha=0.05+(w*0.95))

#for i in range(np.size(A,0)):
#    plt.text(A[i,0], A[i,1], "%04x" % i)

plt.autoscale()
if len(sys.argv) > 2:
    plt.savefig(sys.argv[2])
plt.show()
