import re
import sys
import hfst
import codecs
#the general algorithm is implemented as finite-state machine
import transitions
#for random number generation
from random import randint
#for syllabification
from greek_accentuation.syllabify import syllabify, display_word

####CLASS DEFINITIONS####

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
		
	#syllabifies words, removes punctuation
	def syllabify(self, text):
		resultsent = ''
		words = re.split(r' ', text)
		for word in words:
			#remove interpunction
			word = re.sub(r'[,:\.]', '', word)
			syllabified = syllabify(word)
			resultsent+=str(display_word(syllabified))
			resultsent+=str(' ')
			
		return resultsent.rstrip(' ')

class annotator(object):

	#count the number of syllables in the input verse
	#based on syllabification performed by preprocessor class
	def count_syllables(self, text):
		return(len(re.findall(r'[\. ]', text))+1)
		
	def rule1(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		return(re.search(r'[ηω]', current))
		
	def rule2(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		return(re.search(r'(αι|οι|νι|ει|αν|εν|ον|ηι|ωι|ην)$', current))
		
	def rule3(self, text, position):
		text = re.split(r'[ \.]', text)
		current = text[position]
		next = text[position+1]
		return(re.match(r'(αι|οι|νι|ει|αν|εν|ον|ηι|ωι|ην)', next))
		
####MAIN PROGRAM####	
	
infile = codecs.open(sys.argv[1], "r", "utf-8")
outfile = codecs.open(sys.argv[2], "w", "utf-8")

lines = infile.readlines()

#get a verse selector: use this to select and process a random subset of verses
##sel = selector()
##selection = sel.select(lines, 1)
##print(selection)

#get a preprocessor
prep = preprocessor()

#get an annotator
ann = annotator()

for line in lines:
	scansion = ''
	
	vals = re.split(r'\t+', line.rstrip('\r?\n?'))
	
	#preprocessing
	text = prep.normalise(vals[4])
	syllabified = prep.syllabify(text)
	
	#scansion annotation
	syllable_count = ann.count_syllables(syllabified)
	
	if syllable_count == 12:
		scansion = '-- -- -- -- -- -X'
		
	elif syllable_count == 13:
		scansion = 'one daktylus must be found'
		
	elif syllable_count == 14:
		scansion = 'two daktylus must be found'
	
	elif syllable_count == 15:
		scansion = 'two spondees must be found'
		
	elif syllable_count == 16:
		scansion = 'three spondees must be found'
		
	elif syllable_count == 17:
		scansion = '-** -** -** -** -** -X'
	
	print("{}\t{}\t{}\t{}".format(vals[0], vals[4], syllabified, scansion), file=outfile)