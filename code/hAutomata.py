import re
from transitions.extensions import HierarchicalMachine as Machine
from transitions.extensions.states import add_state_features, Tags

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
			
	def _reset_positions(self):		
		self.positions = []
		self.questions = []
		self.scansion = ''
		self.first_found = False
		self.second_found = False
		
	def set_text(self, text):
		self.text = text
			
	def _set_found(self):
		if self.first_found == True:
			self.second_found = True
		else:
			self.first_found = True
			
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
			
#hierarchical FSAs governing the application of rules
@add_state_features(Tags)
class CustomStateMachine(Machine):
	pass

	
#TODO: handling of implausible annotations (else bei make_scansion)	
#TODO: remove customstatemachine
#TODO: überprüfung aller silben, die nicht geprüft wurden (oder nur im fallback?)
	
class HFSA13(Annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_daktylus', 'children': ['fifthF', 'thirdF', 'fourthF', 'firstF', 'secondF']},
	{'name': 'daktylus_found', 'tags': 'accepted'},
	{'name': 'no_daktylus_found', 'on_enter': '_make_daktyle'},
	'fallback'
	]
	
	def __init__(self, name):
		Annotator.__init__(self, name)
		
		self.machine = CustomStateMachine(model=self, states=HFSA13._states, initial='waiting')
		
		self.machine.add_transition(trigger='start_analysis', source='waiting', dest='searching_for_daktylus_fifthF', after='_search_fifth')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus_fifthF', 'daktylus_found')
		self.machine.add_transition('not_found', 'searching_for_daktylus_fifthF', 'searching_for_daktylus_thirdF', after='_search_third')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus_thirdF', 'daktylus_found')
		self.machine.add_transition('not_found', 'searching_for_daktylus_thirdF', 'searching_for_daktylus_fourthF', after='_search_fourth')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus_fourthF', 'daktylus_found')
		self.machine.add_transition('not_found', 'searching_for_daktylus_fourthF', 'searching_for_daktylus_firstF', after='_search_first')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus_firstF', 'daktylus_found')
		self.machine.add_transition('not_found', 'searching_for_daktylus_firstF', 'searching_for_daktylus_secondF', after='_search_second')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus_secondF', 'daktylus_found')
		self.machine.add_transition('not_found', 'searching_for_daktylus_secondF', 'no_daktylus_found')
		self.machine.add_transition('not_found', 'no_daktylus_found', 'fallback')
		
		
	def _search_fifth(self):
		if self._search(10) and self._search(11):
			self.scansion = '-- -- -- -- -** -X'
			self.found_daktylus()
		elif self._search(10):
			self.positions.append(10)
			self.questions.append(11)
			self.not_found()
		elif self._search(11):
			self.positions.append(11)
			self.questions.append(10)
			self.not_found()
		else:
			self.not_found()
		
	def _search_third(self):
		if self._search(6) and self._search(7):
			self.scansion = '-- -- -** -- -- -X'
			self.found_daktylus()
		elif self._search(6):
			self.positions.append(6)
			self.questions.append(7)
			self.not_found()
		elif self._search(7):
			self.positions.append(7)
			self.questions.append(6)
			self.not_found()
		else:
			self.not_found()
	
	def _search_fourth(self):
		if self._search(8) and self._search(9):
			self.scansion = '-- -- -- -** -- -X'
			self.found_daktylus()
		elif self._search(8):
			self.positions.append(8)
			self.questions.append(9)
			self.not_found()
		elif self._search(9):
			self.positions.append(9)
			self.questions.append(8)
			self.not_found()
		else:
			self.not_found()
	
	def _search_first(self):
		if self._search(2) and self._search(3):
			self.scansion = '-** -- -- -- -- -X'
			self.found_daktylus()
		elif self._search(2):
			self.positions.append(2)
			self.questions.append(3)
			self.not_found()
		elif self_search(3):
			self.positions.append(3)
			self.questions.append(2)
			self.not_found()
		else:
			self.not_found()
		
	def _search_second(self):
		if self._search(4) and self._search(5):
			self.scansion = '-- -** -- -- -- -X'
			self.found_daktylus()
		elif self._search(4):
			self.positions.append(4)
			self.questions.append(5)
			self.not_found()
		elif self._search(5):
			self.positions.append(5)
			self.questions.append(4)
			self.not_found()
		else:
			self.not_found()
		
	def _make_daktyle(self):
		Annotator._make_daktyle(self, 11)
	
	def _search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
	
