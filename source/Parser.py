#IMPORTS
import nltk
import MySQLdb

def Parse(sentences, phone):
	#VARIABLE DEFINITIONS
	mysqlhost = "" #Your database host
	mysqlusername = "" #Your database username
	mysqlpassword = "" #Your database password
	restitch = ""
	words = []
	nouns = []
	verbs = []
	functions = []
	Contractions = {"aren't": "are not", "can't": "cannot", "couldn't": "could not", "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not", "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'll": "he will", "he's": "he has", "i'd": "i would", "i'll": "i will", "i'm": "i am", "i've": "i have", "isn't": "is not", "it's": "it is", "let's": "let us", "mightn't": "might not", "musn't": "must not", "shan't": "shall not", "she'd": "she would", "she'll": "she will", "she's": "she is", "shouldn't": "should not", "that's": "that is", "there's": "there is", "they'd": "they would", "they'll": "they will", "they're": "they are", "they've": "they have", "we'd": "we would", "we're": "we are", "we'll": "we will", "we've": "we have", "weren't": "were not", "what'll": "what will", "what're": "what are", "what's": "what is", "what've": "what have", "where's": "where is", "who'd": "who would", "who'll": "who will", "who're": "who are", "who's": "who is", "who've": "who have", "won't": "will not", "wouldn't": "would not", "you'd": "you had", "you'll": "you will", "you're": "you are", "you've": "you have", "how're": "how are"}
	ConfusionSentences = ["what be up", "what be up?"]
	FormsOfBe = ["am", "are", "is", "was", "were", "been", "being"]
	RelevantNouns = ["lights", "lamp", "garage", "cryptoquote", "awake", "up", "alarm", "me", "gpa", "bed", "sleep", "tempcode", "song", "volume", "music"]
	RelevantVerbs = ["turn", "be", "open", "close", "send", "cancel", "stop", "set", "wake", "go", "make", "create", "give", "send", "generate", "play", "change"]

	#MAIN
	con = MySQLdb.connect(mysqlhost, mysqlusername, mysqlpassword, 'LISA'); #Connect to the database
	sentences = sentences.lower().split() #Make all letters lowercase and split sentences into individual words.
	for i in sentences: #Loop through words
		if i in Contractions: #If word is a contraction
			i = Contractions[i] #Split it into its two words
		restitch += i + " " #Add them to the sentence again
	sentences = restitch[:-1] #Remove the final space
	restitch = "" #Reset restitch

	sentences = sentences.lower().split() #Make all letters lowercase and split sentences into individual words.
	for i in sentences: #Loop through words
		if i in FormsOfBe: #If word is a form of be
			i = "be" #Set it to be
		restitch += i + " " #Add it to the sentence again
	sentences = restitch[:-1] #Remove the final space
	restitch = "" #Reset restitch	

	sentences = sentences.lower().split() #Make all letters lowercase and split sentences into individual words.
	for i in sentences: #Loop through words
		if "ing" in i[3:]: #If word is a progressive
			i = i[:-3] #Set remove the last three letters
		restitch += i + " " #Add it to the sentence again
	sentences = restitch[:-1] #Remove the final space
	restitch = "" #Reset restitch

	sentences = nltk.tokenize.sent_tokenize(sentences) #Split into sentences

	for i in sentences: #Loop through sentences
		for x in ConfusionSentences:
			if x in i.lower():
				continue

		words = nltk.tokenize.wordpunct_tokenize(i) #Make all letters lowercase and split sentences into individual words.
		for x in words: #Loop through words
			if x in RelevantNouns: #If word is a relevant noun
				if not x in nouns: #If x isn't already in the nouns list
					nouns.append(x) #Add x to the nouns list
			if x in RelevantVerbs: #If word is a relevant verb
				if not x in verbs: #If x isn't already in the verbs list
					verbs.append(x) #Add x to the verbs list
		for x in verbs: #Loop through the verbs
			for y in nouns: #Loop through the nouns
				c = con.cursor() #Create a new cursor
				c.execute("SELECT functionname FROM Commands WHERE verb=%s and noun=%s", (x,y)) #Select the function which matches the verb noun pair
				f = c.fetchall() #Get the function
				if f != (): #If it's not empty
					functions.append(f[0][0]) #Add it to the list
				c.close() #Close the cursor
	
	return functions
