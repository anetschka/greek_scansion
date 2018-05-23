import re
from transitions import Machine
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

#FSAs governing the application of rules
@add_state_features(Tags)
class CustomStateMachine(Machine):
	pass
	
class FSA13(object):

	_states = ['waiting', {'name': 'searching_for_daktylus', 'on_enter': '_search_daktylus'}, {'name': 'daktylus_found', 'tags': 'accepted'}, 'daktylus_not_found', 'fallback']
	
	def __init__(self, name):
		#name of the FSA
		self.name = name
		self.rules = ruleset()
		#text to be analyed
		self.text = ''
		#resulting scansion
		self.scansion = ''
		#initialisation
		self.machine = CustomStateMachine(model=self, states=FSA13._states, initial='waiting')
		
		#transitions
		self.machine.add_transition(trigger='start_analysis', source='waiting', dest='searching_for_daktylus')
		self.machine.add_transition('found_daktylus', 'searching_for_daktylus', 'daktylus_found')
		self.machine.add_transition('no_daktylus_found', 'searching_for_daktylus', 'daktylus_not_found')
		self.machine.add_transition('not_found', 'daktylus_not_found', 'fallback')
			
	def _search_daktylus(self):
		if self._search(10):
			self.scansion = '-- -- -- -- -** -X'
			#solution found, don't continue iteration
			self.found_daktylus()
		elif self._search(6):
			self.scansion = '-- -- -** -- -- -X'
			self.found_daktylus()
		elif self._search(8):
			self.scansion = '-- -- -- -** -- -X'
			self.found_daktylus()
		elif self._search(2):
			self.scansion = '-** -- -- -- -- -X'
			self.found_daktylus()
		elif self._search(4):
			self.scansion = '-- -** -- -- -- -X'
			self.found_daktylus()
		else:
			self.no_daktylus_found()
	
	def set_text(self, text):
		self.text = text
		
	def _search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
	