class HFSA14(Annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_first_daktylus', 'children': ['fifthF', 'thirdF', 'fourthF', 'firstF']}, 
	{'name': 'searching_for_second_daktylus', 'children': ['thirdF', 'fourthF', 'firstF', 'secondF']}, 
	{'name': 'no_daktylus_found', 'on_enter': '_make_daktyle'},
	{'name': 'found_two_daktyles', 'on_enter': '_make_scansion', 'tags': 'accepted'}, 
	'fallback'
	]
	
	def __init__(self, name):
		Annotator.__init__(self, name)
		self.machine = CustomStateMachine(model=self, states=HFSA14._states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_daktylus_fifthF', after='_search_fifth')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fifthF', 'searching_for_first_daktylus_thirdF', unless=[self._found_first], after='_search_third')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fifthF', 'searching_for_second_daktylus_thirdF', conditions=[self._found_first], after='_search_third')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_thirdF', 'found_two_daktyles', conditions=[self._found_second])
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_thirdF', 'searching_for_second_daktylus_fourthF', unless=[self._found_second], after='_search_fourth') 
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_fourthF', 'searching_for_second_daktylus_firstF', unless=[self._found_second], after='_search_first')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_firstF', 'found_two_daktyles', conditions=[self._found_second])
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_firstF', 'searching_for_second_daktylus_secondF', unless=[self._found_second], after='_search_second')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_thirdF', 'searching_for_first_daktylus_fourthF', unless=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_thirdF', 'searching_for_second_daktylus_fourthF', conditions=[self._found_first], after='_search_fourth')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_fourthF', 'found_two_daktyles', conditions=[self._found_second])	
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fourthF', 'searching_for_first_daktylus_firstF', unless=[self._found_first], after='_search_first')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fourthF', 'searching_for_second_daktylus_firstF', conditions=[self._found_first], after='_search_first')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_firstF', 'no_daktylus_found', unless=[self._found_first])
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_firstF', 'searching_for_second_daktylus_secondF', conditions=[self._found_first], after='_search_second')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_secondF', 'found_two_daktyles', conditions=[self._found_second])
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_secondF', 'no_daktylus_found', unless=[self._found_second])
		self.machine.add_transition('not_found', 'no_daktylus_found', 'fallback')

	def _search_fifth(self):
		#search through a range of syllables, returning true only for safe cases
		if self._search(11) and self._search(12):
			self.positions.append(11)
			self.positions.append(12)
			self._set_found()
		elif self._search(11):
			self.positions.append(11)
			self.questions.append(12)
		elif self._search(12):
			self.positions.append(12)
			self.questions.append(11)
		self.search_daktylus()
		
	def _search_third(self):
		if (self._search(6) and self._search(7)):
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		elif (self._search(7) and self._search(8)):
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif self._search(6):
			self.positions.append(6)
			self.questions.append(7)
		elif self._search(7):
			self.positions.append(7)
			self.questions.append(6)
			self.questions.append(8)
		elif self._search(8):
			self.positions.append(8)
			self.questions.append(7)
		self.search_daktylus()
	
	def _search_fourth(self):
		if (self._search(8) and self._search(9)):
			self.positions.append(8)
			self.positions.append(9)
			self._set_found()
		elif (self._search(9) and self._search(10)):
			self.positions.append(9)
			self.positions.append(10)
			self._set_found()
		elif self._search(8):
			self.positions.append(8)
			self.questions.append(9)
		elif self._search(9):
			self.positions.append(9)
			self.questions.append(10)
			self.questions.append(8)
		elif self._search(10):
			self.positions.append(10)
			self.questions.append(9)
		self.search_daktylus()
	
	def _search_first(self):
		if self._search(2) and self._search(3):
			self.positions.append(2)
			self.positions.append(3)
			self._set_found()
		elif self._search(2):
			self.positions.append(2)
			self.questions.append(3)
			self._set_found()
		elif self._search(3):
			self.positions.append(3)
			self.questions.append(2)
		self.search_daktylus()
		
	def _search_second(self):
		if (self._search(4) and self._search(5)):
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		elif (self._search(5) and self._search(6)):
			self.positions.append(5)
			self.positions.append(6)
			self._set_found()
		elif self._search(4):
			self.positions.append(4)
			self.questions.append(5)
		elif self._search(5):
			self.positions.append(5)
			self.questions.append(4)
			self.questions.append(6)
		elif self._search(6):
			self.positions.append(6)
			self.questions(5)
		self.search_daktylus()
	
	def _make_scansion(self):
		if 2 in self.positions:
			self.scansion = '-** '
			if 5 in self.positions:
				self.scansion+='-** -- -- -- -X'
				return
			elif 7 in self.positions:
				self.scansion+='-- -** -- -- -X'
				return				
			elif 9 in self.positions:
				self.scansion+='-- -- -** -- -X'
				return
			elif 11 in self.positions:
				self.scansion+='-- -- -- -** -X'
				return
		elif 4 in self.positions:
			self.scansion = '-- -** '
			if 7 in self.positions:
				self.scansion+='-** -- -- -X'
				return				
			elif 9 in self.positions:
				self.scansion+='-- -** -- -X'
				return
			elif 11 in self.positions:
				self.scansion+='-- -- -** -X'
				return
		elif 6 in self.positions:
			self.scansion = '-- -- -** '
			if 9 in self.positions:
				self.scansion+='-** -- -X'
				return
			elif 11 in self.positions:
				self.scansion+='-- -** -X'
				return
		elif 8 in self.positions:
			self.scansion = '-- -- -- -** -** -X'
			
	def _make_daktyle(self):
		Annotator._make_daktyle(self, 12)
		
	def _search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True

