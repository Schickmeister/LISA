#PROGRAM INFORMATION
author = "Austin L. Schick"
version_number = "0.0.0.0"

#INIT
import os
os.system("clear")
raw_input("Hi, I'm LISA " + version_number + ". Press any key to get started.")
os.system("clear")

#IMPORTS
import Parser
print "Parser imported"
import LISAFunctions
print "Functions imported"
import nltk
print "NLTK imported"
import cherrypy
print "Cherrypy imported"
import serial
import time
import signal
import threading
from twilio.rest import TwilioRestClient
print "Twilio imported"
import powerapi
print "Powerapi imported"
import SimpleCV
print "SimpleCV imported"
import MySQLdb
print "MySQLdb imported"
import hashlib
import AIMLResponse
print "AIMLResponse imported"


class GetSMS(object):
	#INIT
	os.system("clear")

	#VARIABLE DEFINITIONS
	CurrentUser = {
		"Phone":"",
		"Clearance":0,
		"TempClearance":0,
	}

	mysqlhost = "" #Your database host
	mysqlusername = "" #Your database username
	mysqlpassword = "" #Your database password

	con = MySQLdb.connect(mysqlhost, mysqlusername, mysqlpassword, 'LISA'); #Connect to the database
	FunctionDictionary = {
		"Lights":LISAFunctions.Lights,
		"Lamp":LISAFunctions.Lamp,
		"LightState":LISAFunctions.LightState,
		"TempCode":LISAFunctions.TempCode,
		"PlayMusic":LISAFunctions.PlayMusic,
		"StopMusic":LISAFunctions.StopMusic,
		"SetVolume":LISAFunctions.SetVolume,
	}

	#FUNCTIONS
	def SendMessage(self, message_body, sendto):
		if message_body == "":
			message_body = "I have no response for that."

		twilio_account_sid = "" #Your twilio account sid
		twilio_auth_token = "" #Your twilio auth token
		twilio_phone_number = "" #Your twilio phone number
		client = TwilioRestClient(twilio_account_sid, twilio_auth_token)
		message = client.sms.messages.create(body=message_body, to=sendto, from_=twilio_phone_number)

	def GetUserData(self):
		try: #Try to do this
			c = GetSMS.con.cursor() #Create a new cursor
			c.execute("SELECT phone FROM Users WHERE phone=%s", (GetSMS.CurrentUser["Phone"],)) #See if the phone number is in the database
		except MySQLdb.OperationalError, e: #If the connection timed out
			GetSMS.con = MySQLdb.connect(mysqlhost, GetSMS.mysqlusername, GetSMS.mysqlpassword, 'LISA'); #Connect to the database
			c = GetSMS.con.cursor() #Create a new cursor
			c.execute("SELECT phone FROM Users WHERE phone=%s", (GetSMS.CurrentUser["Phone"],)) #See if the phone number is in the database		

		r = c.fetchall() #Get the result

		if r == (): #If the phone number isn't in the database
			c.execute("INSERT INTO Users VALUES(%s, 0, 0, NULL)", (GetSMS.CurrentUser["Phone"],)) #Enter it

			GetSMS.CurrentUser["Clearance"] = 0 #Set the clearance to zero
			GetSMS.CurrentUser["TempClearance"] = 0 #Set the temporary clearance to zero
		else: #If the phone number is in the database
			c.execute("SELECT clearance FROM Users WHERE phone=%s", (GetSMS.CurrentUser["Phone"],)) #Find its clearance
			GetSMS.CurrentUser["Clearance"] = int(c.fetchall()[0][0]) #Save it in a variable

			c.execute("SELECT tempclearance FROM Users WHERE phone=%s", (GetSMS.CurrentUser["Phone"],)) #Find its temporary clearance
			GetSMS.CurrentUser["TempClearance"] = int(c.fetchall()[0][0]) #Save it in a variable

		c.close() #Close the cursor
		GetSMS.con.commit() #Commit the changes

	def GetFunctionClearance(self, function):
		c = GetSMS.con.cursor() #Create a new cursor

		c.execute("SELECT clearance FROM Commands WHERE functionname=%s", (function,)) #Get the function's clearance
		Function_Clearance = int(c.fetchall()[0][0]) #Save it to a variable

		c.close()

		return Function_Clearance #Return it 

	def ResetTempClearance(self):
		c = GetSMS.con.cursor() #Create a new cursor
		c.execute("UPDATE Users SET tempclearance = 0 WHERE phone=%s", (GetSMS.CurrentUser["Phone"],)) #Reset the temporary clearnce for the current phone number
		c.close() #Close the cursor
		GetSMS.con.commit() #Commit the changes

	def SetTempClearance(self, tempcode):
		c = GetSMS.con.cursor() #Create new cursor
		c.execute("SELECT clearance FROM TempCodes WHERE code = SHA2(%s, 384)", (tempcode,)) #Find the clearance of the tempcode received
		f = c.fetchall() #Get the value

		if f == (): #If it didn't exist
			c.close()
			return -1 #Return a -1
		else:
			c.execute("UPDATE Users SET tempclearance=%s WHERE phone=%s", (f[0][0], GetSMS.CurrentUser["Phone"])) #Give the user the proper tempclearance
			c.execute("DELETE FROM TempCodes WHERE code = SHA2(%s, 384)", (tempcode,))

			c.close() #Close the cursor
			GetSMS.con.commit() #Commit the changes
			return f[0][0] #Return the proper clearance

	def index(self, **keywords):
		if 'From' in keywords and 'Body' in keywords:
			GetSMS.CurrentUser["Phone"] = keywords['From'][1:] #Get the phone number from the Twilio request
			Functions = Parser.Parse(keywords['Body'], GetSMS.CurrentUser["Phone"]) #Get the body of the message from the twilio request and send it through the parser

			GetSMS.GetUserData(self) #Get the clearance of the current user

			if Functions == []: #If no functions were found by the parser
				if len(keywords['Body']) == 8: #If the message was 8 characers long
					OutputClearance = GetSMS.SetTempClearance(self, keywords['Body']) #Set OutputClearance to the output of SetTempClearance
					if OutputClearance == -1: #If it wasn't
						GetSMS.SendMessage(self, AIMLResponse.Respond(keywords['Body'], GetSMS.CurrentUser["Phone"]), GetSMS.CurrentUser["Phone"]) #Respond with aiml
					else:
						GetSMS.SendMessage(self, "You have one function with level " + str(OutputClearance) + " clearance.", GetSMS.CurrentUser["Phone"]) #Send a message alerting the user of what their temporary clearance is.
				else:
					GetSMS.SendMessage(self, AIMLResponse.Respond(keywords['Body'], GetSMS.CurrentUser["Phone"]), GetSMS.CurrentUser["Phone"]) #Respond with aiml
			else: #If a function was found by the parser
				for i in Functions:
					Function_Clearance = GetSMS.GetFunctionClearance(self, i)

					if Function_Clearance <= GetSMS.CurrentUser["Clearance"]: #If the current user has clearance to do the function
						GetSMS.SendMessage(self, GetSMS.FunctionDictionary[i](self, keywords['Body']), GetSMS.CurrentUser["Phone"]) #Send a message with the output of the chosen function i to whoever requested the function
					elif Function_Clearance <= GetSMS.CurrentUser["TempClearance"]: #If the current user has temporary clearance to do the function
						GetSMS.SendMessage(self, GetSMS.FunctionDictionary[i](self, keywords['Body']), GetSMS.CurrentUser["Phone"]) #Send a message with the output of the chosen function i to whoever requested the function
						GetSMS.ResetTempClearance(self) #Reset their temporary clearance
					else: #If the current user doesn't have clearance to do the function
						GetSMS.SendMessage(self, "Sorry, you don't have the clearance to do that.", GetSMS.CurrentUser["Phone"]) #Tell them 

	index.exposed = True

server_socket_port = 0 #Your server socket port
server_socket_host = '0.0.0.0' #Your server socket host

cherrypy.config.update({'server.socket_port':server_socket_port})
cherrypy.config.update({'server.socket_host':server_socket_host})
cherrypy.config.update({'log.screen': False})
cherrypy.quickstart(GetSMS())
