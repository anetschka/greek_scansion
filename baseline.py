#NOTE: This requires Linux! Check CLTK documentation for more information: docs.cltk.org
#Local files on Windows can be accessed from the mnt directory in the Linux environment.

import re
import sys
import codecs
from cltk.prosody.greek.scanner import Scansion

infile = codecs.open(sys.argv[1], "r", "utf-8")
outfile = codecs.open(sys.argv[2], "w", "utf-8")
lines = infile.readlines()

scanner = Scansion()
for line in lines:
	vals = re.split(r'\t+', line.rstrip('\r?\n?'))
	scansion = scanner.scan_text(vals[1])
	print("{}\t{}\t{}".format(vals[0], vals[1], scansion), file=outfile)

infile.close()