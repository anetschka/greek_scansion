import re
from transducer import fallbackTransducer
from transitions.extensions import HierarchicalMachine as Machine
from transitions.extensions.states import add_state_features, Tags
from preprocessing import preprocessor

#class containing linguistic rules
class ruleset(object):	
		
	#long by nature
	def rule_nl1(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'[ηω]', current) and re.search(r'[ηω]([αιουεωη][t]|[ςβγδθκλμνπρστφχξζψ]|[ηω])', current + following):
			return True
		
	#long by nature
	def rule_nl2(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)([αιουεωη][t]|[ςβγδθκλμνπρστφχξζψ])', current+following):
			return True
		
	#long by position
	def rule_pl(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'([αιουεωη][ςβγδθκλμνπρστφχξζψ]{2,}|[αιουεωη][ξζψ])', current+following):
			return True
		
	#muta cum liquida
	def rule_ml(self, text, position):
		current = text[position-1]
		following = text[position]
		if re.search(r'[αιουεωη][βγδπτκφχθ][λρνμ]', current+following):
			return True

	#circumflex
	def rule_zf(self, text, position):
		current = text[position-1]
		if re.search(r'z', current):
			return True

#class representing verse object; it makes verse, syllables, and scansion available at all times
class verse(object):

	def __init__(self):
		self.verse = ''
		self.syllables = ''
		self.scansion = ''
		self.correction = ''

	def clear(self):
		self.verse = ''
		self.syllables = ''
		self.scansion = ''
		self.correction = ''

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
		self.fallbackTransducer = fallbackTransducer()
		self.success = True
		self.synizesis = False
		self.scansionLength = 1
		self.correctionLength = 0
			
	def _reset_positions(self):		
		self.positions = []
		self.questions = []
		self.verse.clear()
		self.first_found = False
		self.second_found = False
		self.third_found = False
		self.fourth_found = False
		self.success = True
		self.synizesis = False
		self.scansionLength = 1
		self.correctionLength = 0

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
			
	#sets self.verse.scansion based on FSAs' output (after local search)
	def _make_spondeus(self, limit):
		self.verse.scansion = '-'
		for x in range(2, limit+1):
			if x in self.positions:
				self.verse.scansion+='-'
			else:
				self.verse.scansion+='?'
		self.verse.scansion+='-X'

	#function used to verify correctness of produced hexameter annotation
	def _verify_output(self):
		self.success = self._verify_string(self.verse.scansion)
		self.verified()

	def _verify_string(self, string):		
		s_units = list(filter(lambda s: re.match(r'[-\?\*]', s), string))
		for x in range(0, len(s_units)-2):
			if self._search_long(x+1) and s_units[x] == '*':
				return False
			elif s_units[x] == '?':
				return False
		return True

	#function used to search the whole verse for long syllables (for global search)
	#partially annotated string is completed by FST and verified
	def _search_whole(self):
		s_units = list(self.verse.scansion)
		for x in range(1, len(s_units)-2): #no need to scan last two syllabs
			if s_units[x] == '?':
				search_result = self._search_long(x+1)
				if search_result:
					s_units[x] = '-'
		self.verse.scansion = ''.join(s_units)
		#apply finite-state transducer
		results = self._apply_transducer()
		#failure if transducer does not accept input string
		if len(results.items()) == 0:
			self.success = False
			self.scansionLength = 0
		else:
			lengths = [len(v) for v in results.values()]
			self.scansionLength = lengths[0]
			self._set_transducerResult(results, mode='fallback')
		self.verified()

	#function used to correct faulty hexameter scheme: fallback to vowel-wise analysis
	#Then, the FST is called. If the FST fails, a simple regex tries to identify synizesis candidates
	#and calls this function again, recursively.
	def _correct(self):
		self._correct_string()
		results = self._apply_transducer(mode='correction')
		if len(results.items()) == 0:
			#check for synizesis
			if re.search(r'ε[ωαο]', self.verse.verse):
				self.verse.verse = re.sub(r'ε[ωαο]', 'ω', self.verse.verse)
				self.verse.syllables = re.split(r'[ \.]', preprocessor.papakitsos_syllabify(self, self.verse.verse))
				self.synizesis = True
				self._correct()
			#no synizesis or possible - analysis has eventually failed
			else:
				self.success = False
		else:
			lengths = [len(v) for v in results.values()]
			self.correctionLength = lengths[0]
			self._set_transducerResult(results, mode='correction')
		if self.state != 'finished' and self.state != 'failure':
			self.corrected()

	def _apply_transducer(self, mode = 'fallback'):
		if mode == 'fallback':
			line = self.verse.scansion
		else:
			line = self.verse.correction
		#actually, we can already make some very obvious corrections
		line = re.sub(r'-\?-', '---', line)
		line = re.sub(r'-\?\?-X', '-**-X', line)
		line = re.sub(r'-\?-X', '---X', line)
		line = re.sub(r'-\?\?-\?X', '-**-X', line)
		return self.fallbackTransducer.apply(line).extract_paths(output='dict')

	def _set_transducerResult(self, results, mode = 'fallback'):
		for input, outputs in results.items():
				i = len(outputs)-1
				while(i >= 0):
					data = outputs[i]
					if self._verify_string(data[0]) and mode == 'fallback':
						self.verse.scansion = data[0]
						break
					elif mode == 'correction':
						self.verse.correction = data[0]
					i -= 1
					if i == -1:
						self.success = False

	#this function assigns length vowel by vowel if all other processing before has failed
	def _correct_string(self):
		diphtongs = ['υι', 'ει', 'αυ', 'ευ', 'ου', 'ηι', 'ωι', 'ηυ']
		vowels = ['α', 'ι', 'ο', 'υ', 'ε', 'η','ω']
		consonants = ['ς', 'β', 'γ', 'δ', 'θ', 'κ', 'λ', 'μ', 'ν', 'π', 'ρ', 'σ', 'τ', 'φ', 'χ', 'ξ', 'ζ', 'ψ']
		letters = list(''.join(self.verse.syllables))
		self.verse.correction = ''
		for x in range(0, len(letters)):
			if letters[x] in vowels:
				if x == len(letters)-1:
					self.verse.correction += 'X'
				elif x < len(letters)-1 and letters[x+1] == 'z':
					self.verse.correction += '-'
					continue
				elif (letters[x] == 'η' or letters[x] == 'ω') :					
					if (x < len(letters)-1 and (letters[x+1] not in vowels or letters[x+1] in ['η', 'ω'])):
						self.verse.correction += '-'
					elif x < len(letters)-1 and letters[x+1] in vowels:
						if x < len(letters)-2 and letters[x+2] == 't':
							self.verse.correction += '-'
						else:
							self.verse.correction += '?'
					else:
						self.verse.correction += '-'
					continue
				elif x > 0 and (letters[x-1] + letters[x] in diphtongs):
					if x < len(letters)-1 and letters[x+1] == 't':
						self.verse.correction += '?'
					else:
						self.verse.correction += '-'
					continue
				elif x < len(letters)-2 and letters[x+1] in consonants and letters[x+2] in consonants and not re.match(r'[βγδπτκφχθ][λρνμ]', letters[x+1] + letters[x+2]):
					self.verse.correction += '-'
					continue
				elif x < len(letters)-1 and letters[x+1] in ['ξ', 'ζ', 'ψ']:
					self.verse.correction += '-'
					continue
				elif x < len(letters)-1 and (letters[x] + letters[x+1] not in diphtongs and letters[x] + letters[x+1] not in ['αι', 'οι']):
					self.verse.correction += '?'

	#this function is called by the FSAs for finding long syllables (in local search)
	def _search_long(self, position):
		if self.rules.rule_zf(self.verse.syllables, position):
			return True
		elif self.rules.rule_nl1(self.verse.syllables, position):
			return True
		elif self.rules.rule_nl2(self.verse.syllables, position):
			return True
		elif self.rules.rule_pl(self.verse.syllables, position) and not self.rules.rule_ml(self.verse.syllables, position):
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
		self.machine.add_transition('verified', 'found_four_spondees', 'success', conditions=[self._is_successful])
		self.machine.add_transition('verified', 'found_four_spondees', 'correction', unless=[self._is_successful])
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
			else:
				self.search_spondeus()
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

class SimpleFSA(annotator):
	
	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'analysing'},
	{'name': 'finished'}
	]

	def __init__(self, name):
		annotator.__init__(self, name)
		self.machine = Machine(model=self, states=SimpleFSA._states, initial='waiting')
		self.machine.add_transition(trigger='start_analysis', source='waiting', dest='analysing', after='_analyse')
		self.machine.add_transition('corrected', 'analysing', 'finished')

	def verify(self, line):
		return annotator._verify_string(self, line)
	
	def _analyse(self):
		annotator._correct(self)