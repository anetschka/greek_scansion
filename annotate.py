import re
import sys
#for finite-state transducer (fallback processing)
import hfst
import codecs
#for random number generation
from random import randint
#the general algorithm is implemented as finite-state machine
from transitions import Machine
from transitions.extensions.states import add_state_features, Tags
#for simple syllabification (baseline)
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
		
	#syllabifies words, removes punctuation, using a simple rule
	def vowel_syllabify(self, text):
		resultsent = ''
		words = re.split(r' ', text)
		pattern = re.compile(r'([αιουεηω])')
		for word in words:
			word = re.sub(r'[,:\.]', '', word)
			syllabified = pattern.sub('\\1.', word)
			resultsent+=syllabified.rstrip('\.')
			resultsent+=str(' ')
		
		return resultsent.rstrip(' ')
		
	#syllabifies words, removes punctuation, re-implementing CLTK rules
	#https://github.com/cltk/cltk/blob/master/cltk/prosody/greek/scanner.py
	def cltk_syllabify(self,text):
		resultsent = ''
		words = re.split(r' ', text)
		diphtongs = ['αι', 'οι', 'υι', 'ει', 'αυ', 'ευ', 'ου', 'ηι', 'ωι', 'ηυ']
		vowels = ['α', 'ι', 'ο', 'υ', 'ε', 'η','ω']
		consonants = ['ς', 'β', 'γ', 'δ', 'θ', 'κ', 'λ', 'μ', 'ν', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ξ', 'ζ', 'ψ']
		for word in words:
			word = re.sub(r'[,:\.]', '', word)
			syllabified = ''
			letters = list(word)
			counter = 0
			for letter in letters:
				syllabified+=letter
				if letter in vowels:
					#consonant in end belongs to last syllable
					if (counter == len(letters)-2) and \
					(letters[counter+1] in consonants):
						continue
					#not last letter
					if (counter < len(letters)-1) and \
					(letter + letters[counter+1] not in diphtongs): #don't separate diphtong
						syllabified+='.'
				counter+=1
			
			resultsent+=syllabified
			resultsent+=str(' ')
		
		return resultsent.rstrip(' ')
		
	#syllabifies words, removes punctuation, following the article by Papakitsos, E: "Computerized scansion of Ancient Greek Hexameter"
	def papakitsos_syllabify(self, text):
		resultsent = ''
		diphtongs = ['αι', 'οι', 'υι', 'ει', 'αυ', 'ευ', 'ου', 'ηι', 'ωι', 'ηυ']
		vowels = ['α', 'ι', 'ο', 'υ', 'ε', 'η','ω']
		consonants = ['ς', 'β', 'γ', 'δ', 'θ', 'κ', 'λ', 'μ', 'ν', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ξ', 'ζ', 'ψ']
		clusters = ['βδ', 'βλ', 'βρ', 'γδ', 'γλ', 'γμ', 'γν', 'γρ', 'δμ', 'δν', 'δρ', 'θλ', 'θμ', 'θν', 'θρ', 'κλ', 'κμ', 'κν', 'κρ', 'κτ', 'μν', 'πλ', 'πν', 'πρ', 'πτ', 'σβ', 'σγ', 'σθ', 'σκ', 'σμ', 'σπ', 'στ', 'σφ', 'σχ', 'τλ', 'τμ', 'τν', 'τρ', 'φθ', 'φλ', 'φν', 'φρ', 'χθ', 'χλ', 'χμ', 'χν', 'χρ']
		cleaned = re.sub(r'[,:\.]', '', text)
		letters = list(cleaned)
		syllabified = ''
		for index in range(0, len(letters)):
			#first and last letter letter
			if index == 0 or index == len(letters):
				syllabified+=letters[index]
			#consonant between vowels
			elif index > 0 and index < len(letters)-1 and letters[index] in consonants and letters[index-1] in vowels and letters[index+1] in vowels:
				syllabified+='.'
				syllabified+=letters[index]
			elif index < len(letters)-2 and letters[index] in vowels and (letters[index+1] + letters[index+2] in clusters):
				syllabified+=letters[index]
				syllabified+='.'
			elif index < len(letters)-1 and letters[index-1] in vowels and letters[index] in consonants and letters[index+1] in consonants and (letters[index] + letters[index+1] not in clusters):
				syllabified+=letters[index]
				syllabified+='.'
			else:
				syllabified+=letters[index]
		resultsent+=syllabified	
		
		return resultsent
		
	#count the number of syllables in the input verse
	def count_syllables(self, text):
		return(len(re.findall(r'[\. ]', text))+1)
		
	#find out whether text is very short (not enough syllables)
	def find_spurious_verse(self, text):
		return(len(re.findall(r' ', text))+1)

#class containing linguistic rules
class ruleset(object):	
		
	#long by nature
	def rule1(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position-1]
		if re.search(r'[ηω]', current):
			return True
		
	#long by nature
	def rule2(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position-1]
		#if re.search(r'(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)$', current):
		if re.search(r'(υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)$', current):
			return True
		
	#long by position
	def rule3(self, text, position):
		text = re.split(r'[ \.]', text)
		next = text[position]
		if re.match(r'^(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)', next):
			return True
		
	#long by position
	def rule4(self, text, position):
		text = re.split(r'[ \.]', text)
		next = text[position]
		if re.match(r'([ςβγδθκλμνπρστφχξζψ]{2,*}|[ξζψ])', next):
			return True
		
	#muta cum liquida
	def muta(self, text, position):
		text = re.split(r'[ \.]', text)
		next = text[position]
		if re.match(r'[βγδπτκφχθ][λρνμ]', next):
			return True
		
	#hiat
	def hiat(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position-1]
		next = text[position]
		if re.search(r'[αιουεωη]{1,*}', current) and re.match(r'[αιουεωη]{1,*}', next):
			return True

#FSAs governing the application of rules
@add_state_features(Tags)
class CustomStateMachine(Machine):
	pass
	
class FSA13(object):

	states = [{'name': 'waiting', 'on_enter': 'reset_found'}, {'name': 'searching_for_daktylus', 'on_enter': 'search_daktylus'}, {'name': 'daktylus_found', 'tags': 'accepted'}, 'daktylus_not_found', 'fallback']
	
	def __init__(self, name):
		#name of the FSA
		self.name = name
		self.rules = ruleset()
		#text to be analyed
		self.text = ''
		#resulting scansion
		self.scansion = ''
		#initialisation
		self.machine = CustomStateMachine(model=self, states=FSA13.states, initial='waiting')
		
		#transitions
		self.machine.add_transition(trigger='start_analysis', source='waiting', dest='searching_for_daktylus')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus', 'daktylus_found')
		self.machine.add_transition('not_found', 'searching_for_daktylus', 'daktylus_not_found')
		self.machine.add_transition('fallback_analysis', 'daktylus_not_found', 'fallback')
			
	def search_daktylus(self):
		if self.search(10):
			self.scansion = '-- -- -- -- -** -X'
			#solution found, no need to execute the rest
			return
		elif self.search(6):
			self.scansion = '-- -- -** -- -- -X'
			return
		elif self.search(8):
			self.scansion = '-- -- -- -** -- -X'
			return
		elif self.search(2):
			self.scansion = '-** -- -- -- -- -X'
			return
		elif self.search(4):
			self.scansion = '-- -** -- -- -- -X'
			return
	
	def reset_found(self):
		self.found = False
	
	def set_text(self, text):
		self.text = text
		
	def search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
	
class FSA14(object):

	states = ['waiting', 'searching_for_first_daktylus', 'searching_for_second_daktylus', 'no_daktylus_found', {'name': 'found_two_daktyles', 'tags': 'accepted'}, 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found_first = False
		self.found_second = False
		self.rules = ruleset()
		self.text = ''
		self.machine = CustomStateMachine(model=self, states=FSA14.states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_daktylus')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus', 'searching_for_second_daktylus', conditions=['is_found(1)'])
		self.machine.add_transition('search daktylus', 'searching_for_first_daktylus', 'no_daktylus_found', unless=['is_found(1)'])
		self.machine.add_transition('search_second', 'searching_for_second_daktylus', 'found_two_daktyles', conditions=['is_found(2)'])
		self.machine.add_transition('search_second', 'searching_for_second_daktylus', 'no_daktylus_found', unless=['is_found(2)'])
		self.machine.add_transition('failure', 'no_daktylus_found', 'fallback')
		
	def is_found(self, position):
		if position == 1:
			return self.found_first
		elif position == 2:
			return self.found_second
		else:
			raise Exception("invalid position")
			
	def set_text(self, text):
		self.text = text
	
class FSA15(object):

	states = ['waiting', 'searching_for_first_spondeus', 'searching_for_second_spondeus', 'no_spondeus_found', {'name': 'found_two_spondees', 'tags': 'accepted'}, 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found_first = False
		self.found_second = False
		self.rules = ruleset()
		self.text = ''
		self.machine = CustomStateMachine(model=self, states=FSA15.states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus', 'searching_for_second_spondeus', conditions=['is_found(1)'])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus', 'no_spondeus_found', unless=['is_found(1)'])
		self.machine.add_transition('search_second', 'searching_for_second_spondeus', 'found_two_spondees', conditions=['is_found(2)'])
		self.machine.add_transition('search_second', 'searching_for_second_spondeus', 'no_spondeus_found', unless=['is_found(2)'])
		self.machine.add_transition('failure', 'no_spondeus_found', 'fallback')
		
		
	def is_found(self, position):
		if position == 1:
			return self.found_first
		elif position == 2:
			return self.found_second
		else:
			raise Exception("invalid position")
	
	def set_text(self, text):
		self.text = text
	
class FSA16(object):
	states = ['waiting', 'searching_for_spondeus', {'name': 'spondeus_found', 'tags': 'accepted'}, 'spondeus_not_found', 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found = False
		self.rules = ruleset()
		self.text = ''
		self.machine = CustomStateMachine(model=self, states=FSA16.states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_spondeus')
		self.machine.add_transition('search_spondeus', 'searching_for_spondeus', 'spondeus_found', conditions=['is_found()'])
		self.machine.add_transition('search_spondeus', 'searching_for_spondeus', 'spondeus_not_found', unless=['is_found()'])
		self.machine.add_transition('failure', 'spondeus_not_found', 'fallback')
		
	def is_found(self):
		return self.found
		
	def set_text(self, text):
		self.text = text
		
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
	if prep.find_spurious_verse(text) < 3:
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
		if(fsa13.scansion):
			fsa13.found_daktylus()
			scansion = fsa13.scansion
		else:
			print('not found, fallback required')
			fsa13.not_found()
		
	elif syllable_count == 14:
		scansion = 'two daktyles must be found'
		if fsa14.state != 'waiting':
			fsa14.to_waiting()
		fsa14.start_analysis()
	
	elif syllable_count == 15:
		scansion = 'two spondees must be found'
		if fsa15.state != 'waiting':
			fsa15.to_waiting()
		fsa15.start_analysis()
		
	elif syllable_count == 16:
		scansion = 'one spondeus must be found'
		if fsa16.state != 'waiting':
			fsa16.to_waiting()
		fsa16.start_analysis()
		
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