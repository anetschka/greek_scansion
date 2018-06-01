import re
#utf8 support
import codecs
#for random number generation
from random import randint
#for stripping diacritics
import unicodedata
#for simple syllabification
from greek_accentuation.syllabify import syllabify, display_word

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

	#reads external preposition file
	def __init__(self):
		self.prepositions = codecs.open('resources/long_prepositions.txt', 'r', 'utf-8').readlines()
		preps = list(self.prepositions)
		self.prepositions = sorted(preps, key=len, reverse=True)
		self.prep_pattern = '('
		for preposition in self.prepositions:
			preposition = re.sub(r'\r?\n?', '', preposition)
			self.prep_pattern+=preposition
			self.prep_pattern+='|'
		self.prep_pattern = self.prep_pattern[:-1]
		self.prep_pattern+=')'
	
	#removes accents, lowercases
	def normalise(self, text):
		#some regexes have to be applied more than once since diacritics can be combined
		text = re.sub(r'ῆ', 'ηz', text) #replace circumflex by something that is easier to handle
		text = re.sub(r'ἣ', 'η', text)
		text = re.sub(r'ὴ', 'η', text)
		text = re.sub(r'ἡ', 'η', text)
		text = re.sub(r'ή', 'η', text)
		text = re.sub(r'ἠ', 'η', text)
		text = re.sub(r'ῆ', 'ηz', text)
		text = re.sub(r'ῃ', 'η', text)
		text = re.sub(r'ὴ', 'η', text)
		text = re.sub(r'ή', 'η', text)
		text = re.sub(r'ῃ', 'η', text)
		text = re.sub(r'ῇ', 'ηz', text)
	
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
	
		text = re.sub(r'ῒ', 'ϊ', text)
		text = re.sub(r'ΐ', 'ϊ', text)
		#text = re.sub(r'ϊ', 'ι', text) 
		text = re.sub(r'ὶ', 'ι', text) 
		text = re.sub(r'ί', 'ι', text) 
		text = re.sub(r'ῖ', 'ιz', text) 
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
	
		text = re.sub(r'ΰ', 'ϋ', text)
		text = re.sub(r'ῢ', 'ϋ', text)
		text = re.sub(r'ῦ', 'υz', text)
		text = re.sub(r'ύ', 'υ', text)
		text = re.sub(r'ὐ', 'υ', text)
		text = re.sub(r'ὺ', 'υ', text)
		text = re.sub(r'ὗ', 'ῦ', text)
		text = re.sub(r'ὕ', 'υ', text)
		#text = re.sub(r'ϋ', 'υ', text)
		text = re.sub(r'ὑ', 'υ', text)
		text = re.sub(r'ῦ', 'υz', text)
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
		text = re.sub(r'ῶ', 'ωz', text)
		text = re.sub(r'ᾧ', 'ῶ', text)
		text = re.sub(r'ὡ', 'ω', text)
		text = re.sub(r'ῶ', 'ωz', text)
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
			
		return re.split(r'[ \.]', resultsent.rstrip(' '))
		
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
		
		return re.split(r'[ \.]', resultsent.rstrip(' '))
		
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
		
		return re.split(r'[ \.]', resultsent.rstrip(' '))
		
	#syllabifies words, removes punctuation, following the article by Papakitsos, E: "Computerized scansion of Ancient Greek Hexameter" in combination
	#with a few other rules
	def papakitsos_syllabify(self, text):
		resultsent = ''
		#prepositions appearing in compounds
		preps = re.compile(' '+self.prep_pattern+'[^\' ]{4}')
		diphtongs = ['αι', 'οι', 'υι', 'ει', 'αυ', 'ευ', 'ου', 'ηι', 'ωι', 'ηυ']
		vowels = ['α', 'ι', 'ο', 'υ', 'ε', 'η', 'ω']
		consonants = ['ς', 'β', 'γ', 'δ', 'θ', 'κ', 'λ', 'μ', 'ν', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ξ', 'ζ', 'ψ']
		clusters = ['βδ', 'βλ', 'βρ', 'γδ', 'γλ', 'γμ', 'γν', 'γρ', 'δμ', 'δν', 'δρ', 'θλ', 'θμ', 'θν', 'θρ', 'κλ', 'κμ', 'κν', 'κρ', 'κτ', 'μν', 'πλ', 'πν', 'πρ', 'πτ', 'σβ', 'σγ', 'σθ', 'σκ', 'σμ', 'σπ', 'στ', 'σφ', 'σχ', 'τλ', 'τμ', 'τν', 'τρ', 'φθ', 'φλ', 'φν', 'φρ', 'χθ', 'χλ', 'χμ', 'χν', 'χρ']
		#handling of prepositions
		matches = re.findall(preps, text)
		for match in matches:
			found = re.search(match, text)
			if found:
				text = re.sub(match, found.group() + ' ', text)
		cleaned = re.sub(r'[,:\.]', '', text)
		letters = list(cleaned)
		simple = []
		for x in range(0, len(letters)-1):
			if letters[x] == 'z':
				continue
			if letters[x+1] == 'z':
				letters[x] += letters[x+1]
			simple.append(letters[x])
		syllabified = ''
		for index in range(0, len(simple)):
			if index == len(simple)-1 and simple[index-1] in vowels and simple[index] in vowels and (simple[index-1] + simple[index]) not in diphtongs:
				syllabified+='.'
				syllabified+=simple[index]
			#consonant between vowels
			elif index > 0 and index < len(simple)-1 and simple[index] in consonants and simple[index-1] in vowels and simple[index+1] in vowels:
				syllabified+='.'
				syllabified+=simple[index]
			#vowel before new word with consonant cluster
			elif index < len(simple)-2 and simple[index] in vowels and (simple[index+1] + simple[index+2] in clusters):
				syllabified+=simple[index]
				syllabified+='.'
			#vowel before consonant cluster
			elif index < len(simple)-1 and simple[index-1] in vowels and simple[index] in consonants and simple[index+1] in consonants and (simple[index] + simple[index+1] not in clusters):
				syllabified+=simple[index]
				syllabified+='.'
			#vowel before diphtong
			elif index < len(simple)-2 and simple[index] in vowels and (simple[index+1] + simple[index+2] in diphtongs):
				syllabified+=simple[index]
				syllabified+='.'
			#first vowel of diphtong
			elif index < len(simple)-1 and (simple[index] + simple[index+1] in diphtongs):
				syllabified+=simple[index]
			#second vowel of diphtong
			elif index > 0 and index < len(simple)-1 and (simple[index-1] + simple[index] in diphtongs):
				syllabified+=simple[index]
				syllabified+='.'
			#sequence of vowels
			elif index < len(simple)-2 and simple[index] in vowels and simple[index+1] in vowels and (simple[index+1] + simple[index+2] not in diphtongs):
				syllabified+=simple[index]
				syllabified+='.'
			else:
				syllabified+=simple[index]
		resultsent+=syllabified	
		
		#treatment of elision
		resultsent = re.sub(r'(.)\'\.? ', '.\g<1>', resultsent)
		#however, a single consonant should not be separated from the next syllable
		resultsent = re.sub(r'(\.[ςβγδθκλμνπρστφχξζψ])\.', '\g<1>', resultsent)
		#treatment of remaining accents
		resultsent = re.sub(r'([ιυ])\.̈', '.\g<1>.', resultsent)
		#treatment of consonants at end of word
		resultsent = re.sub(r'\.([ςβγδθκλμνπρστφχξζψ] )', '\g<1>', resultsent)
		#last consonant in verse or word
		resultsent = re.sub(r'\.([ςβγδθκλμνπρστφχξζψ])$', '\g<1>', resultsent)
		#further cleaning
		resultsent = re.sub(r'\.\.', '.', resultsent)
		resultsent = re.sub(r'\. ', ' ', resultsent)
		resultsent = re.sub(r' \.', ' ', resultsent)

		syllabs = re.split(r'[ \.]', resultsent)
		return syllabs
		
	#count the number of syllables in the input verse
	def count_syllables(self, text):
		return len(text)
