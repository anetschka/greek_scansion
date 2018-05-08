import re
from automata import ruleset
from transitions.extensions import HierarchicalMachine as Machine
from transitions.extensions.states import add_state_features, Tags

@add_state_features(Tags)
class CustomStateMachine(Machine):
	pass

class HFSA13(object):

	_states = [
	'waiting',
	{'name': 'searching_for_daktylus', 'children': ['fifthF', 'thirdF', 'fourthF', 'firstF', 'secondF']},
	{'name': 'daktylus_found', 'tags': 'accepted'},
	'no_daktylus_found',
	'fallback'
	]
	
	def __init__(self, name):
		self.name = name
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
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
		if self._search(10) or self._search(11):
			self.scansion = '-- -- -- -- -** -X'
			self.found_daktylus()
		else:
			self.not_found()
		
	def _search_third(self):
		if self._search(6) or self._search(7):
			self.scansion = '-- -- -** -- -- -X'
			self.found_daktylus()
		else:
			self.not_found()
	
	def _search_fourth(self):
		if self._search(8) or self._search(9):
			self.scansion = '-- -- -- -** -- -X'
			self.found_daktylus()
		else:
			self.not_found()
	
	def _search_first(self):
		if self._search(2) or self._search(3):
			self.scansion = '-** -- -- -- -- -X'
			self.found_daktylus()
		else:
			self.not_found()
		
	def _search_second(self):
		if self._search(4) or self._search(5):
			self.scansion = '-- -** -- -- -- -X'
			self.found_daktylus()
		else:
			self.not_found()
		
	def set_text(self, text):
		self.text = text
		
	def _search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
	
class HFSA14(object):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_first_daktylus', 'children': ['fifthF', 'thirdF', 'fourthF', 'firstF']}, 
	{'name': 'searching_for_second_daktylus', 'children': ['thirdF', 'fourthF', 'firstF', 'secondF']}, 
	'no_daktylus_found',
	{'name': 'found_two_daktyles', 'on_enter': '_make_scansion', 'tags': 'accepted'}, 
	'fallback'
	]
	
	def __init__(self, name):
		self.name = name
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
		self.positions = [0, 0]
		self.machine = CustomStateMachine(model=self, states=HFSA14._states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_daktylus_fifthF', after='_search_fifth')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fifthF', 'searching_for_first_daktylus_thirdF', unless=[self._first_found], after='_search_third')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fifthF', 'searching_for_second_daktylus_thirdF', conditions=[self._first_found], after='_search_third')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_thirdF', 'found_two_daktyles', conditions=[self._second_found])
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_thirdF', 'searching_for_second_daktylus_fourthF', unless=[self._second_found], after='_search_fourth') 
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_fourthF', 'searching_for_second_daktylus_firstF', unless=[self._second_found], after='_search_first')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_firstF', 'found_two_daktyles', conditions=[self._second_found])
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_firstF', 'searching_for_second_daktylus_secondF', unless=[self._second_found], after='_search_second')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_thirdF', 'searching_for_first_daktylus_fourthF', unless=[self._first_found], after='_search_fourth')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_thirdF', 'searching_for_second_daktylus_fourthF', conditions=[self._first_found], after='_search_fourth')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_fourthF', 'found_two_daktyles', conditions=[self._second_found])	
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fourthF', 'searching_for_first_daktylus_firstF', unless=[self._first_found], after='_search_first')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_fourthF', 'searching_for_second_daktylus_firstF', conditions=[self._first_found], after='_search_first')
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_firstF', 'no_daktylus_found', unless=[self._first_found])
		self.machine.add_transition('search_daktylus', 'searching_for_first_daktylus_firstF', 'searching_for_second_daktylus_secondF', conditions=[self._first_found], after='_search_second')
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_secondF', 'found_two_daktyles', conditions=[self._second_found])
		self.machine.add_transition('search_daktylus', 'searching_for_second_daktylus_secondF', 'no_daktylus_found', unless=[self._second_found])
		self.machine.add_transition('not_found', 'no_daktylus_found', 'fallback')
		
	def _search_fifth(self):
		#search through a range of syllables, returning true only for safe cases
		if self._search(10) or self._search(11) or self._search(12):
			self._update_positions(5)
		self.search_daktylus()
		
	def _search_third(self):
		if self._search(6) or self._search(7) or self._search(8):
			self._update_positions(3)
		self.search_daktylus()
	
	def _search_fourth(self):
		if self._search(8) or self._search(9) or self._search(10):
			self._update_positions(4)
		self.search_daktylus()
	
	def _search_first(self):
		if self._search(2) or self._search(3):
			self._update_positions(1)
		self.search_daktylus()
		
	def _search_second(self):
		if self._search(4) or self._search(5) or self._search(6):
			self._update_positions(2)
		self.search_daktylus()
		
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
		self.scansion = ''
		
	def set_text(self, text):
		self.text = text
	
	def _update_positions(self, position):
		if self.positions[0] > 0:
			self.positions[1] = position
		else:
			self.positions[0] = position
	
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
		
	def _search(self, position):
		if not self.rules.rule1(self.text, position) and not self.rules.rule2(self.text, position) and not self.rules.rule3(self.text, position) and not self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True

