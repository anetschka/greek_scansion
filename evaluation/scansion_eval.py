import sys
import codecs
import re

#file containing annotation output
datafile = codecs.open(sys.argv[1], 'r', 'utf-8')
myverses = datafile.readlines()
datafile.close()

#gold standard
goldfile = codecs.open(sys.argv[2], 'r', 'utf-8')
goldverses = goldfile.readlines()
goldfile.close()

#logging
logfile = codecs.open(sys.argv[3], 'w', 'utf-8')

#dictionaries for holding verse information
mydic = {} #automatic annotations
golddic = {} #gold annotation

#read automatic annotations (expected format: line code\tverse\tsyllabication\tscansion
for verse in myverses:
	contents = re.split(r'\t+', verse.rstrip('\r?\n?'))
	mydic[contents[0]] = ''.join(filter(lambda s: re.match(r'[-\?\*]', s), contents[3]))
	
#read gold annotations
for verse in goldverses:
	contents = re.split(r'\t+', verse.rstrip('\r?\n?'))
	golddic[contents[0]] = ''.join(filter(lambda s: re.match(r'[-\?\*]', s), contents[3]))
	
#number verses in sample
sample_items = 0
#false negative verses
fn_items = 0
#false positive verses
fp_items = 0
#number of evaluated syllables 
evaluated_syllabs = 0
#correct verses and syllables
correct_items = 0
correct_syllabs = 0
#false negative syllables
fn_syllabs = 0
#false positive syllables
fp_syllabs = 0

#string comparison for each verse
for key in mydic.keys():
	if key in golddic.keys():
		sample_items += 1
		#verse-wise evaluation
		if re.search(r'[-\?\*]+', mydic[key]) and mydic[key] == golddic[key]:
			correct_items += 1
		#verse has not been annotated: fn
		elif not re.search(r'[-\?\*]+', mydic[key]):
			fn_items += 1
		else:
			fp_items += 1
			print(key, file = logfile)
			print(mydic[key], file = logfile)
			print(golddic[key], file = logfile)
			
		#syllable-wise evaluation
		goldsyllabs = list(golddic[key])
		mysyllabs = list(mydic[key])
		for x in range(0, min(len(goldsyllabs), len(mysyllabs))):
			evaluated_syllabs += 1
			#syllable has been annotated
			if re.match(r'[-\?\*]', mysyllabs[x]) and mysyllabs[x] == goldsyllabs[x]:
				correct_syllabs += 1
			#syllable has not been annotated
			elif not re.match(r'[-\?\*]', mysyllabs[x]) and re.match(r'[-\?\*]', goldsyllabs[x]):
				fn_syllabs += 1
			else:
				fp_syllabs += 1
				
print('Verses in sample:')
print(sample_items)

print('Syllables evaluated:')
print(evaluated_syllabs)

#calculate verse precision
print('Verse precision:')
print(correct_items/(correct_items + fp_items))

#calculate verse recall
print('Verse recall:')
print(correct_items/(correct_items + fn_items))

#syllable precision
print('Syllable precision:')
print(correct_syllabs/(correct_syllabs + fp_syllabs))

#syllable recall
print('Syllable recall:')
print(correct_syllabs/(correct_syllabs + fn_syllabs))

logfile.close()