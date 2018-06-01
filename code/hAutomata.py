import re
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
		next = text[position]
		if re.match(r'^(αι|οι|υι|ει|αυ|ευ|ου|ηι|ωι|ηυ)', next):
			return True
		
	#long by position
	def rule4(self, text, position):
		next = text[position]
		if re.match(r'([ςβγδθκλμνπρστφχξζψ]{2,*}|[ξζψ])', next):
			return True
		
	#muta cum liquida
	def muta(self, text, position):
		next = text[position]
		if re.match(r'[βγδπτκφχθ][λρνμ]', next):
			return True
		
	#hiat
	def hiat(self, text, position):
		current = text[position-1]
		next = text[position]
		if re.search(r'[αιουεωη]{1,*}', current) and re.match(r'[αιουεωη]{1,*}', next):
			return True

#superclass encapsulating basic functionality
class Annotator(object):

	def __init__(self, name):
		self.name = name
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
		self.positions = []
		self.questions = []
		self.first_found = False
		self.second_found = False
		self.third_found = False
		self.fourth_found = False
			
	def _reset_positions(self):		
		self.positions = []
		self.questions = []
		self.scansion = ''
		self.first_found = False
		self.second_found = False
		self.third_found = False
		self.fourth_found = False
		
	def set_text(self, text):
		self.text = text
			
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
		if self.first_found:
			return True
		else:
			return False
		
	def _found_second(self):
		if self.second_found:
			return True
		else:
			return False

	def _found_third(self):
		if self.third_found:
			return True
		else:
			return False

	def _found_fourth(self):
		if self.fourth_found:
			return True
		else:
			return False
			
	def _make_daktyle(self, limit):
		self.scansion = '-'
		for x in range(2, limit+1):
			if x in self.positions:
				self.scansion+='*'
			elif x in self.questions:
				self.scansion+='?'
			else:
				self.scansion+='-'
		self.scansion+='-X'
		
	def _make_spondeus(self, limit):
		self.scansion = '-'
		for x in range(2, limit+1):
			if x in self.positions:
				self.scansion+='-'
			else:
				self.scansion+='?'
		self.scansion+='-X'
		
	def _search_short(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
			
	def _search_long(self, position):
		if self.rules.rule1(self.text, position) or self.rules.rule2(self.text, position) or self.rules.rule3(self.text, position) or self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True

class HFSA13(Annotator):

	_states = [
		{'name': 'waiting', 'on_enter': '_reset_positions'},
		{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF']},
		{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF']},
		{'name': 'searching_for_third_spondeus', 'children': ['fourthF', 'thirdF']},
		{'name': 'searching_for_fourth_spondeus', 'children': ['thirdF', 'fifthF']},
		{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
		{'name': 'found_four_spondees', 'on_enter': '_make_scansion'},
		'fallback'
	]

	def __init__(self, name):
		Annotator.__init__(self, name)
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

	def _search_second(self):
		if self._search_long(3) and self._search_long(4):
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif self._search_long(4) and self._search_long(5):
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		elif self._search_long(3):
			self.positions.append(3)
		elif self._search_long(4):
			self.positions.append(4)
		elif self._search_long(5):
			self.positions.append(5)
		self.search_spondeus()

	def _search_first(self):
		if self._search_long(1) and self._search_long(2):
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif self._search_long(1):
			self.positions.append(1)
		elif self._search_long(2):
			self.positions.append(2)
		self.search_spondeus()

	def _search_fourth(self):
		if self._search_long(7) and self._search_long(8):
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif self._search_long(8) and self._search_long(9):
			self.positions.append(8)
			self.positions.append(9)
			self._set_found()
		elif self._search_long(7):
			self.positions.append(7)
		elif self._search_long(8):
			self.positions.append(8)
		elif self._search_long(9):
			self.positions.append(9)
		self.search_spondeus()

	def _search_third(self):
		if self._search_long(5) and self._search_long(6):
			self.positions.append(5)
			self.positions.append(6)
			self._set_found()
		elif self._search_long(6) and self._search_long(7):
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		elif self._search_long(6):
			self.positions.append(6)
		elif self._search_long(7):
			self.positions.append(7)
		elif self._search_long(5):
			self.positions.append(5)
		self.search_spondeus()

	def _search_fifth(self):
		if self._search_long(10) and self._search_long(11):
			self.positions.append(10)
			self.positions.append(11)
			self._set_found()
		elif self._search_long(10):
			self.positions.append(10)
		elif self._search_long(11):
			self.positions.append(11)
		self.search_spondeus()

	def _make_scansion(self):
		for x in range(1,12):
			if x not in self.positions:
				self.questions.append(x)
		#nr. 40
		if 10 in self.questions and 11 in self.questions:
			self.scansion = '-- -- -- -- -** -X'
		#nr. 41
		elif 8 in self.questions and 9 in self.questions:
			self.scansion = '-- -- -- -** -- -X'
		#nr. 42
		elif 6 in self.questions and 7 in self.questions:
			self.scansion = '-- -- -** -- -- -X'
		#nr. 43
		elif 4 in self.questions and 5 in self.questions:
			self.scansion = '-- -** -- -- -- -X'
		#nr. 44
		elif 2 in self.questions and 3 in self.questions:
			self.scansion = '-** -- -- -- -- -X'
		else:
			self.search_spondeus()


	def _make_spondeus(self):
		Annotator._make_spondeus(self, 11)

class HFSA14(Annotator):

	_states = [
		{'name': 'waiting', 'on_enter': '_reset_positions'},
		{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF', 'fourthF']},
		{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF', 'thirdF']},
		{'name': 'searching_for_third_spondeus', 'children': ['fourthF', 'thirdF', 'fifthF']},
		{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
		{'name': 'found_three_spondees', 'on_enter': '_make_scansion'},
		'fallback'
	]

	def __init__ (self, name):
		Annotator.__init__(self, name)
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

	def _search_second(self):
		if self._search_long(3) and self._search_long(4):
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif self._search_long(4) and self._search_long(5):
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		elif self._search_long(3):
			self.positions.append(3)
		elif self._search_long(4):
			self.positions.append(4)
		elif self._search_long(5):
			self.positions.append(5)
		self.search_spondeus()

	def _search_first(self):
		if self._search_long(1) and self._search_long(2):
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif self._search_long(1):
			self.positions.append(1)
		elif self._search_long(2):
			self.positions.append(2)
		self.search_spondeus()
		
	def _search_fourth(self):
		if self._search_long(8) and self._search_long(9):
			self.positions.append(8)
			self.positions.append(9)
			self._set_found()
		elif self._search_long(9) and self._search_long(10):
			self.positions.append(9)
			self.positions.append(10)
			self._set_found()
		elif self._search_long(8):
			self.positions.append(8)
		elif self._search_long(9):
			self.positions.append(9)
		elif self._search_long(10):
			self.positions.append(10)
		self.search_spondeus()
		
	def _search_third(self):
		if self._search_long(7) and self._search_long(8):
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif self._search_long(6) and self._search_long(7):
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		elif self._search_long(6):
			self.positions.append(6)
		elif self._search_long(7):
			self.positions.append(7)
		elif self._search_long(8):
			self.positions.append(8)
		self.search_spondeus()
		
	def _search_fifth(self):
		if self._search_long(11) and self._search_long(12):
			self.positions.append(11)
			self.positions.append(12)
			self._set_found()
		elif self._search_long(11):
			self.positions.append(11)
		elif self._search_long(12):
			self.positions.append(12)
		self.search_spondeus()

	def _make_scansion(self):
		for x in range(1,13):
			if x not in self.positions:
				self.questions.append(x)
		#nr. 30
		if 8 in self.questions and 9 in self.questions and 11 in self.questions and 12 in self.questions:
			self.scansion = '-- -- -- -** -** -X'
		#nr. 31
		elif 6 in self.questions and 7 in self.questions and 11 in self.questions and 12 in self.questions:
			self.scansion = '-- -- -** -- -** -X'
		#nr. 32
		elif 6 in self.questions and 7 in self.questions and 9 in self.questions and 10 in self.questions:
			self.scansion = '-- -- -** -** -- -X'
		#nr. 33
		elif 2 in self.questions and 3 in self.questions and 11 in self.questions and 12 in self.questions:
			self.scansion = '-** -- -- -- -** -X'
		#nr. 34
		elif 2 in self.questions and 3 in self.questions and 9 in self.questions and 10 in self.questions:
			self.scansion = '-** -- -- -** -- -X'
		#nr. 35
		elif 2 in self.questions and 3 in self.questions and 7 in self.questions and 8 in self.questions:
			self.scansion = '-** -- -** -- -- -X'
		#nr. 36
		elif 2 in self.questions and 3 in self.questions and 5 in self.questions and 6 in self.questions:
			self.scansion = '-** -** -- -- -- -X'
		#nr. 37
		elif 4 in self.questions and 5 in self.questions and 11 in self.questions and 12 in self.questions:
			self.scansion = '-- -** -- -- -** -X'
		#nr. 38
		elif 4 in self.questions and 5 in self.questions and 9 in self.questions and 10 in self.questions:
			self.scansion = '-- -** -- -** -- -X'
		#nr. 39
		elif 4 in self.questions and 5 in self.questions and 7 in self.questions and 8 in self.questions:
			self.scansion = '-- -** -** -- -- -X'
		else:
			self.search_spondeus()

	def _make_spondeus(self):
		Annotator._make_spondeus(self, 12)

class HFSA15(Annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF']}, 
	{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF', 'thirdF', 'fifthF']},
	{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
	{'name': 'found_two_spondees', 'on_enter': '_make_scansion'}, 
	'fallback'
	]

	def __init__ (self, name):
		Annotator.__init__(self, name)
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
		
	def _search_second(self):
		if self._search_long(3) and self._search_long(4):
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif self._search_long(4) and self._search_long(5):
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		elif self._search_long(3):
			self.positions.append(3)
		elif self._search_long(4):
			self.positions.append(4)
		elif self._search_long(5):
			self.positions.append(5)
		self.search_spondeus()
		
	def _search_first(self):
		if self._search_long(1) and self._search_long(2):
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif self._search_long(1):
			self.positions.append(1)
		elif self._search_long(2):
			self.positions.append(2)
		self.search_spondeus()
		
	def _search_fourth(self):
		if self._search_long(10) and self._search_long(11):
			self.positions.append(10)
			self.positions.append(11)
			self._set_found()
		elif self._search_long(9) and self._search_long(10):
			self.positions.append(9)
			self.positions.append(10)
			self._set_found()
		elif self._search_long(9):
			self.positions.append(9)
		elif self._search_long(10):
			self.positions.append(10)
		elif self._search_long(11):
			self.positions.append(11)
		self.search_spondeus()
		
	def _search_third(self):
		if self._search_long(7) and self._search_long(8):
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif self._search_long(6) and self._search_long(7):
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		elif self._search_long(6):
			self.positions.append(6)
		elif self._search_long(7):
			self.positions.append(7)
		elif self._search_long(8):
			self.positions.append(8)
		self.search_spondeus()
		
	def _search_fifth(self):
		if self._search_long(12) and self._search_long(13):
			self.positions.append(12)
			self.positions.append(13)
			self._set_found()
		elif self._search_long(12):
			self.positions.append(12)
		elif self._search_long(13):
			self.positions.append(13)
		self.search_spondeus()
		
	def _make_scansion(self):
		if 2 in self.positions:
			self.scansion = '-- '
			if 4 in self.positions:
				self.scansion+= '-- -** -** -** -X'
			elif 7 in self.positions:
				self.scansion+= '-** -- -** -** -X'
			elif 10 in self.positions:
				self.scansion+= '-** -** -- -** -X'
			elif 13 in self.positions:
				self.scansion+= '-** -** -** -- -X'
			else:
				self.search_spondeus()
		elif 5 in self.positions:
			self.scansion = '-** -- '
			if 7 in self.positions:
				self.scansion+= '-- -** -** -X'
			elif 10 in self.positions:
				self.scansion+= '-** -- -** -X'
			elif 13 in self.positions:
				self.scansion+= '-** -** -- -X'
			else:
				self.search_spondeus()
		elif 8 in self.positions:
			self.scansion = '-** -** -- '
			if 10 in self.positions:
				self.scansion+= '-- -** -X'
			elif 13 in self.positions:
				self.scansion+= '-** -- -X'
		elif 11 in self.positions:
			self.scansion = '-** -** -** -- -- -X'
		else:
			self.search_spondeus()
			
	def _make_spondeus(self):
		Annotator._make_spondeus(self, 13)
			
class HFSA16(Annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF', 'fifthF']},
	{'name': 'spondeus_found'},
	{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
	'fallback'
	]
	
	def __init__(self, name):
		Annotator.__init__(self, name)
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
	
	def _search_second(self):
		if self._search_long(4) and self._search_long(5):
			self.scansion = '-** -- -** -** -** -X'
			self.found_spondeus()
		elif self._search_long(4):
			self.positions.append(4)
			self.not_found()
		elif self._search_long(5):
			self.positions.append(5)
			self.not_found()
		else:
			self.not_found()
		
	def _search_first(self):
		if self._search_long(2):
			self.scansion = '-- -** -** -** -** -X'
			self.found_spondeus()
		else:
			self.not_found()
			
	def _search_fourth(self):
		if self._search_long(10) and self._search_long(11):
			self.scansion = '-** -** -** -- -** -X'
			self.found_spondeus()
		elif self._search_long(10):
			self.positions.append(10)
			self.not_found()
		elif self._search_long(11):
			self.positions.append(11)
			self.not_found()
		else:
			self.not_found()
			
	def _search_third(self):
		if self._search_long(7) and self._search_long(8):
			self.scansion = '-** -** -- -** -** -X'
			self.found_spondeus()
		elif self._search_long(7):
			self.positions.append(7)
			self.not_found()
		elif self._search_long(8):
			self.positions.append(8)
			self.not_found()
		else:
			self.not_found()
			
	def _search_fifth(self):
		if self._search_long(13) and self._search_long(14):
			self.scansion = '-** -** -** -** -- -X'
			self.found_spondeus()
		elif self._search_long(13):
			self.positions.append(13)
			self.not_found()
		elif self._search_long(14):
			self.positions.append(14)
			self.not_found()
		else:
			self.not_found()
			
	def _make_spondeus(self):
		Annotator._make_spondeus(self, 14)