class HFSA15(object):

	_states = [
	{'name': 'waiting', 'on_enter': '_reset_positions'},
	{'name': 'searching_for_first_spondeus', 'children': ['secondF', 'firstF', 'fourthF', 'thirdF']}, 
	{'name': 'searching_for_second_spondeus', 'children': ['firstF', 'fourthF', 'thirdF', 'fifthF']}, 
	'no_spondeus_found',
	{'name': 'found_two_spondees', 'on_enter': '_make_scansion', 'tags': 'accepted'}, 
	'fallback'
	]
	
	def __init__ (self, name):
		self.name = name
		self.rules = ruleset()
		self.text = ''
		self.scansion = ''
		self.positions = [0, 0]
		self.machine = CustomStateMachine(model=self, states=HFSA15._states, initial='waiting')
		
		self.machine.add_transition('start_analysis', 'waiting', 'searching_for_first_spondeus_secondF', after='_search_second')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_first_spondeus_firstF', unless=[self._first_found], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_secondF', 'searching_for_second_spondeus_firstF', conditions=[self._first_found], after='_search_first')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'found_two_spondees', conditions=[self._second_found])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_firstF', 'searching_for_second_spondeus_fourthF', unless=[self._second_found], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_first_spondeus_fourthF', unless=[self._first_found], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_firstF', 'searching_for_second_spondeus_fourthF', conditions=[self._first_found], after='_search_fourth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'found_two_spondees', conditions=[self._second_found])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fourthF', 'searching_for_second_spondeus_thirdF', unless=[self._second_found], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_fourthF', 'searching_for_first_spondeus_thirdF', unless=[self._first_found], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_fourthF', 'searching_for_second_spondeus_thirdF', conditions=[self._first_found], after='_search_third')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_thirdF', 'found_two_spondees', conditions=[self._second_found])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_thirdF', 'searching_for_second_spondeus_fifthF', unless=[self._second_found], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_thirdF', 'no_spondeus_found', unless=[self._first_found])
		self.machine.add_transition('search_spondeus', 'searching_for_first_spondeus_thirdF', 'searching_for_second_spondeus_fifthF', conditions=[self._first_found], after='_search_fifth')
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fifthF', 'found_two_spondees', conditions=[self._second_found])
		self.machine.add_transition('search_spondeus', 'searching_for_second_spondeus_fifthF', 'no_spondeus_found', unless=[self._second_found])
		self.machine.add_transition('not_found', 'no_spondeus_found', 'fallback')
		
	def _search_second(self):
		if self._search(4) or self._search(5):
			self._update_positions(2)
		self.search_spondeus()
		
	def _search_first(self):
		if self._search(2):
			self._update_positions(1)
		self.search_spondeus()
		
	def _search_fourth(self):
		if self._search(10) or self._search(11):
			self._update_positions(4)
		self.search_spondeus()
		
	def _search_third(self):
		if self._search(7) or self._search(8):
			self._update_positions(3)
		self.search_spondeus()
		
	def _search_fifth(self):
		if self._search(13):
			self._update_positions(5)
		self.search_spondeus()
		
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
		self.scansion = ''
		
	def set_text(self, text):
		self.text = text
		
	def _update_positions(self, position):
		if self.positions[0] > 0:
			self.positions[1] = position
		else:
			self.positions[0] = position
		
	def _make_scansion(self):
		if 1 in self.positions:
			self.scansion = '-- '
			if 2 in self.positions:
				self.scansion+= '-- -** -** -** -X'
				return
			elif 3 in self.positions:
				self.scansion+= '-** -- -** -** -X'
				return
			elif 4 in self.positions:
				self.scansion+= '-** -** -- -** -X'
				return
			elif 5 in self.positions:
				self.scansion+= '-** -** -** -- -X'
		elif 2 in self.positions:
			self.scansion = '-** -- '
			if 3 in self.positions:
				self.scansion+= '-- -** -** -X'
				return
			elif 4 in self.positions:
				self.scansion+= '-** -- -** -X'
				return
			elif 5 in self.positions:
				self.scansion+= '-** -** -- -X'
				return
		elif 3 in self.positions:
			self.scansion = '-** -** -- '
			if 4 in self.positions:
				self.scansion+= '-- -** -X'
				return
			elif 5 in self.positions:
				self.scansion+= '-** -- -X'
				return
		elif 4 in self.positions:
			self.scansion = '-** -** -** -- -- -X'
		
	def _search(self, position):
		if self.rules.rule1(self.text, position) or self.rules.rule2(self.text, position) or self.rules.rule3(self.text, position) or self.rules.rule4(self.text, position) and not self.rules.muta(self.text, position) and not self.rules.hiat(self.text, position):
			return True
		
	