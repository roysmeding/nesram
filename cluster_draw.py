import sys
import math
import cairo
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scipy.sparse

sys.stderr.write("Loading data...\n")

A      = np.loadtxt(sys.argv[1]+".vi", delimiter=',')
edges  = np.loadtxt(sys.argv[1]+".cluster")
ent    = np.loadtxt(sys.argv[1]+".ent")
dimred = np.loadtxt(sys.argv[1]+".dimred")

n_seqs = np.size(ent,0)

sys.stderr.write("Computing graph layout...\n")

G=nx.Graph()
for n in range(2048):
    G.add_node(n)

for e in range(np.size(edges,0)):
    i,j,d = edges[e,:]
    G.add_edge(i,j, weight=1.-d)

initial_pos = { i:dimred[i,:] for i in range(np.size(dimred,0)) }

layout = nx.spring_layout(G, pos=initial_pos)

sys.stderr.write("Computed.\n")

# drawing

WIDTH=3840
HEIGHT=2160

sys.stderr.write("Creating %dx%d image...\n" % (WIDTH, HEIGHT))
surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context (surface)

xmin, xmax = min((p[0] for p in layout.itervalues())), max((p[0] for p in layout.itervalues()))
ymin, ymax = min((p[1] for p in layout.itervalues())), max((p[1] for p in layout.itervalues()))
w,h = xmax-xmin, ymax-ymin

ctx.move_to(   0.,     0.)
ctx.line_to(   0., HEIGHT)
ctx.line_to(WIDTH, HEIGHT)
ctx.line_to(WIDTH,     0.)
ctx.line_to(   0.,     0.)
ctx.set_source_rgba(0.,0.,0.,1.)
ctx.fill()

scale = min(WIDTH/w, HEIGHT/h) * 0.95
ctx.scale(scale, scale)

tx,ty = (-xmin-xmax+WIDTH/scale)/2., (-ymin-ymax+HEIGHT/scale)/2.
ctx.translate(tx, ty)

cm = plt.cm.get_cmap('gist_rainbow')    # colormap for for nodes/edges based on index

sys.stderr.write("Drawing edges...\n")
ctx.set_line_width(0.001)

for e in range(np.size(edges,0)):
    i,j,d = edges[e,:]

    x1,y1 = layout[i]
    x2,y2 = layout[j]

    r1,g1,b1,_    = cm(float(i)/n_seqs)
    r2,g2,b2,_    = cm(float(j)/n_seqs)

    w1 = ent[i]/(80./9.) + 0.1
    w2 = ent[j]/(80./9.) + 0.1

    gr = cairo.LinearGradient(x1,y1,x2,y2)
    gr.add_color_stop_rgba(0.0, r1, g1, b1, d*w1)
    gr.add_color_stop_rgba(1.0, r2, g2, b2, d*w2)

    ctx.set_source(gr)

    ctx.move_to(x1,y1)
    ctx.line_to(x2,y2)
    ctx.stroke()

NODE_SIZE = 0.005

sys.stderr.write("Drawing nodes...\n")

for i in range(n_seqs):
    x,y = layout[i]
    w = ent[i]/(80./9.) + 0.1
    ctx.arc(x,y,NODE_SIZE*(0.5+ent[i]*0.5/8.),0, 2 * math.pi)
    r,g,b,_ = cm(float(i)/n_seqs)
    ctx.set_source_rgba(r,g,b, w)
    ctx.fill()

sys.stderr.write("Saving...\n")
surface.write_to_png(sys.argv[2])

sys.stderr.write("Done.\n")

