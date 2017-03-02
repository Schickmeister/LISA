#IMPORTS
import aiml

#INIT
Kernel = aiml.Kernel() #Add a new kernel to the kernels dictionary which corresponds to the current user

brainLoaded = False #Brain is not yet loaded
forceReload = False #There is no force reload

while not brainLoaded: #While the brain isn't loaded
	#BRAIN LOAD
	if forceReload: #If we have to force a reload
		Kernel.bootstrap(learnFiles="Startup.xml", commands="load aiml b") #Learn from the aiml files

		brainLoaded = True #The brain is loaded
		Kernel.saveBrain("LISA.brn") #Save the brain
	else: #If we don't have to force a reload
		try: #Try to
			Kernel.bootstrap(brainFile = "LISA.brn") #Load from a brain file
			brainLoaded = True #Brain is loaded
		except: #If we couldn't
			forceReload = True #We have to force a reload

	#BOT VARIABLES
	Kernel.setBotPredicate("name", "Lisa")

#FUNCTIONS
def Respond(userinput, currentuser):
	return Kernel.respond(userinput, currentuser) #Return the kernel's response
