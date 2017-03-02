#IMPORTS
import os
import SimpleCV
import MySQLdb
import string
import random
import subprocess
from grooveshark import Client

#VARIABLE DEFINITIONS
mysqlhost = "" #Your database host
mysqlusername = "" #Your database username
mysqlpassword = "" #Your database password
cam = SimpleCV.Camera()
con = MySQLdb.connect(mysqlhost, mysqlusername, mysqlpassword, 'LISA');

#FUNCTIONS
def Lights(self, userinput):
	if "on" in userinput:
		os.system("heyu on A1")
		return "Lumos"
	if "off" in userinput:
		os.system("heyu off A1")
		return "Nox"
def Lamp(self, userinput):
	return "You have to buy a socket module first."
def LightState(self, userinput):
	img = cam.getImage()
	bw = img.crop(210, 140, 200, 200).binarize(250).invert()

	if (bw.meanColor()[0] > 20):
		if "on" in userinput:		
			return "Looks like it"
		else:
			return "I don't think so"
	else:
	   	if "off" in userinput:
			return "Looks like it"
		else:
			return "I don't think so"
def TempCode(self, userinput):
	TempCode = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))

	try:
		Clearance = int(''.join(x for x in userinput if x.isdigit()))
	except ValueError:
		return "What clearance, moron?"

	if Clearance > 10 or Clearance == "":
		return "That's an invalid clearance."

	c = con.cursor()
	c.execute("INSERT INTO TempCodes (code, clearance) VALUES (SHA2(%s, 384), %s);", (TempCode, Clearance))
	c.close()
	con.commit()

	return TempCode

def PlayMusic(self, userinput):
	client = Client()
	client.init()

	searchquery = userinput.split("song")[1]

	try:
		song = next(client.search(searchquery, type='Songs'))
		p = subprocess.Popen(["exec cvlc " + song.stream.url + " vlc://quit --quiet > /dev/null"], shell=True)

		return "Playing " + str(song)
	except StopIteration:
		return "It don't see that song."

def StopMusic(self, userinput):
	p.kill()
	return "Ok, stopping the music."

def SetVolume(self, userinput):
	beforepercent = userinput.split("%")[0]
	percent = beforepercent.split()[-1]
	os.system("pactl set-sink-volume 0 " + percent + "%")

	return "Got it. Your volume is at " + percent + "% now."
	
