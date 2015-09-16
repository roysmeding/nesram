import sys
import math
import numpy as np
import scipy.cluster.hierarchy
import matplotlib.pyplot as plt
import cairo

print "Loading files..."
A = np.genfromtxt(sys.argv[1]+'.vi', delimiter=',')
assert np.size(A,0) == np.size(A,1)

n_seqs = np.size(A,0)

ent = np.loadtxt(sys.argv[1]+'.ent')
assert np.size(ent) == n_seqs

dimred = np.loadtxt(sys.argv[1]+'.dimred')
assert np.size(dimred,0) == n_seqs

################################################################################
# GRAPH CLUSTERING
################################################################################

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
tree = {i:i for i in range(n_seqs)}

for idx,(i,j,d,n) in enumerate(Z):
    lhs = tree.pop(int(i))
    rhs = tree.pop(int(j))

    tree[idx+n_seqs] = ([lhs, rhs], d)

assert len(tree) == 2

tree = ([tree[tree.keys()[0]], tree[tree.keys()[1]]], 0.)

# simplify that binary tree to an N-ary tree where needed
# we merge nodes where one child is a leaf node,
# the other isn't but has a leaf node child too,
# and they are close distance-wise

sys.stderr.write("Before simplification: %d nodes, %d edges\n" % (len(Z)+n_seqs, len(Z)*2))

sys.stderr.write("Simplifying...\n")

nodes = {}
edges = []
idx = n_seqs

for i in range(n_seqs):
    nodes[i] = (dimred[i,0], dimred[i,1])

def simplify(l, parent):
    global idx, nodes, edges
    c,d = l

    if isinstance(c[0], (int,long)) and isinstance(c[1], (int,long)):
        # two leaf nodes. add them to the parent
        new_parent = idx
        idx += 1
        edges.append((parent, new_parent, d))

        edges.append((new_parent, c[0], d))
        edges.append((new_parent, c[1], d))

        x1, y1 = nodes[c[0]]
        x2, y2 = nodes[c[1]]

        nodes[new_parent] = ((x1+x2)/2, (y1+y2)/2)
        return nodes[new_parent]
        
    elif not (isinstance(c[0], (int,long))  or  isinstance(c[1], (int,long))):
        # neither child is leaf node. preserve node for children and simplify children
        new_parent = idx
        idx += 1
        edges.append((parent, new_parent, d))

        x1, y1 = simplify(c[0], new_parent)
        x2, y2 = simplify(c[1], new_parent)
        nodes[new_parent] = ((x1+x2)/2, (y1+y2)/2)
        return nodes[new_parent]

    else:
        # one leaf node, one not. remove node, attach children to parent
        lc,ic = None,None
        if isinstance(c[0], (int,long)):
            lc,ic = c[1], c[0]
        else:
            lc,ic = c[0], c[1]

        new_parent = idx
        idx += 1
        edges.append((parent, new_parent, d))

        x1, y1 = simplify(lc, new_parent)
        x2, y2 = nodes[ic]
        edges.append((new_parent, ic, d))
        nodes[new_parent] = ((x1+x2)/2, (y1+y2)/2)
        return nodes[new_parent]

root = idx
idx += 1
nodes[root] = simplify(tree, root)

sys.stderr.write("After simplification: %d nodes, %d edges\n" % (len(nodes), len(edges)))

################################################################################
# DRAWING
################################################################################

WIDTH=3840
HEIGHT=2160

print "Creating %dx%d image..." % (WIDTH, HEIGHT)
surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context (surface)

xmin, xmax = np.min(dimred[:,0]), np.max(dimred[:,0])
ymin, ymax = np.min(dimred[:,1]), np.max(dimred[:,1])
w,h = xmax-xmin, ymax-ymin

scale = min(WIDTH/w, HEIGHT/h)
ctx.scale(scale, scale)

tx,ty = -(xmin-WIDTH/scale/2+w/2), -(ymin-HEIGHT/scale/2+h/2)
ctx.translate(tx,ty)

cm = plt.cm.get_cmap('gist_rainbow')    # colormap for for nodes/edges based on index

print "Drawing edges..."
ctx.set_line_width(0.001)

for i,j,d in edges:
    x1,y1 = nodes[i]
    x2,y2 = nodes[j]

    ctx.set_source_rgba(1.,1.,1., 0.5)
    ctx.move_to(x1,y1)
    ctx.line_to(x2,y2)
    ctx.stroke()


NODE_SIZE = 0.005

print "\nDrawing nodes..."
for i,(x,y) in nodes.iteritems():
    if i < 2048:
        w = ent[i]/(80./9.) + 0.1
        r,g,b,_ = cm(float(i)/n_seqs)
        s = NODE_SIZE*(0.5+ent[i]*0.5/8.)
    else:
        r,g,b,w = [1.,1.,1.,0.9]
        s = NODE_SIZE*0.5
    ctx.arc(x,y,s,0, 2 * math.pi)
    ctx.set_source_rgba(r,g,b, w)
    ctx.fill()

print "\nSaving..."
surface.write_to_png(sys.argv[2])

print "Done."
