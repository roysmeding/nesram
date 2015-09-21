import sys
import os
import math

if len(sys.argv) != 3:
    print "Usage: %s <file> <frames per slice>" % sys.argv[0]
    sys.exit(-1)

ifilename = sys.argv[1]
frames_per_slice = int(sys.argv[2])

print "%d" % math.ceil((os.stat(ifilename).st_size // 2048) / float(frames_per_slice))
