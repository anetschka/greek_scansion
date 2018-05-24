import sys
import re
import codecs

#file containing your syllabication
datafile = codecs.open(sys.argv[1], 'r', 'utf-8')
myverses = datafile.readlines()
datafile.close()

#gold file containing correct syllabication
goldfile = codecs.open(sys.argv[2], 'r', 'utf-8')
goldverses = goldfile.readlines()
goldfile.close()

#logging
logfile = codecs.open(sys.argv[3], 'w', 'utf-8')

#ditionaries will hold verse information
mydic = {} #your syllabication
golddic = {} #gold syllabication

#read datafile (expected format: line code\tverse\tsyllabication\tscansion)
for verse in myverses:
	contents = re.split(r'\t+', verse.rstrip('\r?\n?'))
	simplified = re.sub(r'[\. ]', '#', contents[2])
	mydic[contents[0]] = simplified
	
#read goldfile (expected format: line code\tsyllabication)
for verse in goldverses:
	contents = re.split(r'\t+', verse.rstrip('\r?\n?'))
	simplified = re.sub(r'[\. ]', '#', contents[1])
	golddic[contents[0]] = simplified

#number of evaluated verses
evaluated_items = 0
#number of evaluated syllables
evaluated_syllabs = 0
#correct verses and syllables
correct_items = 0
correct_syllabs = 0
	
#perform string comparison for each verse
for key in mydic.keys():
	if key in golddic.keys():
		evaluated_items+=1
		#verse-wise evaluation
		if mydic[key] == golddic[key]:
			correct_items+=1
		else:
			print(key, file=logfile)
		
		#syllable-wise evaluation
		goldsyllabs = re.split(r'#', golddic[key])
		mysyllabs = re.split(r'#', mydic[key])
		for x in range(0, min(len(goldsyllabs), len(mysyllabs))):
			evaluated_syllabs+=1
			if mysyllabs[x] == goldsyllabs[x]:
				correct_syllabs+=1
		
print('Verses evaluated:')
print(evaluated_items)

print('Syllables evaluated:')
print(evaluated_syllabs)
		
#calculate verse correctness
print('Correct verses:')
print(correct_items/evaluated_items)

#calculate syllable correctness
print('Correct syllables:')
print(correct_syllabs/evaluated_syllabs)

logfile.close()

