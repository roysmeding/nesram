import sys
import numpy as np
import math
import cairo
import matplotlib.pyplot as plt

print "Loading files..."
A = np.genfromtxt(sys.argv[1]+'.vi', delimiter=',')
assert np.size(A,0) == np.size(A,1)

n_seqs = np.size(A,0)

ent = np.loadtxt(sys.argv[1]+'.ent')
assert np.size(ent) == n_seqs

dimred = np.loadtxt(sys.argv[1]+'.dimred')
assert np.size(dimred,0) == n_seqs

WIDTH=3840
HEIGHT=2160

print "Creating %dx%d image..." % (WIDTH, HEIGHT)
surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context (surface)

xmin, xmax = np.min(dimred[:,0]), np.max(dimred[:,0])
ymin, ymax = np.min(dimred[:,1]), np.max(dimred[:,1])
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

print "Drawing edges..."
ctx.set_line_width(0.001)
# n = n_seqs*(n_seqs-1)/2

# l = len(str(n))
# fmt = '%'+str(l)+'d / %'+str(l)+'d'
# back = '\b' * (2*l+3)
# 
# sys.stdout.write('\t' + (fmt % (0,n)))
# for j in range(1,n_seqs-1):
#     done = j*n_seqs - j*(j+1)/2
#     sys.stdout.write(back + (fmt % (done,n)))
#     sys.stdout.flush()
#     for i in range(j+1,n_seqs):
#         x1,y1 = dimred[i,:]
#         x2,y2 = dimred[j,:]
# 
#         #d = (100.**(1.-A[i,j]))/100.
#         d = 1.-A[i,j]
# 
#         r1,g1,b1,_    = cm(float(i)/n_seqs)
#         r2,g2,b2,_    = cm(float(j)/n_seqs)
#         r05, g05, b05 = (r1+r2)/2., (g1+g2)/2., (b1+b2)/2.
# 
#         w1 = ent[i]/(80./9.) + 0.1
#         w2 = ent[j]/(80./9.) + 0.1
# 
#         gr = cairo.LinearGradient(x1,y1,x2,y2)
#         gr.add_color_stop_rgba(0.0, r1, g1, b1, w1)
#         gr.add_color_stop_rgba(0.5, r05,g05,b05, d*(w1+w2)/2)
#         gr.add_color_stop_rgba(1.0, r2, g2, b2, w2)
# 
#         ctx.set_source(gr)
# 
#         ctx.move_to(x1,y1)
#         ctx.line_to(x2,y2)
#         ctx.stroke()

for i in range(0, n_seqs-1):
    j = i+1
    x1,y1 = dimred[i,:]
    x2,y2 = dimred[j,:]

    r1,g1,b1,_    = cm(float(i)/n_seqs)
    r2,g2,b2,_    = cm(float(j)/n_seqs)

    d = 1. - A[i,j]

    w1 = d*(ent[i]/(80./9.) + 0.1)
    w2 = d*(ent[j]/(80./9.) + 0.1)

    gr = cairo.LinearGradient(x1,y1,x2,y2)
    gr.add_color_stop_rgba(0.0, r1, g1, b1, w1)
    gr.add_color_stop_rgba(1.0, r2, g2, b2, w2)

    ctx.set_source(gr)

    ctx.move_to(x1,y1)
    ctx.line_to(x2,y2)
    ctx.stroke()

NODE_SIZE = 0.005

print "\nDrawing nodes..."

l = len(str(n_seqs))
fmt = '%'+str(l)+'d / %'+str(l)+'d'
back = '\b' * (2*l+3)

sys.stdout.write('\t' + (fmt % (0,n_seqs)))

for i in range(n_seqs):
    sys.stdout.write(back + (fmt % (i, n_seqs)))
    sys.stdout.flush()
    x,y = dimred[i,:]
    w = ent[i]/(80./9.) + 0.1
    ctx.arc(x,y,NODE_SIZE*(0.5+ent[i]*0.5/8.),0, 2 * math.pi)
    r,g,b,_ = cm(float(i)/n_seqs)
    ctx.set_source_rgba(r,g,b, w)
    ctx.fill()

print "\nSaving..."
surface.write_to_png(sys.argv[2])

print "Done."
