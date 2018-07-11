import re
import transducer
from transitions.extensions import HierarchicalMachine as Machine
from transitions.extensions.states import add_state_features, Tags

#class containing linguistic rules
class ruleset(object):	
		
	#long by nature
	def rule1(self, text, position):
		current = text[position-1]
		if re.search(r'[ηω]', current):
			return True
		
	#long by nature
	def rule2(self, text, position):
		current = text[position-1]
		#if re.search(r'(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)$', current):
		if re.search(r'(υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)$', current):
			return True
		
	#long by position
	def rule3(self, text, position):
		following = text[position]
		if re.match(r'^(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)', following):
			return True
		
	#long by position
	def rule4(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'([αιουεωη][ςβγδθκλμνπρστφχξζψ]{2,}|[αιουεωη][ξζψ])', current+following):
			return True
		
	#muta cum liquida
	def muta(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'[αιουεωη][βγδπτκφχθ][λρνμ]', current+following):
			return True
		
	#hiat
	def hiat(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'[αιουεωη]{2,*}', current+following):
		#if re.search(r'[αιουεωη]{1,*}$', current) and re.match(r'^[αιουεωη]{1,*}', following):
			return True

	#circumflex
	def circumflex(self, text, position):
		current = text[position-1]
		if re.search(r'z', current):
			return True

#class representing verse object; it makes verse, syllables, and scansion available at all times
class verse(object):

	def __init__(self):
		self.verse = ''
		self.syllables = ''
		self.scansion = ''

	def clear(self):
		self.verse = ''
		self.syllables = ''
		self.scansion = ''

