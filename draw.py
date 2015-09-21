import sys
import math
import cairo
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import scipy.sparse

sys.stderr.write("Loading data...\n")

A      = np.loadtxt(sys.argv[1]+".vi", delimiter=',')
ent    = np.loadtxt(sys.argv[1]+".ent")
dimred = np.loadtxt(sys.argv[1]+".dimred")

n_seqs = np.size(ent,0)

# drawing
WIDTH=3840
HEIGHT=2160

sys.stderr.write("Creating %dx%d image...\n" % (WIDTH, HEIGHT))
surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context (surface)

xmin, xmax = min(dimred[:,0]), max(dimred[:,0])
ymin, ymax = min(dimred[:,1]), max(dimred[:,1])
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

sys.stderr.write("Drawing nodes...\n")

cr.select_font_face("Inconsolata", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
cr.set_font_size(8)

for i in range(n_seqs):
    x,y = dimred[i,:]
    w = ent[i]/(80./9.) + 0.1
    ctx.arc(x,y,NODE_SIZE*(0.5+ent[i]*0.5/8.),0, 2 * math.pi)
    r,g,b,_ = cm(float(i)/n_seqs)
    ctx.set_source_rgba(r,g,b, w)
    ctx.fill()

sys.stderr.write("Saving...\n")
surface.write_to_png(sys.argv[2])

sys.stderr.write("Done.\n")

