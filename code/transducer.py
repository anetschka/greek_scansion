import hfst

class fallbackTransducer(object):
    
    def __init__(self):
        #initialise fst
        self.fallbackTransducer = hfst.HfstBasicTransducer()
        #add states
        self.fallbackTransducer.add_state(0)
        self.fallbackTransducer.add_state(1)
        self.fallbackTransducer.add_state(2)
        self.fallbackTransducer.add_state(3)
        self.fallbackTransducer.add_state(4)
        self.fallbackTransducer.add_state(5)
        self.fallbackTransducer.add_state(6)
        self.fallbackTransducer.add_state(7)
        self.fallbackTransducer.add_state(8)
        self.fallbackTransducer.add_state(9)
        self.fallbackTransducer.add_state(10)
        self.fallbackTransducer.add_state(11)
        self.fallbackTransducer.add_state(12) 
        #these are intermediate states for alternative paths
        #we just append the index of the preceding state once more
        self.fallbackTransducer.add_state(33)
        self.fallbackTransducer.add_state(55)
        self.fallbackTransducer.add_state(77)
        self.fallbackTransducer.add_state(99)
        #transitions
        #first half of first foot
        self.fallbackTransducer.add_transition(0, 1, '-', '-', 1)
        self.fallbackTransducer.add_transition(0, 1, '?', '-', 1)
        #second half of first foot
        self.fallbackTransducer.add_transition(1, 2, '-', '-', 0.6)
        self.fallbackTransducer.add_transition(1, 2, '?', '-', 0.6)
        self.fallbackTransducer.add_transition(1, 11, '*', '*', 0.2)
        self.fallbackTransducer.add_transition(1, 11, '?', '*', 0.2)
        self.fallbackTransducer.add_transition(11, 2, '*', '*', 0.2)
        self.fallbackTransducer.add_transition(11, 2, '?', '*', 0.2)
        #first half of second foot
        self.fallbackTransducer.add_transition(2, 3, '-', '-', 1)
        self.fallbackTransducer.add_transition(2, 3, '?', '-', 1)
        #second half of second foot
        self.fallbackTransducer.add_transition(3, 4, '-', '-', 0.5)
        self.fallbackTransducer.add_transition(3, 4, '?', '-', 0.5)
        self.fallbackTransducer.add_transition(3, 33, '*', '*', 0.25)
        self.fallbackTransducer.add_transition(3, 33, '?', '*', 0.25)
        self.fallbackTransducer.add_transition(33, 4, '*', '*', 0.25)
        self.fallbackTransducer.add_transition(33, 4, '?', '*', 0.25)
        #first half of third foot
        self.fallbackTransducer.add_transition(4, 5, '-', '-', 1)
        self.fallbackTransducer.add_transition(4, 5, '?', '-', 1)
        #second half of third foot
        self.fallbackTransducer.add_transition(5, 6, '-', '-', 0.8)
        self.fallbackTransducer.add_transition(5, 6, '?', '-', 0.8)
        self.fallbackTransducer.add_transition(5, 55, '*', '*', 0.1)
        self.fallbackTransducer.add_transition(5, 55, '?', '*', 0.1)
        self.fallbackTransducer.add_transition(55, 6, '*', '*', 0.1)
        self.fallbackTransducer.add_transition(55, 6, '?', '*', 0.1)
        #first half fourth foot
        self.fallbackTransducer.add_transition(6, 7, '-', '-', 1)
        self.fallbackTransducer.add_transition(6, 7, '?', '-', 1)
        #second half of fourth foot
        self.fallbackTransducer.add_transition(7, 8, '-', '-', 0.7)
        self.fallbackTransducer.add_transition(7, 8, '?', '-', 0.7)
        self.fallbackTransducer.add_transition(7, 77, '*', '*', 0.15)
        self.fallbackTransducer.add_transition(7, 77, '?', '*', 0.15)
        self.fallbackTransducer.add_transition(77, 8, '*', '*', 0.15)
        self.fallbackTransducer.add_transition(77, 8, '?', '*', 0.15)
        #first half of fifth foot
        self.fallbackTransducer.add_transition(8, 9, '-', '-', 1)
        self.fallbackTransducer.add_transition(8, 9, '?', '-', 1)
        #second half of fifth foot
        self.fallbackTransducer.add_transition(9, 10, '-', '-', 0.9)
        self.fallbackTransducer.add_transition(9, 10, '?', '-', 0.9)
        self.fallbackTransducer.add_transition(9, 99, '*', '*', 0.05)
        self.fallbackTransducer.add_transition(9, 99, '?', '*', 0.05)
        self.fallbackTransducer.add_transition(99, 10, '*', '*', 0.05)
        self.fallbackTransducer.add_transition(99, 10, '?', '*', 0.05)
        #sixth foot
        self.fallbackTransducer.add_transition(10, 11, '-', '-', 1)
        self.fallbackTransducer.add_transition(10, 11, '?', '-', 1)
        self.fallbackTransducer.add_transition(11, 12, 'X', 'X', 1)
        self.fallbackTransducer.add_transition(11, 12, '?', 'X', 1)
        self.fallbackTransducer.add_transition(11, 12, '-', 'X', 1)
        #mark accepting state
        self.fallbackTransducer.set_final_weight(12,12)

    def apply(self, line):
        tok = hfst.HfstTokenizer()
        Transducer = hfst.HfstTransducer(self.fallbackTransducer)
        Transducer.push_weights_to_end()
        words = hfst.tokenized_fst(tok.tokenize(line))
        words.compose(Transducer)
        words.minimize()
        return words