class FSA14(object):

	_states = [{'name': 'waiting', 'on_enter': '_reset_positions'}, {'name': 'searching_for_first_daktylus', 'on_enter': '_search_first'}, {'name': 'searching_for_second_daktylus', 'on_enter': '_search_second'}, 'no_daktylus_found', {'name': 'found_two_daktyles', 'on_enter': '_make_scansion', 'tags': 'accepted'}, 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
		self.positions = [0, 0]
		self.machine = CustomStateMachine(model=self, states=FSA14._states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_daktylus')
		self.machine.add_transition('search_first_daktylus', 'searching_for_first_daktylus', 'searching_for_second_daktylus', conditions=[self._first_found])
		self.machine.add_transition('search_first_daktylus', 'searching_for_first_daktylus', 'no_daktylus_found', unless=[self._first_found])
		self.machine.add_transition('search_second_daktylus', 'searching_for_second_daktylus', 'found_two_daktyles', conditions=[self._second_found])
		self.machine.add_transition('search_second_daktylus', 'searching_for_second_daktylus', 'no_daktylus_found', unless=[self._second_found])
		self.machine.add_transition('not_found', 'no_daktylus_found', 'fallback')
			
	def _search_first(self):
		if self._search(10):
			#found daktylus in fifth syllable
			self.positions[0] = 5
			self.search_first_daktylus()
		elif self._search(6):
			self.positions[0] = 3
			self.search_first_daktylus()
		elif self._search(8):
			self.positions[0] = 4
			self.search_first_daktylus()
		elif self._search(2):
			self.positions[0] = 1
			self.search_first_daktylus()
		#last case is not executed because no second daktylus can be found
		else:
			#search failed, passing into no_daktylus_found
			self.search_first_daktylus()
	
	def _search_second(self):
		#second daktylus must be in second foot
		if 1 in self.positions:
			if self._search(4):
				self.positions[1] = 2
			self.search_second_daktylus()
		#daktylus must be in first or second foot
		elif 4 in self.positions:
			if self._search(2):
				self.positions[1] = 1
				self.search_second_daktylus()
			elif self._search(4):
				self.positions[1] = 2
				self.search_second_daktylus()
			else:
				self.search_second_daktylus()
		#daktylus must be in fourth, first, or second foot
		elif 3 in self.positions:
			if self._search(8):
				self.positions[1] = 4
				self.search_second_daktylus()
			elif self._search(2):
				self.positions[1] = 1
				self.search_second_daktylus()
			elif self._search(4):
				self.positions[1] = 2
				self.search_second_daktylus()
			else:
				self.search_second_daktylus()
		#daktylus can be in any but the fifth foot
		elif 5 in self.positions:
			if self._search(6):
				self.positions[1] = 3
				self.search_second_daktylus()
			elif self._search(8):
				self.positions[1] = 4
				self.search_second_daktylus()
			elif self._search(2):
				self.positions[1] = 1
				self.search_second_daktylus()
			elif self._search(4):
				self.positions[1] = 2
				self.search_second_daktylus()
			else:
				self.search_second_daktylus()
		else:
			self.search_second_daktylus()
				
	def set_text(self, text):
		self.text = text
		
	def _search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
	
	def _first_found(self):
		if self.positions[0] > 0:
			return True
		else:
			return False
			
	def _second_found(self):
		if self.positions[1] > 0:
			return True
		else:
			return False
			
	def _reset_positions(self):		
		self.positions = [0, 0]
		
	def _make_scansion(self):
		if 1 in self.positions:
			self.scansion = '-** '
			if 2 in self.positions:
				self.scansion+='-** -- -- -- -X'
				return
			elif 3 in self.positions:
				self.scansion+='-- -** -- -- -X'
				return				
			elif 4 in self.positions:
				self.scansion+='-- -- -** -- -X'
				return
			elif 5 in self.positions:
				self.scansion+='-- -- -- -** -X'
				return
		elif 2 in self.positions:
			self.scansion = '-- -** '
			if 3 in self.positions:
				self.scansion+='-** -- -- -X'
				return				
			elif 4 in self.positions:
				self.scansion+='-- -** -- -X'
				return
			elif 5 in self.positions:
				self.scansion+='-- -- -** -X'
				return
		elif 3 in self.positions:
			self.scansion = '-- -- -** '
			if 4 in self.positions:
				self.scansion+='-** -- -X'
				return
			elif 5 in self.positions:
				self.scansion+='-- -** -X'
				return
		elif 4 in self.positions:
			self.scansion = '-- -- -- -** -** -X'
	
class FSA15(object):

	_states = [{'name': 'waiting', 'on_enter': '_reset_positions'}, {'name': 'searching_for_first_spondeus', 'on_enter': '_search_first'}, {'name': 'searching_for_second_spondeus', 'on_enter': '_search_second'}, 'no_spondeus_found', {'name': 'found_two_spondees', 'on_enter': '_make_scansion', 'tags': 'accepted'}, 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
		self.positions = [0, 0]
		self.machine = CustomStateMachine(model=self, states=FSA15._states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus')
		self.machine.add_transition('search_first_spondeus', 'searching_for_first_spondeus', 'searching_for_second_spondeus', conditions=[self._first_found])
		self.machine.add_transition('search_first_spondeus', 'searching_for_first_spondeus', 'no_spondeus_found', unless=[self._first_found])
		self.machine.add_transition('search_second_spondeus', 'searching_for_second_spondeus', 'found_two_spondees', conditions=[self._second_found])
		self.machine.add_transition('search_second_spondeus', 'searching_for_second_spondeus', 'no_spondeus_found', unless=[self._second_found])
		self.machine.add_transition('not_found', 'no_spondeus_found', 'fallback')
		
	def _search_first(self):
		if self._search(4):
			self.positions[0] = 2
			self.search_first_spondeus()
		elif self._search(2):
			self.positions[0] = 1
			self.search_first_spondeus()
		elif self._search(8):
			self.positions[0] = 4
			self.search_first_spondeus()
		elif self._search(6):
			self.positions[0] = 3
			self.search_first_spondeus()
		else:
			self.search_first_spondeus()
			
	def _search_second(self):
		#second spondeus must be in fifth foot
		if 3 in self.positions:
			if self._search(10):
				self.positions[1] = 5
			self.search_second_spondeus()
		#spondeus must be in third or fifth foot
		elif 4 in self.positions:
			if self._search(6):
				self.positions[1] = 3
				self.search_second_spondeus()
			elif self._search(10):
				self.positions[1] = 5
				self.search_second_spondeus()
			else:
				self.search_second_spondeus()
		elif 1 in self.positions:
			if self._search(8):
				self.positions[1] = 4
				self.search_second_spondeus()
			elif self._search(6):
				self.positions[1] = 3
				self.search_second_spondeus()
			elif self._search(10):
				self.positions[1] = 5
				self.search_second_spondeus()
			else:
				self.search_second_spondeus()
		elif 2 in self.positions:
			if self._search(2):
				self.positions[1] = 1
				self.search_second_spondeus()
			elif self._search(8):
				self.positions[1] = 4
				self.search_second_spondeus()
			elif self._search(6):
				self.positions[1] = 3
				self.search_second_spondeus()
			elif self._search(10):
				self.positions[1] = 5
				self.search_second_spondeus()
			else:
				self.search_second_spondeus()
		else:
			self.search_second_spondeus()
	
	def _search(self, position):
		if self.rules.rule1(self.text, position) or self.rules.rule2(self.text, position) or self.rules.rule3(self.text, position) or self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
	
	def _first_found(self):
		if self.positions[0] > 0:
			return True
		else:
			return False
			
	def _second_found(self):
		if self.positions[1] > 0:
			return True
		else:
			return False
			
	def _reset_positions(self):		
		self.positions = [0, 0]
	
	def set_text(self, text):
		self.text = text
		
	def _make_scansion(self):
		if 1 in self.positions:
			self.scansion = '-- '
			if 2 in self.positions:
				self.scansion += '-- -** -** -** -X'
				return
			elif 3 in self.positions:
				self.scansion += '-** -- -** -** -X'
				return
			elif 4 in self.positions:
				self.scansion += '-** -** -- -** -X'
				return
			elif 5 in self.positions:
				self.scansion += '-** -** -** -- -X'
				return
		elif 2 in self.positions:
			self.scansion = '-** -- '
			if 3 in self.positions:
				self.scansion += '-- -** -** -X'
				return
			elif 4 in self.positions:
				self.scansion += '-** -- -** -X'
				return
			elif 5 in self.positions:
				self.scansion += '-** -** -- -X'
				return
		elif 3 in self.positions:
			self.scansion = '-** -** -- '
			if 4 in self.positions:
				self.scansion += '-- -** -X'
				return
			elif 5 in self.positions:
				self.scansion += '-** -- -X'
				return
		elif 4 in self.positions:
			self.scansion = '-** -** -** -- -- -X'
			return
	
class FSA16(object):
	_states = ['waiting', {'name': 'searching_for_spondeus', 'on_enter': '_search_spondeus'}, {'name': 'spondeus_found', 'tags': 'accepted'}, 'spondeus_not_found', 'fallback']
	
	def __init__(self, name):
		self.name = name
		self.found = False
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
		self.machine = CustomStateMachine(model=self, states=FSA16._states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_spondeus')
		self.machine.add_transition('found_spondeus', 'searching_for_spondeus', 'spondeus_found')
		self.machine.add_transition('no_spondeus_found', 'searching_for_spondeus', 'spondeus_not_found')
		self.machine.add_transition('not_found', 'spondeus_not_found', 'fallback')
		
	def _search_spondeus(self):
		if self._search(4):
			self.scansion = '-** -- -** -** -** -X'
			self.found_spondeus()
		elif self._search(2):
			self.scansion = '-- -** -** -** -** -X'
			self.found_spondeus()
		elif self._search(8):
			self.scansion = '-** -** -** -- -** -X'
			self.found_spondeus()
		elif self._search(6):
			self.scansion = '-** -** -- -** -** -X'
			self.found_spondeus()
		elif self._search(10):
			self.scansion = '-** -** -** -** -- -X'
			self.found_spondeus()
		else:
			self.no_spondeus_found()
	
	def set_text(self, text):
		self.text = text
		
	def _search(self, position):
		if self.rules.rule1(self.text, position) or self.rules.rule2(self.text, position) or self.rules.rule3(self.text, position) or self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
		