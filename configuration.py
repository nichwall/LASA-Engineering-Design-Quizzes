# Uses Python 2.7

print "This program will allow you to easily edit the quiz data."
print "It assumes that a folder named 'Website' is in the same directory\n and that the folder structure matches that of the"
print "one located at https://github.com/nichwall/LASA-Engineering-Design-Quizzes."
print "\nThe quiz data is stored in a Tab Seperated File (.tsv), and follows the format"
print "of the included file at the above link."

print "**********"
raw_input("Press enter to continue...")

quizSrc = "quizData.tsv"
appSrc = "Website/finalVersion.py"


print "Reading quiz data...",
quizFile = open(quizSrc,'r')
readed = quizFile.read().split("\n")
quizFile.close()
print "Done!"

print "Reading application data...",
appFile = open(appSrc,'r')
appIn = appFile.read().split("\n")
appFile.close()
print "Done!"

qTitles = []
for i in range(6):
	qTitles.append(raw_input("Enter Quiz %s Name: " % i))

outStr = ""
curLine = 0
while appIn[curLine].find("###") == -1:
	outStr += appIn[curLine] + "\n"
	curLine+=1
outStr += "### BEGIN CONFIG\n\n"

# Rename quizzes
outStr += '\n# Titles of the quizzes\nquizTitles = ['
for i in qTitles:
	outStr += '"%s",' % i
outStr = outStr[:-1]+"]"

# Get counts of questions in the quizzes
qLens = []
curLen = 1
for i in range(1,len(readed)-2):
	qNum = readed[i].split("\t")[0]
	if int(qNum) == int(readed[i+1].split("\t")[0]):
		curLen+=1
	else:
		qLens.append(curLen)
		curLen = 1
qLens.append(curLen)

outStr += "\n\n# Number of questions in the quiz\nquizLengths = ["
for i in qLens:
	outStr += '%s,' % i
outStr = outStr[:-1]
outStr += "]"

outStr += '\n\n# Variable to control the quizzes.\nquizDatas = """'
for i in readed:
	outStr += i + "\n"
outStr = outStr[:-1]
outStr += '"""\n\n### END CONFIG\n'

# Add the rest of it back in...
curLine += 1
while appIn[curLine].find("###") == -1:
	curLine+=1

for i in range(curLine+1,len(appIn)-1):
	outStr += appIn[i] + "\n"

# Write to file!

file = open(appSrc,'w')
file.write(outStr)
file.close()
