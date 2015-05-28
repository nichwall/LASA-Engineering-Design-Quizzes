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

### BEGIN CONFIG

# Titles of the quizzes
quizTitles = []

# Number of questions in the quiz
quizLengths = []

# Variable to control the quizzes.
quizDatas = """
"""

### END CONFIG

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
			template = JINJA_ENVIRONMENT.get_template('static/studentCreate.html')
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
		template = JINJA_ENVIRONMENT.get_template('static/teacherCreate.html')
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
			template = JINJA_ENVIRONMENT.get_template('static/teacherCreate.html')
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
		template = JINJA_ENVIRONMENT.get_template('static/notLoggedInError.html')
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
		template = JINJA_ENVIRONMENT.get_template('static/quizzes.html')
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
		
		template = JINJA_ENVIRONMENT.get_template('static/quizzes.html')
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
		template = JINJA_ENVIRONMENT.get_template('static/mainPage.html')
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