class HFSA15(Annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF']}, 
	{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF', 'thirdF', 'fifthF']}, 
	{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
	{'name': 'found_two_spondees', 'on_enter': '_make_scansion', 'tags': 'accepted'}, 
	'fallback'
	]
	
	def __init__ (self, name):
		Annotator.__init__(self, name)
		self.machine = CustomStateMachine(model=self, states=HFSA15._states, initial='waiting')
		
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
		if self._search(3) and self._search(4):
			self.positions.append(3)
			self.positions.append(4)
			self._set_found()
		elif self._search(4) and self._search(5):
			self.positions.append(4)
			self.positions.append(5)
			self._set_found()
		elif self._search(3):
			self.positions.append(3)
		elif self._search(4):
			self.positions.append(4)
		elif self._search(5):
			self.positions.append(5)
		self.search_spondeus()
		
	def _search_first(self):
		if self._search(1) and self._search(2):
			self.positions.append(1)
			self.positions.append(2)
			self._set_found()
		elif self._search(1):
			self.positions.append(1)
		elif self._search(2):
			self.positions.append(2)
		self.search_spondeus()
		
	def _search_fourth(self):
		if self._search(10) and self._search(11):
			self.positions.append(10)
			self.positions.append(11)
			self._set_found()
		elif self._search(9) and self._search(10):
			self.positions.append(9)
			self.positions.append(10)
			self._set_found()
		elif self._search(9):
			self.positions.append(9)
		elif self._search(10):
			self.positions.append(10)
		elif self._search(11):
			self.positions.append(11)
		self.search_spondeus()
		
	def _search_third(self):
		if self._search(7) and self._search(8):
			self.positions.append(7)
			self.positions.append(8)
			self._set_found()
		elif self._search(6) and self._search(7):
			self.positions.append(6)
			self.positions.append(7)
			self._set_found()
		elif self._search(6):
			self.positions.append(6)
		elif self._search(7):
			self.positions.append(7)
		elif self._search(8):
			self.positions.append(8)
			self._set_found()
		self.search_spondeus()
		
	def _search_fifth(self):
		if self._search(12) and self._search(13):
			self.positions.append(12)
			self.positions.append(13)
			self._set_found()
		elif self._search(12):
			self.positions.append(12)
		elif self._search(13):
			self.positions.append(13)
		self.search_spondeus()
		
	def _make_scansion(self):
		if 2 in self.positions:
			self.scansion = '-- '
			if 4 in self.positions:
				self.scansion+= '-- -** -** -** -X'
				return
			elif 7 in self.positions:
				self.scansion+= '-** -- -** -** -X'
				return
			elif 10 in self.positions:
				self.scansion+= '-** -** -- -** -X'
				return
			elif 13 in self.positions:
				self.scansion+= '-** -** -** -- -X'
		elif 5 in self.positions:
			self.scansion = '-** -- '
			if 7 in self.positions:
				self.scansion+= '-- -** -** -X'
				return
			elif 10 in self.positions:
				self.scansion+= '-** -- -** -X'
				return
			elif 13 in self.positions:
				self.scansion+= '-** -** -- -X'
				return
		elif 8 in self.positions:
			self.scansion = '-** -** -- '
			if 10 in self.positions:
				self.scansion+= '-- -** -X'
				return
			elif 13 in self.positions:
				self.scansion+= '-** -- -X'
				return
		elif 11 in self.positions:
			self.scansion = '-** -** -** -- -- -X'
		else:
			self.search_spondeus()
			
	def _make_spondeus(self):
		Annotator._make_spondeus(self, 13)
			
	def _search(self, position):
		if self.rules.rule1(self.text, position) or self.rules.rule2(self.text, position) or self.rules.rule3(self.text, position) or self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
			
class HFSA16(Annotator):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF', 'fifthF']},
	{'name': 'spondeus_found', 'tags': 'accepted'},
	{'name': 'no_spondeus_found', 'on_enter': '_make_spondeus'},
	'fallback'
	]
	
	def __init__(self, name):
		Annotator.__init__(self, name)
		self.machine = CustomStateMachine(model=self, states=HFSA16._states, initial='waiting')
		
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
		if self._search(4) and self._search(5):
			self.scansion = '-** -- -** -** -** -X'
			self.found_spondeus()
		elif self._search(4):
			self.positions.append(4)
			self.not_found()
		elif self._search(5):
			self.positions.append(5)
			self.not_found()
		else:
			self.not_found()
		
	def _search_first(self):
		if self._search(2):
			self.scansion = '-- -** -** -** -** -X'
			self.found_spondeus()
		else:
			self.not_found()
			
	def _search_fourth(self):
		if self._search(10) and self._search(11):
			self.scansion = '-** -** -** -- -** -X'
			self.found_spondeus()
		elif self._search(10):
			self.positions.append(10)
			self.not_found()
		elif self._search(11):
			self.positions.append(11)
			self.not_found()
		else:
			self.not_found()
			
	def _search_third(self):
		if self._search(7) and self._search(8):
			self.scansion = '-** -** -- -** -** -X'
			self.found_spondeus()
		elif self._search(7):
			self.positions.append(7)
			self.not_found()
		elif self._search(8):
			self.positions.append(8)
			self.not_found()
		else:
			self.not_found()
			
	def _search_fifth(self):
		if self._search(13) and self._search(14):
			self.scansion = '-** -** -** -** -- -X'
			self.found_spondeus()
		elif self._search(13):
			self.positions.append(13)
			self.not_found()
		elif self._search(14):
			self.positions.append(14)
			self.not_found()
		else:
			self.not_found()
			
	def _make_spondeus(self):
		Annotator._make_spondeus(self, 14)
		
	def _search(self, position):
		if self.rules.rule1(self.text, position) or self.rules.rule2(self.text, position) or self.rules.rule3(self.text, position) or self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
		