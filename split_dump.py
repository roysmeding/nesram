import sys

if len(sys.argv) != 2:
    print "Usage: %s <file>" % sys.argv[0]
    sys.exit(-1)

ifilename = sys.argv[1]

ofiles = []

ifile = open(ifilename, 'r')
for i in range(2048):
    ofiles.append(open('dump/%04d' % (i), 'w'))

while True:
    block = ifile.read(2048)
    if len(block) < 2048:
        if len(block) > 0:
            print "Warning: found trailing incomplete block with length %d" % len(block)
        break
    for i,of in enumerate(ofiles):
        of.write(block[i])

print "Done."
