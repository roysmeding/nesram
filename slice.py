import sys
import os

if len(sys.argv) != 3:
    print "Usage: %s <file> <frames per slice>" % sys.argv[0]
    sys.exit(-1)

ifilename = sys.argv[1]

ifile = open(ifilename, 'r')

frames_per_slice = int(sys.argv[2])

cur_slice = 0

while True:
    print "Slice %d" % cur_slice
    ofiles = []

    directory = 'dump/%04d' % cur_slice
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i in range(2048):
        ofiles.append(open('%s/%04d' % (directory,i), 'w'))

    for idx in range(frames_per_slice):
        # one frame
        block = ifile.read(2048)
        if len(block) < 2048:
            if len(block) > 0:
                print "Warning: found trailing incomplete block with length %d" % len(block)
            break

        for i,of in enumerate(ofiles):
            of.write(block[i])

    if len(block) < 2048:
        break

    for f in ofiles:
        f.close()

    cur_slice += 1

print "Done."
