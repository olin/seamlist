#!/usr/bin/env python
"""
Source: http://lists2.ssc.com/pipermail/linux-list/2006-February/026220.html

to-mbox.py:  Insert line feeds to create mbox format

Usage:   ./to-mbox.py  infile outfile
"""
import sys

if len(sys.argv) != 3:
    print(__doc__)
    sys.exit()

out = open(sys.argv[2],"w")

start = True
for line in open(sys.argv[1]):
    if line.find("From ") == 0:
        if start:
            start = False
        else:
            out.write("\n")
        line = line.replace(" at ", "@")
    elif line.find("Message-ID: ") == 0:
    	messageid_stripped = line[line.find('<')+1:line.rfind('>')]
    	messageid_stripped = messageid_stripped.replace('@','')
    	messageid_stripped = messageid_stripped.replace('.','')
    	line = line + "Content-Type: multipart/mixed;boundary=_000_" + messageid_stripped + "_\n"
    out.write(line)

out.close()