#superclass encapsulating basic functionality
class annotator(object):

	def __init__(self, name):
		self.name = name
		self.rules = ruleset()
		self.verse = verse()
		self.positions = []
		self.questions = []
		self.first_found = False
		self.second_found = False
		self.third_found = False
		self.fourth_found = False
		self.transducer = transducer.transducer()
		self.success = True
			
	def _reset_positions(self):		
		self.positions = []
		self.questions = []
		self.verse.clear()
		self.first_found = False
		self.second_found = False
		self.third_found = False
		self.fourth_found = False
		self.success = True
		
	def set_text(self, verse, syllables):
		self.verse.verse = verse
		self.verse.syllables = syllables
			
	def _set_found(self):
		if not self.first_found:
			self.first_found = True
		elif not self.second_found:
			self.second_found = True
		elif not self.third_found:
			self.third_found = True
		else:
			self.fourth_found = True

	def _found_first(self):
		return self.first_found
		
	def _found_second(self):
		return self.second_found

	def _found_third(self):
		return self.third_found

	def _found_fourth(self):
		return self.fourth_found

	def _is_successful(self):
		return self.success
			
	def _make_spondeus(self, limit):
		self.verse.scansion = '-'
		for x in range(2, limit+1):
			if x in self.positions:
				self.verse.scansion+='-'
			else:
				self.verse.scansion+='?'
		self.verse.scansion+='-X'

	def _verify_output(self):
		#TODO: turn into proper code
		#for now we verify only the first scansion variant given by the transducer
		versions = re.split(r'###', self.verse.scansion)
		if(len(versions) > 1):
			self.success = self._verify_string(versions[1])
		else:
			self.success = self._verify_string(versions[0])
		self.verified()

	def _verify_string(self, string):
		s_units = list(filter(lambda s: re.match(r'[-\?\*]', s), string))
		for x in range(0, len(s_units)-2):
			if self._search_long(x+1) and s_units[x] == '*':
				return False
			elif s_units[x] == '?':
				return False
		return True

	#function used to search the whole verse for long syllables (in fallback)
	def _search_whole(self):
		s_units = list(self.verse.scansion)
		for x in range(1, len(s_units)-2): #no need to scan last two syllabs
			if s_units[x] == '?':
				search_result = self._search_long(x+1)
				if search_result:
					s_units[x] = '-'
		self.verse.scansion = ''.join(s_units)
		#actually, we can already make some very obvious corrections
		self.verse.scansion = re.sub(r'-\?-', '---', self.verse.scansion)
		self.verse.scansion = re.sub(r'-\?\?-X', '-**-X', self.verse.scansion)
		self.verse.scansion = re.sub(r'-\?-X', '---X', self.verse.scansion)
		#apply finite-state transducer
		results = self.transducer.apply(self.verse.scansion).extract_paths(output='dict')
		#lets output all valid solutions
		#TODO: develop selection function
		for input, outputs in results.items():
			for output in outputs:	
				if not self._verify_string(output[0]):
					continue
				self.verse.scansion = self.verse.scansion + '###' + output[0]
		#we currently just select the solution that maximizes the weight
		#weight = 0
		#for input, outputs in results.items():
		#	for output in outputs:
		#		if output[1] > weight:
		#			weight = output[1]
		#			self.verse.scansion = output[0]
		self._verify_output()

	def _correct(self):
		self._correct_string()
		#TODO: This transition does not work right now
		#TODO: FST needs to produce output string
		#TODO: make functioning state transition call
		#remember to set self.success
		self.corrected()

	#this function assigns length vowel by vowel, but only if all other processing before has failed
	def _correct_string(self):
		diphtongs = ['αι', 'οι', 'υι', 'ει', 'αυ', 'ευ', 'ου', 'ηι', 'ωι', 'ηυ']
		vowels = ['α', 'ι', 'ο', 'υ', 'ε', 'η','ω', 'z']
		consonants = ['ς', 'β', 'γ', 'δ', 'θ', 'κ', 'λ', 'μ', 'ν', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ξ', 'ζ', 'ψ']
		letters = list(filter(lambda s: re.match(r'[^ ]', s), self.verse.verse))
		self.verse.scansion += '###corrected###'
		for x in range(0, len(letters)-2):
			if letters[x] in vowels:
				if letters[x] == 'z' and letters[x-1] != 'ω' and letters[x-1] != 'η':
					(head, sep, tail) = self.verse.scansion.rpartition('?')
					if x > 1 and (letters[x-2] + letters[x-1] in diphtongs):
						(head2, sep, tail) = head.rpartition('?')
						self.verse.scansion = head2 + '-'
					else:
						self.verse.scansion = head + '-'
					continue
				elif (letters[x] == 'η' or letters[x] == 'ω') and letters[x+1] not in vowels:
					self.verse.scansion += '-'
					continue
				elif (letters[x-1] == 'η' or letters[x-1] == 'ω') and letters[x] == 'z':
					(head, sep, tail) = self.verse.scansion.rpartition('?')
					self.verse.scansion = head + '-'
					continue
				elif x > 1 and (letters[x-1] + letters[x] in diphtongs) and (letters[x-1] + letters[x] != 'οι') and (letters[x-1] + letters[x] != 'αι') and letters[x+1] not in vowels:
					(head, sep, tail) = self.verse.scansion.rpartition('?')
					self.verse.scansion = head + '-'
					continue
				elif (letters[x+1] + letters[x+2] in diphtongs):
					if letters[x-1] in vowels:
						(head, sep, tail) = self.verse.scansion.rpartition('?')
						self.verse.scansion = head + '-'
					else:
						self.verse.scansion += '-'
					continue
				elif letters[x+1] in consonants and letters[x+2] in consonants and not re.match(r'[βγδπτκφχθ][λρνμ]', letters[x+1] + letters[x+2]):
					self.verse.scansion += '-'
					continue
				elif letters[x+1] in ['ξ', 'ζ', 'ψ']:
					self.verse.scansion += '-'
					continue
				elif x > 1 and letters[x-2] in consonants and (letters[x-1] + letters[x] in diphtongs) and (letters[x-1] + letters[x] != 'οι') and (letters[x-1] + letters[x] != 'αι'):
					(head, sep, tail) = self.verse.scansion.rpartition('?')
					self.verse.scansion = head + '-'
					continue
				else:
					self.verse.scansion += '?'

	def _search_long(self, position):
		if self.rules.circumflex(self.verse.syllables, position) or self.rules.rule3(self.verse.syllables, position):
			return True
		elif (self.rules.rule1(self.verse.syllables, position) or self.rules.rule2(self.verse.syllables, position)) and not self.rules.hiat(self.verse.syllables, position):
			return True
		elif self.rules.rule4(self.verse.syllables, position) and not self.rules.muta(self.verse.syllables, position):
			return True
		else:
			return False

class HFSA13(annotator):

	_states = [
		{'name': 'waiting', 'on_enter': '_reset_positions'},
		{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF']},
		{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF']},
		{'name': 'searching_for_third_spondeus', 'children': ['fourthF', 'thirdF']},
		{'name': 'searching_for_fourth_spondeus', 'children': ['thirdF', 'fifthF']},
		{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
		{'name': 'found_four_spondees', 'on_enter': '_make_scansion'},
		{'name': 'fallback', 'on_enter': '_search_whole'},
		{'name': 'correction', 'on_enter': '_correct'},
		'success',
		'failure'
	]

	def __init__(self, name):
		annotator.__init__(self, name)
		self.machine = Machine(model=self, states=HFSA13._states, initial='waiting')
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus_secondF', after='_search_second')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_first_spondeus_firstF', unless=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'no_spondeus_found', unless=[self._found_first])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_second_spondeus_firstF', conditions=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'searching_for_second_spondeus_fourthF', unless=[self._found_second], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'no_spondeus_found', unless=[self._found_second])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_second_spondeus_fourthF', conditions=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'searching_for_third_spondeus_fourthF', conditions=[self._found_second], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_fourthF', 'searching_for_third_spondeus_thirdF', unless=[self._found_third], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_thirdF', 'no_spondeus_found', unless=[self._found_third])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'searching_for_third_spondeus_thirdF', conditions=[self._found_second], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_thirdF', 'searching_for_fourth_spondeus_fifthF', conditions=[self._found_third], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_fourth_spondeus_fifthF', 'no_spondeus_found', unless=[self._found_fourth])
		self.machine.add_transition('search_spondeus', 'searching_for_fourth_spondeus_fifthF', 'found_four_spondees', conditions=[self._found_fourth])
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_fourthF', 'searching_for_fourth_spondeus_thirdF', conditions=[self._found_third], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_fourth_spondeus_thirdF', 'searching_for_fourth_spondeus_fifthF', unless=[self._found_fourth], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_fourth_spondeus_thirdF', 'found_four_spondees', conditions=[self._found_fourth])
		self.machine.add_transition('search_spondeus', 'found_four_spondees', 'no_spondeus_found')
		self.machine.add_transition('not_found', 'no_spondeus_found', 'fallback')
		self.machine.add_transition('verified', 'fallback', 'correction', unless=[self._is_successful])
		self.machine.add_transition('verified', 'fallback', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_two_spondees', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_two_spondees', 'correction', unless=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'success', conditions=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'failure', unless=[self._is_successful])

	def _search_second(self):
		third = self._search_long(3)
		fourth = self._search_long(4)
		fifth = self._search_long(5)
		if third and fourth:
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif fourth and fifth:
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		elif third:
			self.positions.append(3)
		elif fourth:
			self.positions.append(4)
		elif fifth:
			self.positions.append(5)
		self.search_spondeus()

	def _search_first(self):
		first = self._search_long(1)
		second = self._search_long(2)
		if first and second:
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif first:
			self.positions.append(1)
		elif second:
			self.positions.append(2)
		self.search_spondeus()

	def _search_fourth(self):
		seventh = self._search_long(7)
		eigth = self._search_long(8)
		ninth = self._search_long(9)
		if seventh and eigth:
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif eigth and ninth:
			self.positions.append(8)
			self.positions.append(9)
			self._set_found()
		else:
			if seventh:
				self.positions.append(7)
			if eigth:
				self.positions.append(8)
			if ninth:
				self.positions.append(9)
		self.search_spondeus()

	def _search_third(self):
		fifth = self._search_long(5)
		sixth = self._search_long(6)
		seventh = self._search_long(7)
		if fifth and sixth:
			self.positions.append(5)
			self.positions.append(6)
			self._set_found()
		elif sixth and seventh:
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		else:
			if sixth:
				self.positions.append(6)
			if seventh:
				self.positions.append(7)
			if fifth:
				self.positions.append(5)
		self.search_spondeus()

	def _search_fifth(self):
		tenth = self._search_long(10)
		eleventh = self._search_long(11)
		if tenth and eleventh:
			self.positions.append(10)
			self.positions.append(11)
			self._set_found()
		elif tenth:
			self.positions.append(10)
		elif eleventh:
			self.positions.append(11)
		self.search_spondeus()

	def _make_scansion(self):
		for x in range(1,12):
			if x not in self.positions:
				self.questions.append(x)
		#nr. 40
		if 10 in self.questions and 11 in self.questions:
			self.verse.scansion = '-- -- -- -- -** -X'
			self._verify_output()
		#nr. 41
		elif 8 in self.questions and 9 in self.questions:
			self.verse.scansion = '-- -- -- -** -- -X'
			self._verify_output()
		#nr. 42
		elif 6 in self.questions and 7 in self.questions:
			self.verse.scansion = '-- -- -** -- -- -X'
			self._verify_output()
		#nr. 43
		elif 4 in self.questions and 5 in self.questions:
			self.verse.scansion = '-- -** -- -- -- -X'
			self._verify_output()
		#nr. 44
		elif 2 in self.questions and 3 in self.questions:
			self.verse.scansion = '-** -- -- -- -- -X'
			self._verify_output()
		else:
			self.search_spondeus()

	def _make_spondeus(self):
		annotator._make_spondeus(self, 11)

class HFSA14(annotator):

	_states = [
		{'name': 'waiting', 'on_enter': '_reset_positions'},
		{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF', 'fourthF']},
		{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF', 'thirdF']},
		{'name': 'searching_for_third_spondeus', 'children': ['fourthF', 'thirdF', 'fifthF']},
		{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
		{'name': 'found_three_spondees', 'on_enter': '_make_scansion'},
		{'name': 'fallback', 'on_enter': '_search_whole'},
		{'name': 'correction', 'on_enter': '_correct'},
		'success',
		'failure'
	]

	def __init__ (self, name):
		annotator.__init__(self, name)
		self.machine = Machine(model=self, states=HFSA14._states, initial='waiting')
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus_secondF', after='_search_second')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_first_spondeus_firstF', unless=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_first_spondeus_fourthF', unless=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_fourthF', 'no_spondeus_found', unless=[self._found_first])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_second_spondeus_firstF', conditions=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'searching_for_second_spondeus_fourthF', unless=[self._found_second], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'searching_for_second_spondeus_thirdF', unless=[self._found_second], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_thirdF', 'no_spondeus_found', unless=[self._found_second])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_second_spondeus_firstF', conditions=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_second_spondeus_fourthF', conditions=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_fourthF', 'searching_for_second_spondeus_thirdF', conditions=[self._found_first], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_thirdF', 'searching_for_third_spondeus_fifthF', conditions=[self._found_second], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_fifthF', 'no_spondeus_found', unless=[self._found_third])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'searching_for_third_spondeus_fourthF', conditions=[self._found_second], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_fourthF', 'searching_for_third_spondeus_thirdF', unless=[self._found_third], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_thirdF', 'searching_for_third_spondeus_fifthF', unless=[self._found_third], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'searching_for_third_spondeus_thirdF', conditions=[self._found_second], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_fifthF', 'found_three_spondees', conditions=[self._found_third])
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_fourthF', 'found_three_spondees', conditions=[self._found_third])
		self.machine.add_transition('search_spondeus', 'searching_for_third_spondeus_thirdF', 'found_three_spondees', conditions=[self._found_third])
		self.machine.add_transition('search_spondeus', 'found_three_spondees', 'no_spondeus_found')
		self.machine.add_transition('not_found', 'no_spondeus_found', 'fallback')
		self.machine.add_transition('verified', 'fallback', 'correction', unless=[self._is_successful])
		self.machine.add_transition('verified', 'fallback', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_three_spondees', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_three_spondees', 'correction', unless=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'success', conditions=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'failure', unless=[self._is_successful])

	def _search_second(self):
		third = self._search_long(3)
		fourth = self._search_long(4)
		fifth = self._search_long(5)
		if third and fourth:
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif fourth and fifth:
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		else:
			if third:
				self.positions.append(3)
			if fourth:
				self.positions.append(4)
			if fifth:
				self.positions.append(5)
		self.search_spondeus()

	def _search_first(self):
		first = self._search_long(1)
		second = self._search_long(2)
		if first and second:
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif first:
			self.positions.append(1)
		elif second:
			self.positions.append(2)
		self.search_spondeus()
		
	def _search_fourth(self):
		eigth = self._search_long(8)
		ninth = self._search_long(9)
		tenth = self._search_long(10)
		if eigth and ninth:
			self.positions.append(8)
			self.positions.append(9)
			self._set_found()
		elif ninth and tenth:
			self.positions.append(9)
			self.positions.append(10)
			self._set_found()
		else:
			if eigth:
				self.positions.append(8)
			if ninth:
				self.positions.append(9)
			if tenth:
				self.positions.append(10)
		self.search_spondeus()
		
	def _search_third(self):
		sixth = self._search_long(6)
		seventh = self._search_long(7)
		eigth = self._search_long(8)
		if seventh and eigth:
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif sixth and seventh:
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		else:
			if sixth:
				self.positions.append(6)
			if seventh:
				self.positions.append(7)
			if eigth:
				self.positions.append(8)
		self.search_spondeus()
		
	def _search_fifth(self):
		eleventh = self._search_long(11)
		twelfth = self._search_long(12)
		if eleventh and twelfth:
			self.positions.append(11)
			self.positions.append(12)
			self._set_found()
		elif eleventh:
			self.positions.append(11)
		elif twelfth:
			self.positions.append(12)
		self.search_spondeus()

	def _make_scansion(self):
		for x in range(1,13):
			if x not in self.positions:
				self.questions.append(x)
		#nr. 30
		if 8 in self.questions and 9 in self.questions and 11 in self.questions and 12 in self.questions:
			self.verse.scansion = '-- -- -- -** -** -X'
			self._verify_output()
		#nr. 31
		elif 6 in self.questions and 7 in self.questions and 11 in self.questions and 12 in self.questions:
			self.verse.scansion = '-- -- -** -- -** -X'
			self._verify_output()
		#nr. 32
		elif 6 in self.questions and 7 in self.questions and 9 in self.questions and 10 in self.questions:
			self.verse.scansion = '-- -- -** -** -- -X'
			self._verify_output()
		#nr. 33
		elif 2 in self.questions and 3 in self.questions and 11 in self.questions and 12 in self.questions:
			self.verse.scansion = '-** -- -- -- -** -X'
			self._verify_output()
		#nr. 34
		elif 2 in self.questions and 3 in self.questions and 9 in self.questions and 10 in self.questions:
			self.verse.scansion = '-** -- -- -** -- -X'
			self._verify_output()
		#nr. 35
		elif 2 in self.questions and 3 in self.questions and 7 in self.questions and 8 in self.questions:
			self.verse.scansion = '-** -- -** -- -- -X'
			self._verify_output()
		#nr. 36
		elif 2 in self.questions and 3 in self.questions and 5 in self.questions and 6 in self.questions:
			self.verse.scansion = '-** -** -- -- -- -X'
			self._verify_output()
		#nr. 37
		elif 4 in self.questions and 5 in self.questions and 11 in self.questions and 12 in self.questions:
			self.verse.scansion = '-- -** -- -- -** -X'
			self._verify_output()
		#nr. 38
		elif 4 in self.questions and 5 in self.questions and 9 in self.questions and 10 in self.questions:
			self.verse.scansion = '-- -** -- -** -- -X'
			self._verify_output()
		#nr. 39
		elif 4 in self.questions and 5 in self.questions and 7 in self.questions and 8 in self.questions:
			self.verse.scansion = '-- -** -** -- -- -X'
			self._verify_output()
		else:
			self.search_spondeus()

	def _make_spondeus(self):
		annotator._make_spondeus(self, 12)

class HFSA15(annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF']}, 
	{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF', 'thirdF', 'fifthF']},
	{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
	{'name': 'found_two_spondees', 'on_enter': '_make_scansion'}, 
	{'name': 'fallback', 'on_enter': '_search_whole'},
	{'name': 'correction', 'on_enter': '_correct'},
	'success',
	'failure'
	]

	def __init__ (self, name):
		annotator.__init__(self, name)
		self.machine = Machine(model=self, states=HFSA15._states, initial='waiting')
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus_secondF', after='_search_second')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_first_spondeus_firstF', unless=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_second_spondeus_firstF', conditions=[self._found_first], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'found_two_spondees', conditions=[self._found_second])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'searching_for_second_spondeus_fourthF', unless=[self._found_second], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_first_spondeus_fourthF', unless=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_second_spondeus_fourthF', conditions=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'found_two_spondees', conditions=[self._found_second])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'searching_for_second_spondeus_thirdF', unless=[self._found_second], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_fourthF', 'searching_for_first_spondeus_thirdF', unless=[self._found_first], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_fourthF', 'searching_for_second_spondeus_thirdF', conditions=[self._found_first], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_thirdF', 'found_two_spondees', conditions=[self._found_second])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_thirdF', 'searching_for_second_spondeus_fifthF', unless=[self._found_second], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_thirdF', 'no_spondeus_found', unless=[self._found_first])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_thirdF', 'searching_for_second_spondeus_fifthF', conditions=[self._found_first], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fifthF', 'found_two_spondees', conditions=[self._found_second])
		#deal with implausible spondeus positions
		self.machine.add_transition('search_spondeus', 'found_two_spondees', 'no_spondeus_found')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fifthF', 'no_spondeus_found', unless=[self._found_second])
		self.machine.add_transition('not_found', 'no_spondeus_found', 'fallback')
		self.machine.add_transition('verified', 'fallback', 'correction', unless=[self._is_successful])
		self.machine.add_transition('verified', 'fallback', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_two_spondees', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_two_spondees', 'correction', unless=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'success', conditions=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'failure', unless=[self._is_successful])
		
	def _search_second(self):
		third = self._search_long(3)
		fourth = self._search_long(4)
		fifth = self._search_long(5)
		if third and fourth:
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif fourth and fifth:
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		else:
			if third:
				self.positions.append(3)
			if fourth:
				self.positions.append(4)
			if fifth:
				self.positions.append(5)
		self.search_spondeus()
		
	def _search_first(self):
		first = self._search_long(1)
		second = self._search_long(2)
		if first and second:
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif first:
			self.positions.append(1)
		elif second:
			self.positions.append(2)
		self.search_spondeus()
		
	def _search_fourth(self):
		ninth = self._search_long(9)
		tenth = self._search_long(10)
		eleventh = self._search_long(11)
		if tenth and eleventh:
			self.positions.append(10)
			self.positions.append(11)
			self._set_found()
		elif ninth and tenth:
			self.positions.append(9)
			self.positions.append(10)
			self._set_found()
		else:
			if ninth:
				self.positions.append(9)
			if tenth:
				self.positions.append(10)
			if eleventh:
				self.positions.append(11)
		self.search_spondeus()
		
	def _search_third(self):
		sixth = self._search_long(6)
		seventh = self._search_long(7)
		eigth = self._search_long(8)
		if seventh and eigth:
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif sixth and seventh:
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		else:
			if sixth:
				self.positions.append(6)
			if seventh:
				self.positions.append(7)
			if eigth:
				self.positions.append(8)
		self.search_spondeus()
		
	def _search_fifth(self):
		twelfth = self._search_long(12)
		thirteenth = self._search_long(13)
		if twelfth and thirteenth:
			self.positions.append(12)
			self.positions.append(13)
			self._set_found()
		elif twelfth:
			self.positions.append(12)
		elif thirteenth:
			self.positions.append(13)
		self.search_spondeus()
		
	def _make_scansion(self):
		if 2 in self.positions:
			self.verse.scansion = '-- '
			if 4 in self.positions:
				self.verse.scansion+= '-- -** -** -** -X'
				self._verify_output()
			elif 7 in self.positions:
				self.verse.scansion+= '-** -- -** -** -X'
				self._verify_output()
			elif 10 in self.positions:
				self.verse.scansion+= '-** -** -- -** -X'
				self._verify_output()
			elif 13 in self.positions:
				self.verse.scansion+= '-** -** -** -- -X'
				self._verify_output()
			else:
				self.search_spondeus()
		elif 5 in self.positions:
			self.verse.scansion = '-** -- '
			if 7 in self.positions:
				self.verse.scansion+= '-- -** -** -X'
				self._verify_output()
			elif 10 in self.positions:
				self.verse.scansion+= '-** -- -** -X'
				self._verify_output()
			elif 13 in self.positions:
				self.verse.scansion+= '-** -** -- -X'
				self._verify_output()
			else:
				self.search_spondeus()
		elif 8 in self.positions:
			self.verse.scansion = '-** -** -- '
			if 10 in self.positions:
				self.verse.scansion+= '-- -** -X'
				self._verify_output()
			elif 13 in self.positions:
				self.verse.scansion+= '-** -- -X'
				self._verify_output()
		elif 11 in self.positions:
			self.verse.scansion = '-** -** -** -- -- -X'
			self._verify_output()
		else:
			self.search_spondeus()
			
	def _make_spondeus(self):
		annotator._make_spondeus(self, 13)
			
