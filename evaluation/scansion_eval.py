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
	if len(contents) == 4:
		mydic[contents[0]] = ''.join(filter(lambda s: re.match(r'[-\*X]', s), contents[3]))
	elif len(contents) == 3:
		mydic[contents[0]] = ''.join(filter(lambda s: re.match(r'[-\*X]', s), contents[2]))
	
#read gold annotations
for verse in goldverses:
	contents = re.split(r'\t+', verse.rstrip('\r?\n?'))
	golddic[contents[0]] = ''.join(filter(lambda s: re.match(r'[-\*X]', s), contents[3]))
	
#number verses in sample
sample_items = 0
#false negative verses
fn_items = 0
#false positive verses
fp_items = 0
correct_items = 0

#string comparison for each verse
for key in mydic.keys():
	if key in golddic.keys():
		sample_items += 1
		#verse-wise evaluation
		if re.search(r'[-\?\*]+', mydic[key]) and mydic[key] == golddic[key]:
			correct_items += 1
		elif len(mydic[key]) == 0 and len(golddic[key]) == 0:
			correct_items += 1
		#verse has not been annotated: fn
		elif not re.search(r'[-\?\*]+', mydic[key]) and len(golddic[key]) > 0:
			fn_items += 1
			#log recall errors
			#print(key, file = logfile)
			#print(mydic[key], file = logfile)
			#print(golddic[key], file = logfile)
		else:
			fp_items += 1
			#log precision errors
			print(key, file = logfile)
			print(mydic[key], file = logfile)
			print(golddic[key], file = logfile)
			
logfile.close()
			
print('Verses in sample:')
print(sample_items)

#calculate verse precision
precision = correct_items/(correct_items + fp_items)
print('Verse precision:')
print(precision)

#calculate verse recall
recall = correct_items/(correct_items + fn_items)
print('Verse recall:')
print(recall)

#Calculate verse-wise f-measure
f = (2*precision*recall)/(precision + recall)
print('F measure:')
print(f)