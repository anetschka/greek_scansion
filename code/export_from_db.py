import re
import sys
import codecs
import mysql.connector

#outfile
outfile = codecs.open(sys.argv[1], "w", "utf-8")

#read connection parameters from user input
username = sys.argv[2]
passw = sys.argv[3]
ip = sys.argv[4]
db = sys.argv[5]

connection = mysql.connector.connect(user=username, password=passw, host=ip, database=db)

cursor = connection.cursor()
query = ("SELECT work.work, book.book, line, sentence FROM bachelor.corpus JOIN bachelor.work ON corpus.workid = work.workid JOIN bachelor.book ON corpus.bookid = book.bookid WHERE line NOT REGEXP '(A|B|C|D|E)'")
cursor.execute(query)

#print data to outfile
for (work, bookid, line, sentence) in cursor:
	worktitle = work.decode("utf-8").rstrip(".")
	if re.match(r'(IL|OD|HF|HY|EP|CY|AE|IP|OE)', worktitle):
		phil_id = worktitle + "." + str(bookid.decode()) + "," + str(line)
	else:
		phil_id = worktitle + "." + str(line)
	if worktitle == 'TH' and re.match(r'^\.', bookid.decode()):
		pass
	else:
		print("{}\t{}".format(phil_id, sentence.decode("utf-8")), file=outfile)	
	
extra_query = ("SELECT work.work, book.book, line, sentence FROM bachelor.corpus JOIN bachelor.work ON corpus.workid = work.workid JOIN bachelor.book ON corpus.bookid = book.bookid WHERE line REGEXP '(A|B|C|D|E)'")
cursor.execute(extra_query)

for (work, bookid, line, sentence) in cursor:
	worktitle = work.decode("utf-8").rstrip(".")
	if re.match(r'(IL|OD|HF|HY|EP|CY|AE|IP|OE)', worktitle):
		phil_id = worktitle + "." + str(bookid.decode()) + "," + str(line)
	else:
		phil_id = worktitle + "." + str(line)
	if worktitle == 'TH' and re.match(r'^\.', bookid.decode()):
		pass
	else:
		print("{}\t{}".format(phil_id, sentence.decode("utf-8")), file=outfile)

cursor.close()
connection.close()
outfile.close()