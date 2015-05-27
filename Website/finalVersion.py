# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import users

import re

import logging
import webapp2
import jinja2
import cgi
import os
import random
import datetime
import time
import string
import copy
from collections import OrderedDict

import urllib2
import xml.etree.ElementTree as ET

# Titles of the quizzes
quizTitles = ["Basic Shop Safety",	# Quiz 1
			  "Hand Tools",			# Quiz 2
			  "Basic Power Tools",	# Quiz 3
			  "Metalworking",		# Quiz 4
			  "Advanced Power Tools", # Quiz 5
			  "Electrical"]			# Quiz 6

# Number of questions in the quiz
quizLengths = [15,15,20,8,9,10]

# Variable to control the quizzes.
quizDatas = """Quiz Number	Question Number	Question Text	Correct Answer	Incorrect Answers
1	1	How do you conserve materials?	All of the above.	Use scrap wood.	Measure twice and cut once.	Don't cut in the middle of the wood.
1	2	Which of the following is NOT appropriate to wear in the shop?	Flip flops	Shorts	A t-shirt	Close-toed shoes
1	3	What must ALWAYS be worn while in the shop?	Safety goggles	Ear plugs	Masks	Long pants
1	4	When cleaning up the shop, which of the following should be done first?	Pick up scraps of wood that are reusable.	Sweep off machines.	Grab a broom.	Sweep up dust.
1	5	You should avoid the shop if:	You are injured or feeling sick.	You have other homework to do.	You don't feel like working!	You don't like the other members in your group.
1	6	You should tighten clamps until:	You can't move the wood around anymore.	You have made 35 rotations.	You leave a dent in the wood.	The top touches the wood.
1	7	Why should you be in the shop?	To work.	To have fun.	To see what other people are doing.	To talk to friends.
1	8	When cutting wood:	Always have it clamped down.	Cut against the grain.	Start in the middle.	Toss out all the leftovers.
1	9	Why would you wear a mask?	You have breathing issues.	For funsies, duh!	To protect your chin.	It's Halloween.
1	10	Why is it important to keep the shop clean?	All of the above.	Sawdust is bad to inhale.	It keeps tools in working order.	Debris in the shop is hazardous.
1	11	True or false: hair longer than shoulder length should be pulled back.	True.	False.
1	12	If you have a long sleeved shirt:	Roll up your sleeves.	Just make sure it's not too loose.	You can't enter the shop.	Don't worry about it.
1	13	True or false: high heels are allowed in the shop if they cover your toes.	False	True
1	14	Which step of shop cleaning happens last?	Getting a broom and cleaning up the sawdust.	Putting tools away.	Turning off machines.	Putting scraps away.
1	15	What is the proper sweeping technique?	Sweep towards user in a circular motion.	Sweep only where dust is visible.	Sweep debris into the corners.	Walk in a long line around the shop.
2	1	What is a coping saw used for?	To cut intricate internal cutouts and external shapes out of thin materials.	To cut with the grain of a piece of wood.	To cut across the grain of the wood.	To cut out large simple shapes.
2	2	What do you do if your screwdriver strips the screw?	Remove the stripped screw, get a new one, find a slightly larger screwdriver, and try again.	Use a hammer and force the screw in.	Reset the screwdriver and try again.	Remove stripped screw, get a new one, and try again.
2	3	What is the difference between a mallet and a hammer?	A mallet has a softer blow.	A hammer has a softer blow.	Hammers are used to cut materials.	Mallets usually have a sharp edge.
2	4	What material can you cut with a Hacksaw?	All of the above	Metal	Wood	Plastic
2	5	The purpose of sandpaper is to...	Smooth rough edges on a piece of wood.	Create designs in wood.	Smooth rough edges on a piece of wood or metal.	Clean your workplace.
2	6	True or false: chisels should be used with the grain.	True	False
2	7	What is the difference between a file and a chisel?	A file is used to cut fine amounts of material from a workpiece, while a chisel is used for carving a hard material such as wood, stone, or metal.	A chisel is used to cut fine amounts of material from a workpiece, while a file is used for carving a hard material such as wood, stone, or metal.	Both are used to cut materials.	Both are used to carve.
2	8	Wood glue can be used to...	Glue together two pieces of wood.	Fill in holes in your piece of wood.	Glue another material to wood.	Eat.
2	9	What tool do you use to cut across wood grain?	A Crosscut Saw.	A Rip Saw.	A Coping Saw.	A Hacksaw.
2	10	What is something that must be used if you are working with a hammer?	Clamps	Saw	Screw	Glue
2	11	What is the first step in drilling a hole in a piece of wood?	Clamp down drilled piece of wood and scrap to prevent the drill from going into the table.	Drill a hole using the needed drill bit size.	Drill a pilot hole in the piece of wood.	Glue wood to table to prevent movement.
2	12	How do you cut with a rip saw?	With the grain of the wood.	Across the grain of the wood.	In small intricate cuts.	Diagonally across the grain of the wood.
2	13	True or false: you are always supposed to pull a file against wood.	False	True
2	14	True or false: screws tighten counterclockwise.	False	True
2	15	You want to smooth fine amounts from the corner of a piece of wood. Which tool do you use?	File	Chisel	Hammer	Coping Saw
3	1	When using a drill press, should the object being drilled be clamped down?	Yes.	No.	Only if the object is larger than the platform.	Only if the object is smaller than the platform.
3	2	When using a bandsaw, you should...	Use a push stick and keep your fingers away from the blade.	Cut large or oversized pieces unassisted.	Cut the piece quickly! People are getting impatient!	Clean off your area after you finish each cut.
3	3	What is one instance in which you should NOT use a scroll saw?	When making straight cuts.	Cutting out small pieces.	When the piece is awkward to manage (example: cutting a star shape from a small piece of wood).	When the piece needs to have small curves.
3	4	After using a hot glue gun...	All of the above.	Clean up any hot glue that dripped.	Allow the glue gun to cool.	Store the glue gun away from flammable objects.
3	5	While using a bandsaw, do NOT...	Stop paying to your surroundings and the machine.	Use a push stick.	Keep the blade guard 1/2” above the piece being cut.	Mark where you will be accounting, while also taking into account the width of the blade.
3	6	True or false: when using a handheld electrical drill, you should always mark the center hole.	True, because it works well as a guide.	True, so that you can show off your skills to your adoring audience.	False, because some drill bits (e.g. paddle bits) don’t have a center part.	False, you only need to mark the outer edges.
3	7	True or false: handheld sanders aren’t dangerous.	False. The residue from sanders can cause lacerations and abrasions if it comes into contact with skin, and creates fine sawdust that can irritate the lungs.	True. Sanders don’t have sharp edges and therefore can’t cut people.	True. All they do is sand wood, not cut it.	False. The sawdust and woodchips it creates can be hazardous.
3	8	What would you use a hot glue gun for?	To quickly create strong joints and connections.	For permanents joints.	For heat resistant materials.	For objects that will undergo heavy use.
3	9	What type of cut should be performed with a bandsaw?	Long cuts, large curved cuts, and cuts in large pieces of wood and metal.	Small, intricate cuts that curve.	Cicular cuts in thick boards or plywood.	Cutting 90 degree angles.
3	10	Which part of the drill press is the chuck and what is its purpose?	The chuck is the part that holds the drill press in place while drilling, requiring it to spin with the mechanism and drill a hole.		The chuck is the part of the drill press that allows the material to be securely clamped to the table.	The chuck allows the drill press operator to control to which depth into the material the machine will drill.	The chuck is the part of the drill press that holds the hand feed lever in place, preventing unwanted rotation while the drill is being used.
3	11	What type of cut would you use a scroll saw for?	Small intricate cuts, including 90 degree angles.	Large cuts through thick pieces of wood.	Cutting pieces of metal, such as steel.	Cutting long pieces of wood.
3	12	When using a Miter Saw, what should you do?	Hold the piece of material tightly to the backboard, make sure the blade and material are lined up, and only pull the trigger when you're ready to make the cut.	Grip the piece you're cutting within 5 inches of the blade.	Move the piece of wood while you're cutting.	Pull the trigger to check to see if the saw is working.
3	13	What should you do if a bandsaw has a damaged band?	Ask the instructor to replace the band.	Attempt to replace the band by yourself.	Do not inform anyone and find another machine to use.	Try to use the band saw with the damaged band.
3	14	You want to cut an intricate shape out of wood with the Scroll Saw. What should you do?	Mark the piece, place the guards down, and carefully move the wood through the blade, keeping your hands a safe distance away.	Mark the piece, and begin cutting on the Scroll Saw, keeping your hands close to the blade.	Place the Scroll Saw guards down on the wood, and begin cutting.	Mark the piece, place the guards down, and carefully move the wood through the blade, either straight through or sideways on the blade.
3	15	Why would you use a handheld sander?	To quickly sand down a large area of wood.	To sand small, handheld parts.	To start a fire using friction.	To cut a piece of wood.
3	16	What are miter saws best suited for?	Making large cuts on wood.	Making intricate cuts on stone.	Cutting solid steel blocks in half.	Sanding down small areas.
3	17	Why should the paper for the handheld sander be changed periodically?	To ensure it stays effective at sanding.	To protect the sander.	To keep it from sticking to the sander.	To prevent it from overheating.
3	18	What is the purpose of a jig saw?	To cut pieces that are otherwise too unwieldy to cut into sheets of wood or metal.	To cut intricate shapes out of a certain material.	To make straight cuts.	To  make rounded cuts.
3	19	What is the first step for using a jig saw?	Clamp down your piece of metal or wood.	Set the guard on the jig saw.	Turn on the jig saw.	No other steps required, just make your cut!
3	20	What can you cut with a jig saw?	Metal and wood.	Metal only.	Wood only.	Metal, wood, and plastic.
4	1	What is a belt sander used for?	Sanding larger handheld objects quickly.	Cutting through a solid block of wood.	Creating piles of sawdust.	Launching wood across the shop.
4	2	You want to cut a piece of wood with the panel saw. What should you NOT do?	Hold the wood with one hand while cutting.	Place the wood on the saw rails.	Hold onto the saw with both hands.	Put the saw back in place after finishing the cut.
4	3	You want to use the belt sander but there’s a rip in the belt. What should you do?	Step away from the machine immediately and get the attention of your teacher.	Use it anyways. If it ain’t broke, don’t fix it!	When the piece is awkward to manage (example: cutting a star shape from a small piece of wood).	When the piece needs to have small curves.
4	4	What is the purpose of the Panel saw?	To make large straight cuts in wood.	To smooth down the edges of a piece of wood.	To cut small, sharp curves in wood.	To cut thick pieces of wood.
4	5	You want to cut something with the Panel saw. How do you do that?	Mark where you want to cut, place the wood on the rails, and pull the saw down with both hands.	Hold the piece of wood with one arm and pull down the saw with your other arm.	Mark where you want to cut, place the wood on the rails, and pull the saw with one hand while writing in your logbook with the other.	Have a partner hold the piece of wood while you pull the saw down with both hands.
4	6	What should be used to safely sand a very small piece on the belt sander?	Clamp	Gloves	Another piece of wood	The handle of any hand tool
4	7	Someone is using the Belt Sander, but you just have to quickly sand a small piece of wood. What should you do?	Wait for the other person to finish, then use a clamp to hold onto the small piece of wood while you sand.	Wait for the other person to finish, and then sand the small piece of wood with your hands.	Just walk up to their side and use the Belt Sander at the same time.	Turn off the Belt Sander while they're using it, and demand that you get to use it because you're just going to use it for a second.
4	8	The Panel Saw is loud, you should...	Wear ear protection.	Attempt to cover your ears with your hands as you pull the saw down.	Neglect your ears.	Try to operate the machine quickly and in a slapdash manner in order to minimize damage to your ears.
5	1	An angle grinder is used to cut or grind...	Smaller metal objects.	Blocks of wood.	Solid steel blocks.	People.
5	2	Chop saws are used to cut...	Metal bars or rods.	Metal sheets.	Wood.	Plastics.
5	3	Timmy is about to drill a hole in a piece of metal, and his buddy Samantha tells him he doesn't need to clamp it down. Should Timmy listen to Samantha?	No!	Yes!		
5	4	What volt socket should you plug a Grinder into?	120 volts.	80 volts.	69 volts.	60 volts.
5	5	You should always pre drill a hole for 	All of the the above.	Rivets.	Bolts.	Screws.
5	6	If you see sparks coming off of an abrasive chop saw you should...	Not panic, its totally normal.	Place something over the saw, can't let those sparks get lose!	Shut off the saw immediately- something is wrong.	Panic and run from the saw.
5	7	What should you place over a hole when putting a screw in?	A washer.	A nail.	Plastic wrap.	Nothing.
5	8	When using the chop saw all of the following protective gear should be worn EXCEPT for:	A breathing mask.	Hearing protection.	Gloves.	You don’t need protection when using a chop saw.
5	9	When using the angle grinder, which of the following should you do?	Be prepared for abrasive vibration from the device.	Turn it off if sparks are released.	Use only one hand.	Make the cut as quickly as possible.
6	1	How many tools and materials are required to make a good solder connection?	5.	2.	3.	4.
6	2	How many tools are required to make a good crimped connection?	3.	1.	2.	4.
6	3	Fill in the blanks: After cutting and stripping your piece of wire correctly, how do you proceed if you want to create a solder joint? Once the tip of the soldering iron is hot, ________. Next you need to _____ the tip. Hold the soldering iron _____ and a long piece of solder ______. Place the soldering iron on the _____ of the wire and let the wire heat up. After a few seconds apply the solder, first to the tip of the soldering iron to create a heat bridge and then to the _________ of the joint and move the solder along the joint until it is completely covered in solder. Be careful not to create a ______. The joint should be smooth and shiny. If it is _____ and ____ it is a _____ joint. If it is a solid joint,_______ the cooled joint in _______.	Wipe the tip on the damp sponge to remove any remaining residue. Tin. In your dominant hand... in the other. Underside. On the top side. Blob. A blob... not shiny... a cold. Wrap...electrical tape.	Apply solder to the iron. Clean the tip. In your dominant hand... in the other. Underside. On the top side. Blob. A blob... not shiny... a cold. Wrap...electrical tape.	Turn off the soldering iron. Wipe the tip on the sponge. In your dominant hand... in the other. Underside. On the top side. Blob. A blob... not shiny... a cold. Wrap...electrical tape.	Wipe the tip on the damp sponge to remove any remaining residue. Tin. In your dominant hand... in the other. Underside. On the top side. Blob. A blob... not shiny... a cold. Wrap...heatshrink.
6	4	After cutting and stripping your piece of wire correctly, how do you proceed if you want to create a crimped connection?	Place the connector (fork, circle) onto the stripped wire.	Grab the crimpers.	Solder the end.
6	5	What is the purpose of soldering?	To create a conductive connection between two wires.	Soldering has no use- it’s a totally aesthetic operation.	To add connectors.
6	6	True or false: when stripping wire, place the wire ¼-½ inches into the wire stripper’s head.	True.	False.
6	7	True or false: wire crimpers are used to add connections onto wires.	True.	False.
6	8	True/False: After placing your wire into your pin holder on the 25 pin connector, you should have an inch of uninsulated wire on the outside.	False.	True.
6	9	True/False: The purpose of the Wire Strippers is to remove the insulation from the wire.	True.	False.
6	10	A multimeter can perform the tasks of the ______, _______, and _______.	Voltmeter, ammeter, ohmmeter.	Voltmeter, resistance meter, electricity meter.	Voltmeter, current meter.	Amperage meter, voltmeter, ohmmeter.
"""