class HFSA16(annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF', 'fifthF']},
	{'name': 'spondeus_found', 'on_enter': '_verify_output'},
	{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
	{'name': 'fallback', 'on_enter': '_search_whole'},
	{'name': 'correction', 'on_enter': '_correct'},
	'success',
	'failure'
	]
	
	def __init__(self, name):
		annotator.__init__(self, name)
		self.machine = Machine(model=self, states=HFSA16._states, initial='waiting')
		self.machine.add_transition(trigger='start_analysis', source='waiting', dest='searching_for_spondeus_secondF', after='_search_second')
		self.machine.add_transition('found_spondeus', 'searching_for_spondeus_secondF', 'spondeus_found')
		self.machine.add_transition('not_found', 'searching_for_spondeus_secondF', 'searching_for_spondeus_firstF', after='_search_first')
		self.machine.add_transition('found_spondeus', 'searching_for_spondeus_firstF', 'spondeus_found')
		self.machine.add_transition('not_found', 'searching_for_spondeus_firstF', 'searching_for_spondeus_fourthF', after='_search_fourth')
		self.machine.add_transition('found_spondeus', 'searching_for_spondeus_fourthF', 'spondeus_found')
		self.machine.add_transition('not_found', 'searching_for_spondeus_fourthF', 'searching_for_spondeus_thirdF', after='_search_third')
		self.machine.add_transition('found_spondeus', 'searching_for_spondeus_thirdF', 'spondeus_found')
		self.machine.add_transition('not_found', 'searching_for_spondeus_thirdF', 'searching_for_spondeus_fifthF', after='_search_fifth')
		self.machine.add_transition('found_spondeus', 'searching_for_spondeus_fifthF', 'spondeus_found')
		self.machine.add_transition('not_found', 'searching_for_spondeus_fifthF', 'no_spondeus_found')
		self.machine.add_transition('not_found', 'no_spondeus_found', 'fallback')
		self.machine.add_transition('verified', 'fallback', 'correction', unless=[self._is_successful])
		self.machine.add_transition('verified', 'fallback', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'spondeus_found', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'spondeus_found', 'correction', unless=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'success', conditions=[self._is_successful])
		self.machine.add_transition('corrected', 'correction', 'failure', unless=[self._is_successful])
	
	def _search_second(self):
		fourth = self._search_long(4)
		fifth = self._search_long(5)
		if fourth and fifth:
			self.verse.scansion = '-** -- -** -** -** -X'
			self.found_spondeus()
		elif fourth:
			self.positions.append(4)
			self.not_found()
		elif fifth:
			self.positions.append(5)
			self.not_found()
		else:
			self.not_found()
		
	def _search_first(self):
		if self._search_long(2):
			self.verse.scansion = '-- -** -** -** -** -X'
			self.found_spondeus()
		else:
			self.not_found()
			
	def _search_fourth(self):
		tenth = self._search_long(10)
		eleventh = self._search_long(11)
		if tenth and eleventh:
			self.verse.scansion = '-** -** -** -- -** -X'
			self.found_spondeus()
		elif tenth:
			self.positions.append(10)
			self.not_found()
		elif eleventh:
			self.positions.append(11)
			self.not_found()
		else:
			self.not_found()

	def _search_third(self):
		seventh = self._search_long(7)
		eigth = self._search_long(8)
		if seventh and eigth:
			self.verse.scansion = '-** -** -- -** -** -X'
			self.found_spondeus()
		elif seventh:
			self.positions.append(7)
			self.not_found()
		elif eigth:
			self.positions.append(8)
			self.not_found()
		else:
			self.not_found()
			
	def _search_fifth(self):
		thirteenth = self._search_long(13)
		fourteenth = self._search_long(14)
		if thirteenth and fourteenth:
			self.verse.scansion = '-** -** -** -** -- -X'
			self.found_spondeus()
		elif thirteenth:
			self.positions.append(13)
			self.not_found()
		elif fourteenth:
			self.positions.append(14)
			self.not_found()
		else:
			self.not_found()
			
	def _make_spondeus(self):
		annotator._make_spondeus(self, 14)