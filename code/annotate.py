import re
import sys
import codecs
#classes for random data selection and preprocessing
from preprocessing import selector, preprocessor
#linguistic rules and hierarchical FSAs for verse processing
from hAutomata import HFSA13, HFSA14, HFSA15, HFSA16, SimpleFSA

####MAIN PROGRAM####	
	
infile = codecs.open(sys.argv[1], 'r', 'utf-8')
outfile = codecs.open(sys.argv[2], 'w', 'utf-8')

lines = infile.readlines()
infile.close()

#get a verse selector: use this to select and process a random subset of verses
#sel = selector()
#selection = sel.select(lines, 1)

#get a preprocessor
prep = preprocessor()

#hierarchical FSAs for syllable-wise spondeus search (à la Papakitsos 2011)
hfsa13 = HFSA13('hfsa13')
hfsa14 = HFSA14('hfsa14')
hfsa15 = HFSA15('hfsa15')
hfsa16 = HFSA16('hfsa16')
#simple FSA for vowel-wise analysis in case of errors
simple = SimpleFSA('simple')

for line in lines:
#for line in selection:
	scansion = ''
	
	vals = re.split(r'\t+', line.rstrip('\r?\n?'))

	#preprocessing
	text = prep.normalise(vals[1])

	#selection of functions for syllabification
	#syllabified = prep.simple_syllabify(text)
	##syllabified = prep.vowel_syllabify(text)
	##syllabified = prep.cltk_syllabify(text)
	syllabified = prep.papakitsos_syllabify(text)
	syllable_count = prep.count_syllables(syllabified)
	syllables = re.split(r'[ \.]', syllabified)

	#non-hexameter syllable count
	#we analyse nonetheless, provided that there are not too few syllables
	if syllable_count < 12 or syllable_count > 17:
		if syllable_count > 8:
			if simple.state != 'waiting':
				simple.to_waiting()
			simple.set_text(text, syllables)
			simple.start_analysis()
			scansion = simple.verse.correction
		else:
			print("WARNING: Incorrect syllable count: " + vals[0])

	elif syllable_count == 12:
		scansion = '-- -- -- -- -- -X'
		if simple.state != 'waiting':
			simple.to_waiting()
		simple.set_text(text, syllables)
		if not simple.verify(scansion):
			simple.start_analysis()
			scansion = simple.verse.correction

	elif syllable_count == 17:
		scansion = '-** -** -** -** -** -X'
		if simple.state != 'waiting':
			simple.to_waiting()
		simple.set_text(text, syllables)
		if not simple.verify(scansion):
			simple.start_analysis()
			scansion = simple.verse.correction
		
	elif syllable_count == 13:
		if hfsa13.state != 'waiting':
			hfsa13.to_waiting()
		hfsa13.set_text(text, syllables)
		hfsa13.start_analysis()
		if hfsa13.state == 'no_spondeus_found':
			hfsa13.not_found()
			scansion = hfsa13.verse.scansion + '###' + hfsa13.verse.correction
		else:
			scansion = hfsa13.verse.scansion
		
	elif syllable_count == 14:
		if hfsa14.state != 'waiting':
			hfsa14.to_waiting()
		hfsa14.set_text(text, syllables)
		hfsa14.start_analysis()
		if hfsa14.state == 'no_spondeus_found':
			hfsa14.not_found()
			scansion = hfsa14.verse.scansion + '###' + hfsa14.verse.correction
		else:
			scansion = hfsa14.verse.scansion
				
	elif syllable_count == 15:
		if hfsa15.state != 'waiting':
			hfsa15.to_waiting()
		hfsa15.set_text(text, syllables)
		hfsa15.start_analysis()
		if hfsa15.state == 'no_spondeus_found':
			hfsa15.not_found()		
			scansion = hfsa15.verse.scansion + '###' + hfsa15.verse.correction
		else:
			scansion = hfsa15.verse.scansion
		
	elif syllable_count == 16:
		if hfsa16.state != 'waiting':
			hfsa16.to_waiting()
		hfsa16.set_text(text, syllables)
		hfsa16.start_analysis()
		if hfsa16.state == 'no_spondeus_found':
			hfsa16.not_found()
			scansion = hfsa16.verse.scansion + '###' + hfsa16.verse.correction
		else:
			scansion = hfsa16.verse.scansion

	#output
	if len(scansion) == 0:
		scansion = 'NOT RESOLVED'
	print("{}\t{}\t{}\t{}".format(vals[0], vals[1], syllabified, scansion), file=outfile)

outfile.close()
