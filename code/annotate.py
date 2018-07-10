import re
import sys
import codecs
#classes for random data selection and preprocessing
from preprocessing import selector, preprocessor
#linguistic rules and hierarchical FSAs for verse processing
from hAutomata import HFSA13, HFSA14, HFSA15, HFSA16
from hAutomata import annotator

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

hfsa13 = HFSA13('hfsa13')
hfsa14 = HFSA14('hfsa14')
hfsa15 = HFSA15('hfsa15')
hfsa16 = HFSA16('hfsa16')
annotator = annotator('annotator')

#only for tracking number of lines with obviously erroneous syllabification
syll_counter = 0
#track number of sentences with scansion annotation
scansion_counter = 0

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

	if syllable_count < 12 or syllable_count > 17:
		print("WARNING: Incorrect syllable count: " + vals[0])
		syll_counter += 1
		#TODO: if there are more than four words, proceed to detailed analysis

	#scansion annotation
	elif syllable_count == 12:
		scansion = '-- -- -- -- -- -X'
		#check correctness using generic annotator instance
		#TODO: implement own dea for these cases
		annotator.set_text(text, syllables)
		if annotator._verify_string(scansion):
			scansion_counter += 1
		else:
			#correct
			result = annotator._correct_string()

	elif syllable_count == 17:
		scansion = '-** -** -** -** -** -X'
		annotator.set_text(text, syllables)
		if annotator._verify_string(scansion):
			scansion_counter += 1
		else:
			result = annotator._correct_string()
		
	elif syllable_count == 13:
		if hfsa13.state != 'waiting':
			hfsa13.to_waiting()
		hfsa13.set_text(text, syllables)
		hfsa13.start_analysis()
		if hfsa13.state == 'success':
			scansion = hfsa13.verse.scansion
			scansion_counter += 1
		elif hfsa13.state == 'no_spondeus_found':
			hfsa13.not_found()
			#TODO: rather try to check whether fst has accepted the input string
			if re.match(r'#', hfsa13.verse.scansion):
				scansion_counter += 1
				scansion = hfsa13.scansion
			else:
				scansion = 'NOT RESOLVED'
		else:
			scansion = 'NOT RESOLVED'
		
	elif syllable_count == 14:
		if hfsa14.state != 'waiting':
			hfsa14.to_waiting()
		hfsa14.set_text(text, syllables)
		hfsa14.start_analysis()
		if hfsa14.state == 'success':
			scansion = hfsa14.verse.scansion
			scansion_counter += 1
		elif hfsa14.state == 'no_spondeus_found':
			hfsa14.not_found()
			if re.search(r'#', hfsa14.verse.scansion):
				scansion_counter += 1
				scansion = hfsa14.verse.scansion		
			else:
				scansion = 'NOT RESOLVED'
		else:
			scansion = 'NOT RESOLVED'
				
	elif syllable_count == 15:
		if hfsa15.state != 'waiting':
			hfsa15.to_waiting()
		hfsa15.set_text(text, syllables)
		hfsa15.start_analysis()
		if(hfsa15.state == 'success'):
			scansion = hfsa15.verse.scansion
			scansion_counter += 1
		elif hfsa15.state == 'no_spondeus_found':
			hfsa15.not_found()		
			if re.search(r'#', hfsa15.verse.scansion):
				scansion_counter += 1
				scansion = hfsa15.verse.scansion
			else:
				scansion = 'NOT RESOLVED'
		else:
			scansion = 'NOT RESOLVED'
		
	elif syllable_count == 16:
		if hfsa16.state != 'waiting':
			hfsa16.to_waiting()
		hfsa16.set_text(text, syllables)
		hfsa16.start_analysis()
		if hfsa16.state == 'success':
			scansion = hfsa16.verse.scansion
			scansion_counter += 1
		elif hfsa16.state == 'no_spondeus_found':
			hfsa16.not_found()
			if re.search(r'#', hfsa16.verse.scansion):
				scansion_counter += 1
				scansion = hfsa16.verse.scansion
			else:
				scansion = 'NOT RESOLVED'
		else:
			scansion = 'NOT RESOLVED'
	
	#output
	print("{}\t{}\t{}\t{}".format(vals[0], vals[1], syllabified, scansion), file=outfile)
	
#log	
print(syll_counter, ' incorrectly syllabified verses')
print(scansion_counter, 'annotated verses')

outfile.close()
