import sys

addresses = ["" for i in range(2048)]

if len(sys.argv) != 3:
    sys.stderr.write("Usage: %s <input> <output>\n" % sys.argv[0])
    sys.exit(1)

with open(sys.argv[1],'r') as inf:
    for line in inf:
        try:
            if line[0] == '\r' or line[0] == '\n':
                continue

            if line[0].isspace():
                continue

            start_addr = int(line[0:4], 16)
        
            if start_addr > 2047:
                sys.stderr.write("Warning: address %04x > %04x encountered\n" % (start_addr, 2047))
                continue

            if line[4] == '-':
                assert line[10] == '-'
                end_addr = int(line[5:9], 16)
                for i in range(start_addr, end_addr+1):
                    if addresses[i] != "":
                        sys.stderr.write("Warning: duplicate entry for line %04x\n" % i)
                    addresses[i] = line[11:].strip()
            else:
                assert line[5] == '-'
                if addresses[start_addr] != "":
                    sys.stderr.write("Warning: duplicate entry for line %04x\n" % start_addr)
                addresses[start_addr] = line[6:].strip()
        except Exception as e:
            sys.stderr.write("Warning: %s\n" % e)

with open(sys.argv[2], 'w') as outf:
    first = True
    outf.write('[\n')
    for i,desc in enumerate(addresses):
        if desc == "":
            continue

        if first:
            first = False
        else:
            outf.write(',\n')

        if desc.find('(') > -1:
            desc = desc[:desc.find('(')].strip()

        outf.write('{"addr":%d,"text":"%s"}' % (i, desc))
    outf.write('\n]\n')
