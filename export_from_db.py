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
query = ("SELECT sentenceid, workid, bookid, line, sentence FROM corpus WHERE workid IN (0, 1, 2, 3, 4, 5, 6)")
cursor.execute(query)

#print data to outfile
for (sentenceid, workid, bookid, line, sentence) in cursor:
	print("{}\t{}\t{}\t{}\t{}".format(sentenceid, workid, bookid, line, sentence.decode("utf-8")), file=outfile)
	
cursor.close()
connection.close()
outfile.close()