classID_list = ['000000000']

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def returnSpacesToString(s):
	out = ""
	for i in s:
		if i=="_":
			out+=" "
		else:
			out+=i
	return out

class Student(db.Model):
	loginName = db.StringProperty(required=True)
	realName = db.StringProperty()
	classID = db.StringProperty()
	quizScores= db.StringProperty()
	dateCreated = db.DateProperty()
class Teacher(db.Model):
	loginName = db.StringProperty(required=True)
	realName = db.StringProperty()
	classID = db.StringProperty()
	classTitle = db.StringProperty()
	dateCreated = db.DateProperty()

def class_id_generator(size=9,chars=string.ascii_uppercase+string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def createStudentCookie(student):
	query = Teacher.all()
	query.filter("classID =",student.classID)
	teacherGet = query.get()
	cookieString1 = "S/"
	cookieString1 += student.realName + "/"
	cookieString1 += student.classID + "/"
	# Because students might make an account without a teacher, we'll just catch
	# an exception if they don't have a teacher and put in an identifier for "No Teacher"
	tempTeacherString = ""
	try:
		tempTeacherString += teacherGet.realName + "/"
		tempTeacherString += teacherGet.classTitle + "/"
	except:
		tempTeacherString = "NOTEACHER/NOCLASS/"
	
	cookieString1 += tempTeacherString
	cookieString1 += student.quizScores[0]
	cookieString1 += student.quizScores[1]
	cookieString1 += student.quizScores[2]
	cookieString1 += student.quizScores[3]
	cookieString1 += student.quizScores[4]
	cookieString1 += student.quizScores[5]
	
	# Remove all spaces and replace with underscores
	cookieString = ""
	for i in cookieString1:
		if i==" ":
			cookieString+="_"
		else:
			cookieString+=i
	
	#return cookieString
	return cookieString.encode("ascii","ignore")
def createTeacherCookies(teacherEmail):
	# Get all of the Teacher's that have the same login (e-mail) name.
	teacherQuery = Teacher.all()
	teacherQuery.filter("loginName =",teacherEmail)
	teacherQuery.order('classTitle')
	
	totalString = ""
	
	# Get only the first 6 teachers, because they can only have 6 classes.
	# Make multiple cookie strings. One cookie per class
	for teacher in teacherQuery.run(limit=6):
		# Set up the cookie header
		cookieString1 = "T/"
		cookieString1 += teacher.realName + "/"
		cookieString1 += teacher.classTitle + "/"
		cookieString1 += teacher.classID + "/"
		# Get all (50) students in class
		studentQuery = Student.all()
		studentQuery.filter("classID =",teacher.classID)
		# Loop through students to put in their information
		for j in studentQuery.run(limit=50):
			cookieString1 += j.realName + "/"
			cookieString1 += j.quizScores + "/"
		# Add the end part of the cookie
		# Remove all spaces and replace with underscores
		cookieString = ""
		for i in cookieString1:
			if i==" ":
				cookieString+="_"
			else:
				cookieString+=i
		# Concatenate cookie strings
		totalString += cookieString + "\t\t\t"
	return totalString.encode("ascii","ignore")

def readQuizData(quizNumber,shuffleQuestions=True):
	# Get the first index that we'll search
	startIndex = 1
	for i in range(quizNumber-1):
		startIndex += quizLengths[i]
	# create the correctAnswers dictionary
	quizQuestions = quizDatas.split("\n")[startIndex:startIndex+quizLengths[quizNumber-1]]
	quizData = []
	correctAnswers = []
	# Loop through the questions of the current quiz
	for i in quizQuestions:
		# Split the data of the question along the tabs (because it's from a TSV)
		currentLine = i.decode('utf-8').split("\t")
		currDict = {}
		currDict['question'] = currentLine[2]
		currDict['questionID'] = currentLine[1]
		currDict['correctAnswer'] = currentLine[3]
		correctAnswers.append(currentLine[3])
		# Get the answer choices
		tempAns = []
		for i in range(3,len(currentLine)):
			tempAns.append(currentLine[i])
		# randomize the choices, and then put them into the current dictionary
		if shuffleQuestions:
			random.shuffle(tempAns)
			for i in range(len(tempAns)):
				currDict['ans'+str(i+1)] = tempAns[i]
		quizData.append(currDict)
	return quizData,correctAnswers

class CleanupOldPeople(webapp2.RequestHandler):
	def get(self):
		# Get day of today, we're going to remove everyone
		# older than 6 months. To mark for deletion, just
		# say they were created in 1990, and they'll be cleaned
		# with everyone else, so there's a little bit of time to
		# recover if someone deleted accidentally.
		currentDate = datetime.datetime.now().date()
		# Loop through teachers and clean out old ones
		teachers = Teacher.all()
		for t in teachers.run():
			createDate = t.dateCreated
			timeDelta = currentDate-createDate
			if timeDelta.days>180:
				t.delete()
		
		# Loop through students to clean up
		students = Student.all()
		for s in students.run():
			createDate = s.dateCreated
			timeDelta = currentDate-createDate
			if timeDelta.days>180:
				s.delete()

class LessonRedirect(webapp2.RequestHandler):
	def get(self):
		self.redirect("http://lasaengineeringdesign.weebly.com/")
	
# Create a student to put them into the datastore
class CreateStudent(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		# Check if they're logged in. If they're not, let them know and prevent them from continuing in their registration.
		if not user:
			self.redirect('/notLoggedInError')
		
		template_values = {
			'userName': user,
			'studentName': "",
			'class_id': "",
			'nameError': "",
			'idError': "",
			}
		template = JINJA_ENVIRONMENT.get_template('studentCreate.html')
		self.response.write(template.render(template_values))
	def post(self):
		user = users.get_current_user()
		# Check if they're logged in. If they're not, let them know and prevent them from continuing in their registration.
		if not user:
			self.redirect('/notLoggedInError')
		
		# Get the values of the form via POST
		studentName_Form = cgi.escape(self.request.get('studentname'))
		classID_Form = cgi.escape(self.request.get('class_id'))
		
		# We haven't hit any errors yet
		nameError = ""
		idError = ""
		
		# Get class ID's from datastore, using Teacher's "key"
		classes = Teacher.all(keys_only=True)
		for id in classes.run():
			# get the key_name for every entry
			#logging.debug(id.name())
			classID_list.append(str(id.name()))
		
		# Check if their name is less than 2 characters, because
		# we're requiring between 2 an 20 characters.
		if len(studentName_Form)<2 or len(studentName_Form)>20:
			nameError = "Name must be between 2 and 20 characters"
		else:
			# If they had the right number of characters, make sure they're only using
			# alpha characters and spaces.
			for i in studentName_Form:
				if not (i.isalpha() or i.isspace()):
					nameError = "Name may only contain letters and spaces"
		
		# Check that it's exactly 9 characters long.
		if len(classID_Form)!=9:
			idError = "Class ID must be 9 digits long"
		# Check that the ID exists
		elif classID_Form not in classID_list:
			idError = "Class has not been created, please check with your teacher for the correct ID"
		# Class of 000000000 is "no class"
		if classID_Form=="000000000":
			idError = ""
		
		# If either error is no longer empty, then we know that they still need to change
		# inputs.
		stillCreating = (len(nameError+idError)!=0)
		if stillCreating:
			# If they're still creating, display the form with previous inputs and errors, if any
			template_values = {
				'userName': user,
				'studentName': studentName_Form,
				'class_id': classID_Form,
				'nameError': nameError,
				'idError': idError,
			}
			template = JINJA_ENVIRONMENT.get_template('studentCreate.html')
			self.response.write(template.render(template_values))
		# If they entered good information, then create their student data! And then redirect
		# them to the quiz selection page.
		else:
			newStudent = Student(loginName =	user.email(),
								 realName =		studentName_Form,
								 classID =		classID_Form,
								 quizScores = 	"000000")
			# Save what day the student was created, because cleaning will happen every month
			# to remove old accounts that were created more than 6 months ago.
			newStudent.dateCreated = datetime.datetime.now().date()
			newStudent.put()
			time.sleep(1)
			# Once we've put the student into the datastore, we can create their cookie.
			#self.response.headers.add_header('Set-Cookie','userData = %s' % createStudentCookie(newStudent))
			self.redirect('/')

# Create a Teacher to put in the datastore
class CreateTeacher(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		# Check if they're logged in. If they're not, let them know and prevent them from
		# continuing in their registration.
		if not user:
			self.redirect('/notLoggedInError')
		
		template_values = {
			'userName': user,
			'teacherName': "",
			'classTitle': "",
			'nameError': "",
			'titleError': "",
		}
		template = JINJA_ENVIRONMENT.get_template('teacherCreate.html')
		self.response.write(template.render(template_values))
	def post(self):
		user = users.get_current_user()
		# Check if they're logged in. If they're not, let them know and prevent them from
		# continuing in their registration.
		if not user:
			self.redirect('/notLoggedInError')
		
		# Get variables passed from POST
		teacherName_Form = cgi.escape(self.request.get('teacherName'))
		classTitle_Form = cgi.escape(self.request.get('classTitle'))
		
		# We haven't hit any errors yet
		nameError = ""
		titleError = ""
		
		# Check if the teacher name is more than two characters.
		if len(teacherName_Form) < 2 or len(teacherName_Form) >20:
			nameError = "Name must be between 2 and 20 characters"
		# If they had the right number of characters, make sure they're only using
		# alpha characters, spaces, or periods.
		for i in teacherName_Form:
			if not (i.isalpha() or i.isalnum() or i.isspace() or i=="."):
				nameError = "Name may only contain letters, spaces, or periods"
		
		# Check that the class title on uses alphanumeric and spaces.
		for i in classTitle_Form:
			if not (i.isalpha() or i.isalnum() or i.isspace()):
				titleError = "Class title may only contain letters, numbers, spaces, and periods"		
		
		# If either error is no longer empty, then we know that they still need to change
		# inputs.
		stillCreating = (len(nameError+titleError)!=0)
		if stillCreating:
			# Check if we had an error. If we did, return to the form so that
			# information can be corrected. Otherwise, create the Teacher object and redirect home
			#if len(nameError+titleError)!=0:
			template_values = {
				'userName': user,
				'teacherName': teacherName_Form,
				'classTitle': classTitle_Form,
				'nameError': nameError,
				'titleError': titleError,
			}
			template = JINJA_ENVIRONMENT.get_template('teacherCreate.html')
			self.response.write(template.render(template_values))
		else:
			logging.debug("Creating teacher!")
			# Generate the classID.
			
			# Get class ID's from datastore, using Teacher's "key"
			classes = Teacher.all(keys_only=True)
			for id in classes.run():
				# get the key_name for every entry
				#logging.debug(id.name())
				classID_list.append(str(id.name()))
			
			# Basically, we're going to generate class ID's until we find one that
			# isn't already in use
			new_classID = "000000000"
			while new_classID in classID_list:
				new_classID = class_id_generator()
			
			# Otherwise, make the Teacher and put them in the datastore!
			# Teacher's key_name will be their classID, to allow for faster
			# searching of classes already created
			newTeacher = Teacher(key_name	= str(new_classID),
								 loginName	= user.email(),
								 realName	= teacherName_Form,
								 classID	= new_classID,
								 classTitle	= classTitle_Form)
			newTeacher.dateCreated = datetime.datetime.now().date()
			# Put in datastore
			newTeacher.put()
			time.sleep(1)
			# create cookies! As usual...
			self.redirect('/')

class NotSignedIn(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('notLoggedInError.html')
		self.response.write(template.render())
	
class Signin(webapp2.RequestHandler):
	def get(self):
		# Redirect to the Home page after the signin page
		self.redirect(users.create_login_url('/'))

class Quiz(webapp2.RequestHandler):
	def get(self):
		print self.request.url
		user = users.get_current_user()
		if user:
			user = user.nickname()
		else:
			user = "Guest"
		
		quizNumber = eval(self.request.url.split("/")[-1][-1])
		questionSetArray, correctAnsArray = readQuizData(quizNumber)
		template_values = {
			'userName': user,
			'buttonArray': questionSetArray,
			'quizNum': quizNumber,
			'quizAns': correctAnsArray,
			'isChecking': False}
		template = JINJA_ENVIRONMENT.get_template('/quizzes.html')
		self.response.write(template.render(template_values))
	def post(self):
		answers = []
		i = 1
		# Read the quiz data for checking
		quizNumber = eval(self.request.url.split("/")[-1][-1])
		quizData = readQuizData(quizNumber,False)
		numberCorrect = 0
		questionCount = len(quizData[1])
		#corAnswers = self.request.get('stuffyStuff')
		corAnswers = quizData[1]
		answers = []
		for q in range(1,questionCount+1):
			tempDict = {}
			tempDict['question']=quizData[0][q-1]['question']
			tempDict['correctAnswer']=quizData[0][q-1]['correctAnswer']
			tempDict['isCorrect']= (corAnswers[q-1]==self.request.get(str(q)))
			tempDict['userAnswer'] = self.request.get(str(q))
			if tempDict['isCorrect']:
				numberCorrect+=1
			answers.append(tempDict)
		scores = {}
		try:
			scores['percent'] = str(numberCorrect*100/questionCount)+"%"
		except:
			scores['percent'] = "0%"
		scores['qCount'] = questionCount
		scores['cCount'] = numberCorrect
		
		# Get cookie
		cookieFilling = returnSpacesToString(self.request.cookies.get('userData','0'))
		oldScore = -1
		user = users.get_current_user()
		# Check if we're a student
		if cookieFilling.split("/")[0]=="S":
			oldScore = cookieFilling.split("/")[-1][quizNumber-1]
			# Check if they scored higher on this quiz than what they have in their cookie
			if numberCorrect > ord(cookieFilling.split("/")[-1][quizNumber-1])-97:
				# Check if user, so that we can update grades.
				if user:
					# Get the student
					getStudent = Student.all()
					getStudent.filter("loginName =",users.get_current_user().email())
					student = getStudent.get()
					# Replace the grade in place
					newScores = ""
					for i in range(0,quizNumber-1):
						newScores += student.quizScores[i]
					newScores+=chr(numberCorrect+97)
					for i in range(quizNumber,6):
						newScores += student.quizScores[i]
					#student.quizScores[quizNumber-1] = chr(numberCorrect+97)
					student.quizScores = newScores
					# Return student to datastore
					student.put()
					# Reset the cookie
					self.response.headers.add_header('Set-Cookie','userData = %s' % createStudentCookie(student))
		# Read cookie to get the information from previous runs
		cookieFilling = returnSpacesToString(self.request.cookies.get('userData','0'))
		username = "Guest"
		if cookieFilling != "0":
			username = cookieFilling.split("/")[1]
		
		template_values = {
			'userName': username,
			'answers': answers,
			'score': scores,
			'oldscore': oldScore,
			'isChecking': True
		}
		
		template = JINJA_ENVIRONMENT.get_template('quizzes.html')
		self.response.write(template.render(template_values))

class RemoveClass(webapp2.RequestHandler):
	def post(self):
		teacherQuery = Teacher.all()
		teacherQuery.filter("classID =",classID)
		teacherGet = teacherQuery.get()
		teacherGet.dateCreated = datetime.datetime(1990,0,0,0,0)
		teacherGet.put()
		
		studentQuery = Student.all()
		studentQuery.filter("classID =",classID)
		for q in studentQuery.run():
			q.dateCreated = datetime.datetime(1990,0,0,0,0)
			q.put()
		self.redirect("/")

class MainPage(webapp2.RequestHandler):
	def get(self):
		# Where did we come from?
		refferrer = self.request.url
		user = users.get_current_user()
		
		loggedIn = False
		hasAccount = False
		isStudent = False
		isTeacher = False
		
		# Gradebook things!
		gradebookData = []
		# Quiz Data
		q1 = 'N/A'
		q2 = 'N/A'
		q3 = 'N/A'
		q4 = 'N/A'
		q5 = 'N/A'
		q6 = 'N/A'
		
		teacherName = ""
		userName = ""
		className = ""
		classID = ""
		
		if user:
			# Check the grades in the cookie
			cookieFilling = self.request.cookies.get('userData','0')
			# If they're a student...
			if cookieFilling.split("/")[0] == "S":
				# Class Info
				logging.debug("cookieFilling: "+str(cookieFilling))
				userName = cookieFilling.split("/")[1]
				teacherName = cookieFilling.split("/")[3]
				className = cookieFilling.split("/")[4]
				classID = cookieFilling.split("/")[2]
				
				# Insert grades
				grades = cookieFilling.split("/")[-1]
				if grades[0]!="0":
					q1 = str(int(100*float(ord(grades[0])-97)/quizLengths[0]))+"%"
				if grades[1]!="0":
					q2 = str(int(100*float(ord(grades[1])-97)/quizLengths[1]))+"%"
				if grades[2]!="0":
					q3 = str(int(100*float(ord(grades[2])-97)/quizLengths[2]))+"%"
				if grades[3]!="0":
					q4 = str(int(100*float(ord(grades[3])-97)/quizLengths[3]))+"%"
				if grades[4]!="0":
					q5 = str(int(100*float(ord(grades[4])-97)/quizLengths[4]))+"%"
				if grades[5]!="0":
					q6 = str(int(100*float(ord(grades[5])-97)/quizLengths[5]))+"%"
		
		# Check if somebody is logged in. If they're not, let them know that they won't be able to save any quizzes unless
		# they log in. Allow them to take quizzes without logging in, though.
		if user:
			loggedIn = True
			# If they're logged in, and they have an account already, grab their data from the server if they don't have a cookie.
			# This will allow them to redirect directly to the quiz they were trying to take.
			name = user.nickname()
			curEmail = user.email()
			try:
				# Check if there's already a cookie. If there is, then we'll just use the information already there, then redirect
				# to the quiz.
				cookieFilling = self.request.cookies.get('userData','0')
				if cookieFilling == "0":
					logging.debug("oops, try teacher cookie")
					cookieFilling = self.request.cookies.get('userData0','0')
				# If there is a cookie, and the reffering URL is one of the quiz redirects, then redirect to the quiz.
				# If it's not a quiz redirect, then it'll fail and just redirect to the main page.
				if cookieFilling!="0":
					hasAccount = True
					# If they didn't come from a quiz redirect, check if they're a teacher or
					# a student, and then display the correct page information.
					if cookieFilling.split("/")[0]=="T":
						isTeacher = True
						
					elif cookieFilling.split("/")[0]=="S":
						isStudent = True
					# If they have an account and they came here from a quiz redirect, send them
					# to the quiz.
					if eval(refferrer.split("/")[-1].split(".")[0])>0 and eval(refferrer.split("/")[-1].split(".")[0])<100:
						self.redirect('/quiz'+refferrer.split("/")[-1].split(".")[0])
				
					
				# So if there's no cookie, check if they've already created an account.
				else:
					logging.debug("creating cookies...")
					# Check Students first, because more quizzes are taken than people checking grades.
					try:
						getStudent = Student.all()
						getStudent.filter("loginName =",curEmail)
						student = getStudent.get()
						
						if student:
							self.response.headers.add_header('Set-Cookie','userData = %s' % createStudentCookie(student))
							
							isStudent = True
						else:
							# Check teachers last, because less often
							try:
								teacherCookiesData = createTeacherCookies(curEmail).split("\t\t\t")
								for i in range(6):
									try:
										if len(teacherCookiesData[i]) != 0:
											self.response.headers.add_header('Set-Cookie','userData'+str(i)+' = %s' % teacherCookiesData[i])
									except:
										pass
								if len(teacherCookiesData) > 1:
									isTeacher = True
									self.redirect("/")
							except:
								pass
					except:
						pass
			except:
				pass
		else:
			name = "Guest"
			curEmail = "none"
		
		# If they're a teacher, then create the gradebook from their cookie data
		if isTeacher:
			cookieFilling = []
			for i in range(6):
				cookieFilling.append(self.request.cookies.get('userData'+str(i),''))
			for classData in cookieFilling:
				classInfo = {}
				if len(classData)!=0:
					splitted = str(classData).split("/")
					logging.debug(splitted)
					classInfo['isClass'] = True
					classInfo['title'] = splitted[2]
					classInfo['id'] = splitted[3]
					classInfo['students'] = []
					for j in range(4,len(splitted)-1,2):
						tempStudent = {}
						tempStudent['name'] = splitted[j]
						# Get grades!
						for k in range(len(quizLengths)):
							tempStudent['q'+str(k+1)] = int(float(ord(splitted[j+1][k])-97)/quizLengths[k]*100)
							if int(tempStudent['q'+str(k+1)]) < 0:
								tempStudent['q'+str(k+1)] = "N/A"
						classInfo['students'].append(tempStudent)
				else:
					pass
				gradebookData.append(classInfo)
		
		# Once we've checked whether they're logged in, allow them to take a quiz.
		
		template_values = {
			'userName': name,
			'refferrer': refferrer,
			'loggedIn': loggedIn,
			'hasAccount': hasAccount,
			'isTeacher': isTeacher,
			'isStudent': isStudent,
			'classes': gradebookData,
			'q1': q1,
			'q2': q2,
			'q3': q3,
			'q4': q4,
			'q5': q5,
			'q6': q6
		}
		template = JINJA_ENVIRONMENT.get_template('mainPage.html')
		self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/notLoggedInError', NotSignedIn),
	('/signinRedirect', Signin),
	('/redirectToLessons', LessonRedirect),
	('/studentCreate', CreateStudent),
	('/teacherCreate', CreateTeacher),
	('/quiz1', Quiz),
	('/quiz2', Quiz),
	('/quiz3', Quiz),
	('/quiz4', Quiz),
	('/quiz5', Quiz),
	('/quiz6', Quiz),
	('/removeClass', RemoveClass),
	('/cleanup/OAUECQBWP', CleanupOldPeople),
], debug=True)