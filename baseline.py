#NOTE: This requires Linux! Check CLTK documentation for more information: docs.cltk.org
#Local files on Windows can be accessed from the mnt directory in the Linux environment.
#write to kyle to ask why no output is given

from cltk.prosody.greek.scanner import Scansion

scanner = Scansion()
line = scanner.scan_text('νέος μὲν καὶ ἄπειρος, δικῶν ἔγωγε ἔτι. μὲν καὶ ἄπειρος.')
print(line)