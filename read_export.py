import re
import sys
import codecs
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
	
		#remove quotes as they can lead to improper syllabification
		text = re.sub(r'"', '', text)
		
		return text
		
	def syllabify(self, text):
		resultsent = ''
		words = re.split(r' ', text)
		for word in words:
			syllabified = syllabify(word)
			resultsent+=str(display_word(syllabified))
			resultsent+=str(' ')
			
		return resultsent.rstrip(' ')
	
####MAIN PROGRAM####	
	
infile = codecs.open(sys.argv[1], "r", "utf-8")
outfile = codecs.open(sys.argv[2], "w", "utf-8")

lines = infile.readlines()

#get a verse selector: use this to select and process a random subset of verses
#sel = selector()
#selection = sel.select(lines, 1)
#print(selection)

#get a preprocessor
prep = preprocessor()

for line in lines:
	vals = re.split(r'\t+', line.rstrip('\r?\n?'))
	
	#was bedeuten im text die vielen apostrophe (elisionen?)
	#sentence id 73, 271, 372, 34434: schluss-sigma? welche bedeutung hat es? -> eher: fehlerhafte Darstellung von Großbuchstaben -> nach anderen stellen suchen, in denen dies auftritt
	#34453 -> N
	#Achilleus mal mit einem, mal mit zwei l -> normal?
	
	text = prep.normalise(vals[4])
	result = prep.syllabify(text)
	
	print("{}\t{}\t{}\t{}\t{}\t{}".format(vals[0], vals[1], vals[2], vals[3], vals[4], result), file=outfile)