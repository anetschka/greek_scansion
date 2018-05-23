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
query = ("SELECT work.work, bookid, line, sentence FROM bachelor.corpus JOIN work ON corpus.workid = work.workid")
cursor.execute(query)

#print data to outfile
for (work, bookid, line, sentence) in cursor:
	worktitle = work.decode("utf-8").rstrip(".")
	phil_id = worktitle + "." + str(bookid+1) + "," + str(line)
	print("{}\t{}".format(phil_id, sentence.decode("utf-8")), file=outfile)
	
cursor.close()
connection.close()
outfile.close()