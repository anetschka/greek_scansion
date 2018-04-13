#NOTE: This requires Linux! Check CLTK documentation for more information: docs.cltk.org
#Local files on Windows can be accessed from the mnt directory in the Linux environment.
#write to kyle to ask why no output is given

import sys
import codecs
from cltk.prosody.greek.scanner import Scansion

infile = codecs.open(sys.argv[1], "r", "utf-8")
lines = infile.readlines()

scanner = Scansion()
#example from docs: works fine
line = scanner.scan_text('νέος μὲν καὶ ἄπειρος, δικῶν ἔγωγε ἔτι. μὲν καὶ ἄπειρος.')
print(line)

#own data: empty result, output only for one verse
for line in lines:
	print(scanner.scan_text(line))

infile.close()