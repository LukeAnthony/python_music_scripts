import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.scales as scales
import mingus.core.intervals as intervals
from mingus.containers import Note
from mingus.containers import NoteContainer
from mingus.containers import Bar
from mingus.midi import fluidsynth
import random
import sys

try:
	fluidsynth.init(sys.argv[1])
except IndexError:
	print("Error. Must pass in path to a soundfont file as a cla")
	exit()

class PythonEarTrainer:
	noteRange = 0
	noteChordOrInterval = ""
	octave = 0
	invertChordOrInterval = False
	majorMinorAllocation = 0

	firstAttempt = True
	correctGuesses = 0.0
	totalAttempts = 0.0
	percentCorrect = ""
	defaultOctaveList = [ 1, 2, 3, 4, 5, 6 ]
	octaveChoices = []
	octave = 0
	# use same list and boolean for interval type choices and chord type choice
	chordOrIntervalTypeChoices = []
	moreThanOneChordOrIntervalTypeChoice = len(chordOrIntervalTypeChoices) > 1
	# contains a map of the chord types to a touple containing a list of the chord names of that type and the functions that generate those chords
	chordTypesDictionary = { 
		# Triads: 'm', 'M', 'dim', aug, sus4, sus2
		"triad": ( [ "minor triad", "major triad", "diminished triad", "augmented triad", "suspended fourth triad", "suspended second triad" ],
			 [chords.minor_triad, chords.major_triad, chords.diminished_triad, chords.augmented_triad, chords.suspended_fourth_triad, chords.suspended_second_triad] ),
		# Sevenths: 'm7', 'M7', '7', 'm7b5', 'dim7', 'm/M7', 7sus4, 7#11, 7+, m7+
		"seventh": ( [ "minor seventh", "major seventh", "dominant seventh", "half diminished seventh", "diminished seventh", "minor/major seventh", "suspended seventh", "lydian dominant seventh", "augmented major seventh", "augmented minor seventh" ],
			 [chords.minor_seventh, chords.major_seventh, chords.dominant_seventh, chords.half_diminished_seventh, chords.diminished_seventh, chords.minor_major_seventh, chords.suspended_seventh, chords.lydian_dominant_seventh, chords.augmented_major_seventh, chords.augmented_minor_seventh ] ),
		# Augmented: 'aug', 'M7+'', 'm7+',
		"augmented": ( [ "augmented triad", "augmented major seventh", "augmented minor seventh" ],
			[chords.augmented_triad, chords.augmented_major_seventh, chords.augmented_minor_seventh] ),
		# Suspended: 'sus4', 'sus2', '7sus4',  'susb9'
		"suspended": ( [ "suspended fourth triad", "suspended second triad", "suspended seventh", "suspended fourth ninth" ],
			[chords.suspended_fourth_triad, chords.suspended_second_triad, chords.suspended_seventh, chords.suspended_fourth_ninth] ),
		# Sixths: '6', 'm6', '6/7', '6/9'
		"sixth": ( [ "major sixth", "minor sixth", "dominant sixth", "six ninth" ],
			[chords.major_sixth, chords.minor_sixth, chords.dominant_sixth, chords.sixth_ninth] ),
		# Ninths: '9' , 'M9', 'm9', '7b9', '7#9', '6/9'
		"ninth": ( [ "dominant ninth", "major ninth", "minor ninth", "dominant flat ninth", "dominant sharp ninth", "sixth ninth" ],
			[chords.dominant_ninth, chords.major_ninth, chords.minor_ninth, chords.dominant_flat_ninth, chords.dominant_sharp_ninth, chords.sixth_ninth] ),
		# Elevenths: '7#11', 'm11'
		"eleventh": ( [ "lydian dominant seventh", "minor eleventh" ],
			[chords.lydian_dominant_seventh, chords.minor_eleventh] ),
		# Thirteenths: '13' , 'M13', 'm13'
		"thirteenth": ( [ "dominant thirteenth", "major thirteenth", "minor thirteenth" ], 
			[chords.dominant_thirteenth, chords.major_thirteenth, chords.minor_thirteenth] ),
		# Altered: '7b5', '7b9', '7#9', '6/7', '7b12'
		"altered": ( [ "dominant flat five", "dominant flat ninth", "dominant sharp ninth", "dominant sixth", "hendrix chord" ], 
			[chords.dominant_flat_five, chords.dominant_flat_ninth, chords.dominant_sharp_ninth, chords.dominant_sixth, chords.hendrix_chord] )
	}

	# can get interval functions here https://github.com/bspaans/python-mingus/blob/master/mingus/core/intervals.py#L160
	# TODO is major unison the same note? thought that was called perfect unison.... same q with minor fifth being aug 4th/dim5th
	# contains interval as key mapped to the intervals.py function that generates it
	intervalTypesDictionary = {
		"P1" : intervals.major_unison,
		"m2" : intervals.minor_second,
		"M2" : intervals.major_second,
		"m3" : intervals.minor_third,
		"M3" : intervals.major_third,
		"P4" : intervals.perfect_fourth,
		"A4" : intervals.minor_fifth,
		"dim5" : intervals.minor_fifth, # looks like mingus uses the minor fifth function for both names
		"P5" : intervals.perfect_fifth,
		"m6" : intervals.minor_sixth,
		"M6" : intervals.major_sixth,
		"m7" : intervals.minor_seventh,
		"M7" : intervals.major_seventh
	}
	
	@staticmethod
	def updateStats(points):
		PythonEarTrainer.correctGuesses += points
		PythonEarTrainer.totalAttempts += 1
		PythonEarTrainer.percentCorrect = str(round(PythonEarTrainer.correctGuesses / PythonEarTrainer.totalAttempts, 2) * 100) + "%"

	@staticmethod
	def isChord(input):
		return input.lower() == "c"

	@staticmethod
	def isNote(input):
		return input.lower() == "n"

	@staticmethod
	def isInterval(input):
		return input.lower() == "i"

	"""
		Decision Tree:
			Decide note, chord, or interval
			Decide which range of notes you want to hear
			Decide which octave to play it in
			if interval or chord
				if interval
					decide which intervals you'd like to hear (perfect unison to major seventh)
				if chord
					decide which chord types to choose from
				decide if you want to include inversions
	"""
	@staticmethod
	def getSettings():
		# resetting choices so you don't add to a populated list
		PythonEarTrainer.chordorIntervalTypeChoices = []
		PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = False
		PythonEarTrainer.octaveChoices = []

		PythonEarTrainer.noteChordOrInterval = input("Do you want to hear a random note, a random chord, or a random interval? Enter 'N' for note, 'C' for chord, 'I' for interval ")
		if( not PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval) and not PythonEarTrainer.isNote(PythonEarTrainer.noteChordOrInterval) and not PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval) ):
			raise ValueError("Input wasn't 'N','C', or 'I")
		
		PythonEarTrainer.noteRange = int(input("Starting at C, how many notes would you like the program to randomly choose from. Ex) 1 = (C), 2 = (C,C#), 3 = (C,Db,D)... " ))
		if( PythonEarTrainer.noteRange < 1 or PythonEarTrainer.noteRange > 12 ):
			raise ValueError("Range must be between 1 and 12, inclusive")

		octaveString = input("Which octave(s), from 1-6, do you want to the program to randomly place the note/chord/root of the interval in? Type the octaves separated by a comma (ex: 1,2,3). Type 'all' to randomly choose between octaves 1-6 ")
		if( octaveString.lower() == "all" ):
			PythonEarTrainer.octaveChoices = PythonEarTrainer.defaultOctaveList
		else:
			octaveChoices = octaveString.split(",")
			for octaveChoice in octaveChoices:
				octaveChoiceInt = int(octaveChoice)
				if octaveChoiceInt not in PythonEarTrainer.defaultOctaveList:
					print("Don't recognize octave : " + octaveChoice)
				else:
					PythonEarTrainer.octaveChoices.append(octaveChoiceInt)
			# if no input was recognized
			if( not PythonEarTrainer.octaveChoices ):
				raise ValueError("Must input at least one random octave choice")
		PythonEarTrainer.setRandomOctave()

		if PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval) or PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval):
			if PythonEarTrainer.isInterval( PythonEarTrainer.noteChordOrInterval ):
				intervalChoices = input("What intervals types would you like a random selection to be made from? Choices are: " + str(list(PythonEarTrainer.intervalTypesDictionary.keys())) + ".\nType the intervals separated by a comma (ex: major second, perfect fifth). To select all interval types, type 'all'.\nNOTE: Choosing to include inversions later will add an additional interval type for every interval chosen here ")
				if( intervalChoices.lower() == "all" ):
					PythonEarTrainer.chordOrIntervalTypeChoices = PythonEarTrainer.intervalTypesDictionary.keys()
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = True
				else:
					intervalChoices = intervalChoices.split(',')
					for interval in intervalChoices:
						if interval not in PythonEarTrainer.intervalTypesDictionary.keys():
							print("Didn't recognize interval type: " + interval)
						else:
							PythonEarTrainer.chordOrIntervalTypeChoices.append(interval)
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = len(PythonEarTrainer.chordOrIntervalTypeChoices) > 1
			if(PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval)):
				chordChoices = input("What chord types would you like a random selection to be made from? Choices are " + str(list(PythonEarTrainer.chordTypesDictionary.keys())) + ".\nType the groups you want to select from separated by a comma (ex: Ninths,Thirteenths,Triads). To select from all chord types, type 'all'. ")
				# TODO better input validation
				if( chordChoices.lower() == "all" ):
					PythonEarTrainer.chordOrIntervalTypeChoices = PythonEarTrainer.chordTypesDictionary.keys()
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = True
				else:
					chordChoices = chordChoices.split(',')
					for chord in chordChoices:
						if chord not in PythonEarTrainer.chordTypesDictionary.keys():
							print("Didn't recognize chord type: " + chord)
						#if valid chord
						else:
							PythonEarTrainer.chordOrIntervalTypeChoices.append(chord)
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = len(PythonEarTrainer.chordOrIntervalTypeChoices) > 1

			# both intervals and chords have the option to include inversions
			invertChordOrInterval = input("Y/N Do you want to include inversions? ")
			if( invertChordOrInterval.lower() != "y" and invertChordOrInterval.lower() != "n" ):
				raise ValueError("Answer must be Y/N")
			PythonEarTrainer.invertChordOrInterval = invertChordOrInterval.lower() == "y"

	@staticmethod
	def setRandomOctave():
		PythonEarTrainer.octave = PythonEarTrainer.octaveChoices[random.randrange(len(PythonEarTrainer.octaveChoices))]

	@staticmethod
	def getRandomChord():
		randomRoot = PythonEarTrainer.getRandomRoot()
		listOfChordFunctions = []
		for chordType in PythonEarTrainer.chordOrIntervalTypeChoices:
			listOfChordFunctions.extend(PythonEarTrainer.chordTypesDictionary[chordType][1])
		# giving each chord an equal chance of being selected
		# TODO maybe give certain chords higher probability than others of appearing
		randomChord = listOfChordFunctions[random.randrange(len(listOfChordFunctions))](randomRoot)
		if( PythonEarTrainer.invertChordOrInterval ):
			secondDiceRoll = random.random()
			# will always invert given these odds. 
			# TODO adjust odds manually as needed to mix inversions in with regular chords
			if( secondDiceRoll < 0.00 ):
				pass
			elif( secondDiceRoll < 0.25 ):
				randomChord = chords.first_inversion(randomChord)
			elif( secondDiceRoll < 0.50 ):
				randomChord = chords.second_inversion(randomChord)
			elif( secondDiceRoll < 0.75 ):
				randomChord = chords.third_inversion(randomChord)
			else:
				randomChord = chords.fourth_inversion(randomChord)
		randomChordAsNoteObjects = []
		for tone in randomChord:
			toneAsNote = Note(tone, PythonEarTrainer.octave, None, 110, 1)
			randomChordAsNoteObjects.append(toneAsNote)
		#.determine returns all matching names in list. first entry is most accurate. excluding root note in the chord name since we already have it
		chordName = ' '.join(chords.determine(randomChord)[0].split(' ')[1:])
		# to get chord type list:
			# for each key in chordTypesDictionary, if tuple[0] contains chord name, add key to chord type list
		chordTypeList = []
		for key in PythonEarTrainer.chordTypesDictionary:
			if chordName in PythonEarTrainer.chordTypesDictionary[key][0]:
				chordTypeList.append(key)
		return RandomChord(randomRoot, randomChord, randomChordAsNoteObjects, chordTypeList, chordName )

	@staticmethod
	# use 'tonic' method to get root https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L571
	# Need to use chords.determine https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L919 
	def playAndGuessRandomChord(randomChord):
		b = Bar()
		# placing the chord as two half notes in the bar
		b.place_notes(randomChord.chordTones, 2)
		b.place_notes(randomChord.chordTones, 2)
		rootGuess = ""
		typeGuess = ""
		nameGuess = ""
		while True:
			# play bar on channel 1 at 60bpm
			# plays half note four times
			fluidsynth.play_Bar(b, 1, 60)
			fluidsynth.play_Bar(b, 1, 60)
			if not rootGuess or rootGuess.lower() == "r":
				rootGuess = input("What do you think the root of this chord is? Press R to repeat it ")
				if(rootGuess.lower() == "r"):
					continue
			# only ask if user entered 'all' or more than one type and if a guess hasn't been made already/if user asked to repeat the chord
			if (not typeGuess or typeGuess.lower() == "r") and PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice:
				typeGuess = input("What do you think the type of this chord is (triad, augmented, suspended, etc...)? Press R to repeat it ")
				if(typeGuess.lower() == "r"):
					continue
			if not nameGuess or nameGuess.lower() == "r":
				nameGuess = input("Excluding the root, what is the name of this chord (suspended second, major sixth, etc...)? Press R to repeat it ")
				if(nameGuess.lower() == "r"):
					continue

			print("\nThat chord was a: " + str(randomChord) + "\n")

			if(rootGuess == randomChord.randomRoot):
				PythonEarTrainer.updateStats(1.0)
				print("You were correct. The root is: " + rootGuess)
			else:
				print("Incorrect. You guessed: " + rootGuess + ". The root was: " + randomChord.randomRoot)
				PythonEarTrainer.updateStats(0.0)

			if PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice:
				if(typeGuess in randomChord.chordTypeList):
					PythonEarTrainer.updateStats(1.0)
					print("You were correct. The chord type was: " + typeGuess)
				else:
					print("Incorrect. You guessed: " + typeGuess + ". The chord type(s) were: " + str(randomChord.chordTypeList))
					PythonEarTrainer.updateStats(0.0)

			if(nameGuess == randomChord.chordName):
				PythonEarTrainer.updateStats(1.0)
				print("You were correct. The chord name is: " + nameGuess)
			else:
				print("Incorrect. You guessed: " + nameGuess + ". The chord name was: " + randomChord.chordName)
				PythonEarTrainer.updateStats(0.0)
			break

	@staticmethod
	def getRandomNote():
		randomRoot = PythonEarTrainer.getRandomRoot()
		return Note(randomRoot, PythonEarTrainer.octave, None, 105, 1)

	@staticmethod
	def getRandomRoot():
		# https://github.com/bspaans/python-mingus/blob/master/mingus/core/notes.py#L36
		return notes.int_to_note(random.randint(0, PythonEarTrainer.noteRange - 1), "b" if random.random() > .5 else "#")

	@staticmethod
	def playAndGuessRandomNote(randomNote):
		while True:
			b = Bar()
			b.place_notes(randomNote.name, 2)
			b.place_notes(randomNote.name, 2)
			# plays half note four times 
			fluidsynth.play_Bar(b, 1, 60)
			fluidsynth.play_Bar(b, 1, 60)
			guess = input("What note do you think this is? Press R to repeat it ")
			if guess.lower() == "r":
				continue
			elif not notes.is_valid_note(guess):
				print("You entered: " + guess + ", which isn't a note. Must enter a valid note")
				continue
			else:
				if notes.note_to_int(guess) == notes.note_to_int(randomNote.name):
					print("\nCorrect! That note was a '" +  randomNote.name + "-" + str(randomNote.octave) + "'")
					PythonEarTrainer.updateStats(1.0)
				else:
					print("\nIncorrect. You guessed: '" + guess + "'. That note was a '" + randomNote.name + "-" + str(randomNote.octave) + "'")
					PythonEarTrainer.updateStats(0.0)
			break

	@staticmethod
	def calculateIntervalType(firstNoteName, secondNoteName):
		intervalNamesToAbbreviations = {
			"major unison" : ["P1"],
			"minor second" : ["m2"],
			"major second" : ["M2"],
			"minor third" : ["m3"],
			"major third" : ["M3"],
			"perfect fourth" : ["P4"],
			"minor fifth" : ["A4,dim5"],
			"perfect fifth" : ["A4,dim5"],
			"minor sixth" : ["m6"],
			"major sixth" : ["M6"],
			"minor seventh" : ["m7"],
			"major seventh" : ["M7"],
			"perfect octave" : ["P8"]
		}
		# TODO logic for perfect octave
		intervalType = intervals.determine( firstNoteName, secondNoteName )
		return intervalNamesToAbbreviations[intervalType]

	@staticmethod
	def getRandomInterval():
		randomRootNote = Note( PythonEarTrainer.getRandomRoot(), PythonEarTrainer.octave, None, 105, 1 )
		randomRootName = randomRootNote.name
		listOfIntervalFunctions = []
		for intervalType in PythonEarTrainer.chordOrIntervalTypeChoices:
			listOfIntervalFunctions.append(PythonEarTrainer.intervalTypesDictionary[intervalType])
		# giving each interval an equal chance of being selected
		randomIntervalFunction = listOfIntervalFunctions[random.randrange(len(listOfIntervalFunctions))]
		#randomIntervalName = listOfIntervalFunctions[random.randrange(len(listOfIntervalFunctions))](randomRootName)
		randomIntervalName = randomIntervalFunction(randomRootName)
		print(randomIntervalName)
		if( PythonEarTrainer.invertChordOrInterval ):
			diceRoll = random.random()
			# 50% chance to invert
			# TODO adjust odds as needed
			if( diceRoll < 0.5 ):
				# returns an inverted interval
				return RandomInterval( Note( randomIntervalName, PythonEarTrainer.octave, None, 105, 1 ), randomRootNote, PythonEarTrainer.calculateIntervalType( randomIntervalName, randomRootName ) )
			else:
				# returns the normal interval
				return RandomInterval( randomRootNote, Note( randomIntervalName, PythonEarTrainer.octave, None, 105, 1 ), PythonEarTrainer.calculateIntervalType( randomRootName, randomIntervalName ) )
		else:
			# TODO bug where, if user doesnt want inversions but supplies only one octave to be randomized from, second note placed lower than first if the random interval type would have reached into the next octave
			# need to subtract first note from the second. if negative, second note should be up an octave
				# https://144notes.org/bass-guitar/
			# if secondNote - firstNote = 0, would be same note. should do a 50-50 coin flip for unison or perfect octave
			return RandomInterval( randomRootNote, Note( randomIntervalName, PythonEarTrainer.octave, None, 105, 1 ), PythonEarTrainer.calculateIntervalType( randomRootName, randomIntervalName ) )

	@staticmethod
	def playAndGuessRandomInterval(randomInterval):
		b = Bar()
		# quarter note each
		b.place_notes(randomInterval.get_first_note_name(), 2)
		b.place_notes(randomInterval.get_second_note_name(), 2)
		firstNoteGuess = ""
		secondNoteGuess = ""
		intervalGuess = ""
		# TODO bug where pressing R on second or third choices makes you re-enter previous choices
		while True:
			# plays interval twice
			fluidsynth.play_Bar(b, 1, 60)
			fluidsynth.play_Bar(b, 1, 60)
			if not firstNoteGuess or firstNoteGuess.lower() == "r":
				firstNoteGuess = input("What do you think the first note was? Press R to hear it again ")
				if firstNoteGuess.lower() == "r":
					continue
				elif not notes.is_valid_note(firstNoteGuess):
					print("You entered: " + firstNoteGuess + ", which isn't a note. Must enter a valid note")
					continue
				else:
					if( notes.note_to_int(firstNoteGuess) == notes.note_to_int(randomInterval.get_first_note_name()) ):
						print("Correct! The first note was: " + firstNoteGuess)
						PythonEarTrainer.updateStats(1.0)
					else:
						print("Incorrect! The first note wasn't : " + firstNoteGuess + ". It was " + randomInterval.get_first_note_name())
						PythonEarTrainer.updateStats(0.0)
			
			if not secondNoteGuess or secondNoteGuess.lower() == "r":
				secondNoteGuess = input("What do you think the second note was? Press R to hear it again ")
				if secondNoteGuess.lower() == "r":
					continue
				elif not notes.is_valid_note(secondNoteGuess):
					print("You entered: " + secondNoteGuess + ", which isn't a note. Must enter a valid note")	
					continue
				else:
					if( notes.note_to_int(secondNoteGuess) == notes.note_to_int(randomInterval.get_second_note_name()) ):
						print("Correct! The second note was: " + secondNoteGuess)
						PythonEarTrainer.updateStats(1.0)
					else:
						print("Incorrect! The second note wasn't : " + secondNoteGuess + ". It was " + randomInterval.get_second_note_name())
						PythonEarTrainer.updateStats(0.0)
			
			if not intervalGuess or intervalGuess.lower() == "r":
				intervalGuess = input("What do you think the interval (m2, P4, etc...) was? Press R to hear it again ")
				if not intervalGuess or intervalGuess.lower() == "r":
					continue
				elif( intervalGuess in randomInterval.intervalType ):
					print("Correct! The interval was: " + intervalGuess)
					PythonEarTrainer.updateStats(1.0)
				else:
					print("Incorrect! The interval wasn't : " + intervalGuess + ". It was " + str(randomInterval.intervalType))
					PythonEarTrainer.updateStats(0.0)
				break

