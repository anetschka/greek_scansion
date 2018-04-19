import re
import sys
#for finite-state transducer (fallback processing)
import hfst
import codecs
#for random number generation
from random import randint
#the general algorithm is implemented as finite-state machine
from transitions import Machine
#for syllabification
from greek_accentuation.syllabify import syllabify, display_word

####CLASS DEFINITIONS####

#class for random selection of verses
class selector(object):
	
	def __init__(self):
		#this dictionary contains the total verse count for each work in the Homer corpus
		self.works = {0: 15875, 1: 12150, 2: 1066, 3: 840, 4: 487, 5: 1835, 6: 2344}
		#this dictionary contains the minimum sentenceid for each work in the Homer corpus
		self.min = {0: 1, 1: 15874, 2: 28026, 3: 29092, 4: 29932, 5: 30419, 6: 32254}
		#this dictionary contains the maximum sentenceid for each work in the Homer corpus
		self.max = {0: 15875, 1: 28025, 2: 29091, 3: 29931, 4: 30418, 5: 32253, 6: 34597}
		#dictionary to avoid duplicate selection
		self.selected = {}
	
	def select(self, lines, level):
		#return value
		resultlines = []
		
		#update number of verses to be selected
		for work in self.works:
			count = round((self.works[work]/100)*level, 0)
			self.works[work] = count

		#select correct number of sentences
		for work in self.works:
			while self.works[work] > 0:
				sentence = randint(self.min[work], self.max[work])
				#check if this has already been selected
				if sentence not in self.selected:
					line = lines[sentence]
					self.works[work] = self.works[work]-1
					resultlines.append(line)
					update = {sentence : 1}
					self.selected.update(update)
				
		return resultlines

#class for preprocessing
class preprocessor(object):

	#removes accents, lowercases
	def normalise(self, text):
		#some regexes have to be applied more than once since diacritics can be combined
		text = re.sub(r'ῆ', 'η', text)
		text = re.sub(r'ἣ', 'η', text)
		text = re.sub(r'ὴ', 'η', text)
		text = re.sub(r'ἡ', 'η', text)
		text = re.sub(r'ή', 'η', text)
		text = re.sub(r'ἠ', 'η', text)
		text = re.sub(r'ῆ', 'η', text)
		text = re.sub(r'ῃ', 'η', text)
		text = re.sub(r'ὴ', 'η', text)
		text = re.sub(r'ή', 'η', text)
		text = re.sub(r'ῃ', 'η', text)
	
		text = re.sub(r'Ἄ', 'Α', text)
		text = re.sub(r'Ἀ', 'Α', text)
	
		text = re.sub(r'ἄ', 'α', text)
		text = re.sub(r'ὰ', 'α', text)
		text = re.sub(r'ά', 'α', text)
		text = re.sub(r'ἀ', 'α', text)
		text = re.sub(r'ᾶ', 'α', text)
		text = re.sub(r'ἁ', 'α', text)
		text = re.sub(r'ὰ', 'α', text)
		text = re.sub(r'ᾳ', 'α', text)
		text = re.sub(r'ά', 'α', text)
	
		text = re.sub(r'ϊ', 'ι', text) 
		text = re.sub(r'ὶ', 'ι', text) 
		text = re.sub(r'ί', 'ι', text) 
		text = re.sub(r'ῖ', 'ι', text) 
		text = re.sub(r'ἰ', 'ι', text) 
		text = re.sub(r'ΐ', 'ι', text) 
		text = re.sub(r'ἱ', 'ι', text)
		text = re.sub(r'ί', 'ι', text)
		text = re.sub(r'ῖ', 'ι', text)
		text = re.sub(r'ὶ', 'ι', text)
	
		text = re.sub(r'Ἴ', 'Ι', text)
		text = re.sub(r'Ἰ', 'Ι', text)
	
		text = re.sub(r'ἕ', 'ε', text)
		text = re.sub(r'έ', 'ε', text)
		text = re.sub(r'ὲ', 'ε', text)
		text = re.sub(r'ἑ', 'ε', text)
		text = re.sub(r'ἔ', 'ε', text)
		text = re.sub(r'ἐ', 'ε', text)
	
		text = re.sub(r'Ἕ', 'Ε', text)
		text = re.sub(r'Ἐ', 'Ε', text)
		text = re.sub(r'Ἑ', 'Ε', text)
	
		text = re.sub(r'ῦ', 'υ', text)
		text = re.sub(r'ύ', 'υ', text)
		text = re.sub(r'ὐ', 'υ', text)
		text = re.sub(r'ὺ', 'υ', text)
		text = re.sub(r'ὗ', 'υ', text)
		text = re.sub(r'ὕ', 'υ', text)
		text = re.sub(r'ϋ', 'υ', text)
		text = re.sub(r'ὑ', 'υ', text)
		text = re.sub(r'ῦ', 'υ', text)
		text = re.sub(r'ύ', 'υ', text)
		text = re.sub(r'ὺ', 'υ', text)

		text = re.sub(r'ώ', 'ω', text)
		text = re.sub(r'ῶ', 'ω', text)
		text = re.sub(r'ῳ', 'ω', text)
		text = re.sub(r'ὼ', 'ω', text)
		text = re.sub(r'ὥ', 'ω', text)
		text = re.sub(r'ὣ', 'ω', text)
		text = re.sub(r'ὤ', 'ω', text)
		text = re.sub(r'ὠ', 'ω', text)
		text = re.sub(r'ῶ', 'ω', text)
		text = re.sub(r'ᾧ', 'ω', text)
		text = re.sub(r'ὡ', 'ω', text)
		text = re.sub(r'ῶ', 'ω', text)
		text = re.sub(r'ῳ', 'ω', text)
		text = re.sub(r'ὼ', 'ω', text)
	
		text = re.sub(r'Ἥ', 'Η', text)
		text = re.sub(r'Ἠ', 'Η', text)
	
		text = re.sub(r'ό', 'ο', text)
		text = re.sub(r'ὅ', 'ο', text)
		text = re.sub(r'ὁ', 'ο', text)
		text = re.sub(r'ὸ', 'ο', text)
		text = re.sub(r'ὄ', 'ο', text)
		text = re.sub(r'ὀ', 'ο', text)
	
		text = re.sub(r'Ὀ', 'Ο', text)
	
		text = re.sub(r'Ὠ', 'Ω', text)
	
		text = re.sub(r'ῥ', 'ρ', text)
	
		#remove quotes as they can lead to incorrect syllabification
		text = re.sub(r'"', '', text)
		text = re.sub(r'„', '', text)
		text = re.sub(r'“', '', text)
		
		#finally, lower-case everything
		return text.lower()
		
	#syllabifies words, removes punctuation, using existing library
	def simple_syllabify(self, text):
		resultsent = ''
		words = re.split(r' ', text)
		for word in words:
			#remove punctuation
			word = re.sub(r'[,:\.]', '', word)
			syllabified = syllabify(word)
			resultsent+=str(display_word(syllabified))
			resultsent+=str(' ')
			
		return resultsent.rstrip(' ')
		
	#count the number of syllables in the input verse
	def count_syllables(self, text):
		return(len(re.findall(r'[\. ]', text))+1)

