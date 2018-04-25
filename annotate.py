import re
import sys
#for finite-state transducer (fallback processing)
import hfst
import codecs
#classes for random data selection and preprocessing
from preprocessing import selector, preprocessor
from automata import ruleset, FSA13, FSA14, FSA15, FSA16

####MAIN PROGRAM####	
	
infile = codecs.open(sys.argv[1], "r", "utf-8")
outfile = codecs.open(sys.argv[2], "w", "utf-8")

lines = infile.readlines()

#get a verse selector: use this to select and process a random subset of verses
#sel = selector()
#selection = sel.select(lines, 1)
#print(selection, file = outfile)

#get a preprocessor
prep = preprocessor()

#make dedicated FSAs for processing lines with different syllable count
fsa13 = FSA13('fsa13')
fsa14 = FSA14('fsa14')
fsa15 = FSA15('fsa15')
fsa16 = FSA16('fsa16')

#only for tracking number of lines with obviously erroneous syllabification
syll_counter = 0
#only for tracking number of short lines
short_counter = 0

for line in lines:
#for line in selection:
	scansion = ''
	
	vals = re.split(r'\t+', line.rstrip('\r?\n?'))
	
	#preprocessing
	text = prep.normalise(vals[1])
	#signal very short verses
	if prep.get_verse_length(text) < 4:
		short_counter+=1
	#selection of functions for syllabification
	##syllabified = prep.simple_syllabify(text)
	##syllabified = prep.vowel_syllabify(text)
	##syllabified = prep.cltk_syllabify(text)
	syllabified = prep.papakitsos_syllabify(text)
	syllable_count = prep.count_syllables(syllabified)
	
	#scansion annotation
	if syllable_count == 12:
		scansion = '-- -- -- -- -- -X'
		
	elif syllable_count == 13:
		scansion = 'one daktylus must be found'
		#reset automaton when processing is finished
		if fsa13.state != 'waiting':
			fsa13.to_waiting()
		fsa13.set_text(syllabified)
		fsa13.start_analysis()
		if(fsa13.state == 'daktylus_found'):
			scansion = fsa13.scansion
		else:
			print('not found, fallback required')
			fsa13.not_found()
		
	elif syllable_count == 14:
		scansion = 'two daktyles must be found'
		if fsa14.state != 'waiting':
			fsa14.to_waiting()
		fsa14.set_text(syllabified)
		fsa14.start_analysis()
		if(fsa14.state == 'found_two_daktyles'):
			scansion = fsa14.scansion
		else:
			print('not found, fallback required')
			fsa14.not_found()
	
	elif syllable_count == 15:
		scansion = 'two spondees must be found'
		if fsa15.state != 'waiting':
			fsa15.to_waiting()
		fsa15.set_text(syllabified)
		fsa15.start_analysis()
		if(fsa15.state == 'found_two_spondees'):
			scansion = fsa15.scansion
		else:
			print('not found, fallback required')
			fsa15.not_found()
		
	elif syllable_count == 16:
		scansion = 'one spondeus must be found'
		if fsa16.state != 'waiting':
			fsa16.to_waiting()
		fsa16.set_text(syllabified)
		fsa16.start_analysis()
		if(fsa16.state == 'spondeus_found'):
			scansion = fsa16.scansion
		else:
			print('not found, fallback required')
			fsa16.not_found()
		
	elif syllable_count == 17:
		scansion = '-** -** -** -** -** -X'
	
	#else:
		#print("WARNING: Incorrect syllable count: " + vals[0])
		#syll_counter += 1
	
	#output
	print("{}\t{}\t{}\t{}".format(vals[0], vals[1], syllabified, scansion), file=outfile)

#log	
#print(syll_counter, " incorrectly syllabified verses")
#print(short_counter, " short verses")