class RandomChord:
	def __init__(self, randomRoot, chordTones, chordTonesAsNoteObjects, chordTypeList, chordName):
		# serves as root note
		self.randomRoot = randomRoot
		#  notes in the chord
		self.chordTones = chordTones
		# list of note objects is what fluidsynth needs to play
		self.chordTonesAsNoteObjects = chordTonesAsNoteObjects
		# list of possible chord types such as major, minor, augmented, ninth, suspended, etc...
		self.chordTypeList = chordTypeList
		# lydian dominant seventh, major sixth, suspended second, etc....
		self.chordName = chordName

	def __str__(self):
		return f'{self.randomRoot} {self.chordName}, which is a ' + ' chord or a '.join(self.chordTypeList) + ' chord'

class RandomInterval:
	def __init__(self, firstNote, secondNote, intervalType):
		self.firstNote = firstNote
		self.secondNote = secondNote
		self.intervalType = intervalType

	def get_first_note_name(self):
		return self.firstNote.name

	def get_second_note_name(self):
		return self.secondNote.name

# TODO add chord progression guessing
# TODO add correct/incorrect sound effects
while(True):
	if(PythonEarTrainer.firstAttempt):
		PythonEarTrainer.getSettings()
		PythonEarTrainer.firstAttempt = False
	else:
		settings = input("Press R to repeat the same settings as last time. Enter N for new settings ")
		if(settings.lower() == "n" ):
			PythonEarTrainer.getSettings()
		elif(settings.lower() == "r" ):
			PythonEarTrainer.setRandomOctave()
		else:
			raise ValueError("Need to enter R or N next time")
	if( PythonEarTrainer.isNote(PythonEarTrainer.noteChordOrInterval) ):
		PythonEarTrainer.playAndGuessRandomNote(PythonEarTrainer.getRandomNote())
	elif PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval):
		PythonEarTrainer.playAndGuessRandomChord(PythonEarTrainer.getRandomChord())
	else:
		PythonEarTrainer.playAndGuessRandomInterval(PythonEarTrainer.getRandomInterval())
		
	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonEarTrainer.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonEarTrainer.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonEarTrainer.percentCorrect) + "\n")