#class containing linguistic rules
class ruleset(object):	
	#TODO: Formulierung der Regeln mit Pascal-Skript abgleichen
		
	#normally long
	def rule1(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		if re.search(r'[ηω]', current):
			return True
		
	#normally long
	def rule2(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		if re.search(r'(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)$', current):
			return True
		
	#normally long
	def rule3(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		next = text[position+1]
		if re.match(r'^(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)', next):
			return True
		
	#normally long
	def rule4(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		next = text[position+1]
		if re.match(r'([βγδθκλμνπρστφχξζψ]{2,*}|[ξζψ])', next):
			return True
		
	#muta cum liquida
	def muta(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		next = text[position+1]
		if re.match(r'[βγδπτκφχθ][λρνμ]', next):
			return True
		
	#hiat
	def hiat(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		next = text[position+1]
		if re.search(r'[αιουεωη]{1,2}', current) and re.match(r'[αιουεωη]{1,2}', next):
			return True

#FSAs governing the application of rules
class FSA13(object):

	states = ['waiting', 'searching_for_daktylus', 'daktylus_found', 'daktylus_not_found', 'fallback']
	
	def __init__(self, name):
		#name of the FSA
		self.name = name
		#status parameter
		self.found = False
		self.rules = ruleset()
		#initialisation
		self.machine = Machine(model=self, states=FSA13.states, initial='waiting')
		
		#transitions
		self.machine.add_transition(trigger='start_analysis', source='waiting', dest='searching_for_daktylus')
		self.machine.add_transition(trigger='search_daktylus', source='searching_for_daktylus', dest='daktylus_found', conditions=['is_found'])
		self.machine.add_transition('search_daktylus', 'searching_for_daktylus', 'daktylus_not_found', unless=['is_found'])
		self.machine.add_transition('success', 'daktylus_found', 'waiting')
		self.machine.add_transition('failure', 'daktylus_not_found', 'fallback')
		
	def is_found():
		return self.found
	
class FSA14(object):

	states = ['waiting', 'searching_for_first_daktylus', 'searching_for_second_daktylus', 'no_daktylus_found', 'found_two_daktylus', 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found_first = False
		self.found_second = False
		self.rules = ruleset()
		self.machine = Machine(model=self, states=FSA14.states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_daktylus')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus', 'searching_for_second_daktylus', conditions=['is_found(1)'])
		self.machine.add_transition('search daktylus', 'searching_for_first_daktylus', 'no_daktylus_found', unless=['is_found(1)'])
		self.machine.add_transition('search_second', 'searching_for_second_daktylus', 'found_two_daktylus', conditions=['is_found(2)'])
		self.machine.add_transition('search_second', 'searching_for_second_daktylus', 'no_daktylus_found', unless=['is_found(2)'])
		self.machine.add_transition('success', 'found_two_daktylus', 'waiting')
		self.machine.add_transition('failure', 'no_daktylus_found', 'fallback')
		
	def is_found(position):
		if position == 1:
			return self.found_first
		elif position == 2:
			return self.found_second
		else:
			raise Exception("invalid position")
	
class FSA15(object):

	states = ['waiting', 'searching_for_first_spondeus', 'searching_for_second_spondeus', 'no_spondeus_found', 'found_two_spondees', 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found_first = False
		self.found_second = False
		self.rules = ruleset()
		self.machine = Machine(model=self, states=FSA15.states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus', 'searching_for_second_spondeus', conditions=['is_found(1)'])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus', 'no_spondeus_found', unless=['is_found(1)'])
		self.machine.add_transition('search_second', 'searching_for_second_spondeus', 'found_two_spondees', conditions=['is_found(2)'])
		self.machine.add_transition('search_second', 'searching_for_second_spondeus', 'no_spondeus_found', unless=['is_found(2)'])
		self.machine.add_transition('success', 'found_two_spondees', 'waiting')
		self.machine.add_transition('failure', 'no_spondeus_found', 'fallback')
		
		
	def is_found(position):
		if position == 1:
			return self.found_first
		elif position == 2:
			return self.found_second
		else:
			raise Exception("invalid position")
	
class FSA16(object):

	states = ['waiting', 'searching_for_first_spondeus', 'searching_for_second_spondeus', 'searching_for_third_spondeus', 'no_spondeus_found', 'found_three_spondees', 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found_first = False
		self.found_second = False
		self.found_third = False
		self.rules = ruleset()
		self.machine = Machine(model=self, states=FSA16.states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus', 'searching_for_second_spondeus', conditions=['is_found(1)'])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus', 'no_spondeus_found', unless=['is_found(1)'])
		self.machine.add_transition('search_second', 'searching_for_second_spondeus', 'searching_for_third_spondeus', conditions=['is_found(2)'])
		self.machine.add_transition('search_second', 'searching_for_second_spondeus', 'no_spondeus_found', unless=['is_found(2)'])
		self.machine.add_transition('search_third', 'searching_for_third_spondeus', 'found_three_spondees', conditions=['is_found(3)'])
		self.machine.add_transition('search_third', 'searching_for_third_spondeus', 'no_spondeus_found', unless=['is_found(3)'])
		self.machine.add_transition('success', 'found_three_spondees', 'waiting')
		self.machine.add_transition('failure', 'no_spondeus_found', 'fallback')
		
	def is_found(position):
		if position == 1:
			return self.found_first
		elif position == 2:
			return self.found_second
		elif position == 3:
			return self.found_second
		else:
			raise Exception("invalid position")
		
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

#make dedicated FSAs for processing lines with defferent syllable count
fsa13 = FSA13('fsa13')
fsa14 = FSA14('fsa14')
fsa15 = FSA15('fsa15')
fsa16 = FSA16('fsa16')

counter = 0

for line in lines:
#for line in selection:
	scansion = ''
	
	vals = re.split(r'\t+', line.rstrip('\r?\n?'))
	
	#preprocessing
	text = prep.normalise(vals[1])
	syllabified = prep.simple_syllabify(text)
	
	#scansion annotation
	syllable_count = prep.count_syllables(syllabified)
	
	if syllable_count == 12:
		scansion = '-- -- -- -- -- -X'
		
	elif syllable_count == 13:
		scansion = 'one daktylus must be found'
		fsa13.start_analysis()
		
		#reset automaton when processing is finished
		if fsa13.state != 'waiting':
			fsa13.to_waiting()
		
	elif syllable_count == 14:
		scansion = 'two daktylus must be found'
		fsa14.start_analysis()
		
		if fsa14.state != 'waiting':
			fsa14.to_waiting()
	
	elif syllable_count == 15:
		scansion = 'two spondees must be found'
		fsa15.start_analysis()
		
		if fsa15.state != 'waiting':
			fsa15.to_waiting()
		
	elif syllable_count == 16:
		scansion = 'three spondees must be found'
		fsa16.start_analysis()
		
		if fsa16.state != 'waiting':
			fsa16.to_waiting()
		
	elif syllable_count == 17:
		scansion = '-** -** -** -** -** -X'
	
	else:
		print("WARNING: Incorrect syllable count: " + vals[0])
		counter += 1
	
	print("{}\t{}\t{}\t{}".format(vals[0], vals[1], syllabified, scansion), file=outfile)
	
print(counter, " incorrectly syllabified verses")
#TODO: check whether other syllabification produces better result
#TODO: check how many verses in corpus consist of only one word