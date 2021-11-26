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
	includeInversions = False
	majorMinorAllocation = 0
	randomizedOctave = False
	firstAttempt = True
	correctGuesses = 0.0
	totalAttempts = 0.0
	percentCorrect = ""
	randomOctaveFloor = 2
	randomOctaveCeiling = 4
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
		"perfect unison" : intervals.major_unison,
		"minor second" : intervals.minor_second,
		"major second" : intervals.major_second,
		"minor third" : intervals.minor_third,
		"major third" : intervals.major_third,
		"perfect fourth" : intervals.perfect_fourth,
		"augmented fourth" : intervals.minor_fifth,
		"diminished fifth" : intervals.minor_fifth, # looks like mingus uses the minor fifth function for both names
		"perfect fifth" : intervals.perfect_fifth,
		"minor sixth" : intervals.minor_sixth,
		"major sixth" : intervals.major_sixth,
		"minor seventh" : intervals.minor_seventh,
		"major seventh" : intervals.major_seventh
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

	@staticmethod
	
	# TODO build out decision tree 
	"""
		Decision Tree:
			Decide note, chord, or interval
			Decide which octave to play it in
			decide which range of notes you want to hear
			if interval or chord
				decide if you want to include inversions
				if interval
					decide which intervals you'd like to hear (perfect unison to major seventh)
				if chord
					decide which chord types to choose from
	"""
	def getSettings():
		# resetting choices so you don't add to a populated list
		PythonEarTrainer.chordorIntervalTypeChoices = []

		PythonEarTrainer.noteChordOrInterval = input("Do you want to hear a random note, a random chord, or a random interval? Enter 'N' for note, 'C' for chord, 'I' for interval ")
		if( not PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval) and not PythonEarTrainer.isNote(PythonEarTrainer.noteChordOrInterval) and not PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval) ):
			raise ValueError("Input wasn't 'N','C', or 'I")
		
		PythonEarTrainer.noteRange = int(input("Starting at C, How many notes would you like to shuffle between. Ex) 1 = (C), 2 = (C,C#), 3 = (C,Db,D)... " ))
		if( PythonEarTrainer.noteRange < 1 or PythonEarTrainer.noteRange > 12 ):
			raise ValueError("Range must be between 1 and 12, inclusive")

		octaveString = input("Which octave, from 1-6, do you want to note/chord/interval to be in? Type R to randomize between octaves 1 and 4 (the range of a bass guitar) ")
		if( octaveString.lower() == "r" ):
			PythonEarTrainer.randomizeOctave()
			PythonEarTrainer.randomizedOctave = True
		else:
			if( PythonEarTrainer.octave > 6 or PythonEarTrainer.octave < 1 ):
				raise ValueError("Octave must be between 1 and 6")
			PythonEarTrainer.octave = int(octaveString)
			PythonEarTrainer.randomizedOctave = False

		# both intervals and chords have the option to include inversions
		if PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval) or PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval):
			if PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval)
				intervalChoices = input("What intervals types would you like a random selection to be made from? Choices are: " + str(list(PythonEarTrainer.intervalTypesDictionary.keys())) + ".\nType the intervals separated by a comma (ex: major second, perfect fifth). To select all interval types, type 'all'. ")
				if( intervalChoices.lower() == "all" ):
					PythonEarTrainer.
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
							print("Didn't recognize input " + chord)
						#if valid chord
						else:
							PythonEarTrainer.chordOrIntervalTypeChoices.append(chord)
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = len(PythonEarTrainer.chordOrIntervalTypeChoices) > 1
			
			includeInversions = input("Y/N Do you want to include inversions? ")
			if( includeInversions.lower() != "y" and includeInversions.lower() != "n" ):
				raise ValueError("Answer must be Y/N")
			PythonEarTrainer.includeInversions = includeInversions.lower() == "y"

	@staticmethod
	def randomizeOctave():
		PythonEarTrainer.octave =  random.randint(PythonEarTrainer.randomOctaveFloor, PythonEarTrainer.randomOctaveCeiling)

	@staticmethod
	def getRandomChord():
		randomRoot = PythonEarTrainer.getRandomRoot()
		listOfChordFunctions = []
		for chordType in PythonEarTrainer.chordOrIntervalTypeChoices:
			listOfChordFunctions.extend(PythonEarTrainer.chordTypesDictionary[chordType][1])
		randomChord = listOfChordFunctions[random.randrange(len(listOfChordFunctions))](randomRoot)
		# TODO adjust math? 32% chance of inversion, if inversion 8% chance of each type (first, second, third, fourth -- fourth inversion on a triad would be regular triad so 24% chance of inversion if triad)
		# could add "always invert" option or adjust probability manually here
		if( PythonEarTrainer.includeInversions ):
			secondDiceRoll = random.random()
			if( secondDiceRoll < 0.68 ):
				pass
			elif( secondDiceRoll < 0.76 ):
				randomChord = chords.first_inversion(randomChord)
			elif( secondDiceRoll < 0.84 ):
				randomChord = chords.second_inversion(randomChord)
			elif( secondDiceRoll < 0.92 ):
				randomChord = chords.third_inversion(randomChord)
			else:
				randomChord = chords.fourth_inversion(randomChord)
		randomChordAsNoteObjects = []
		for tone in randomChord:
			toneAsNote = Note(tone, PythonEarTrainer.octave)
			randomChordAsNoteObjects.append(toneAsNote)
		#.determine returns all matching names in list. first entry is most accurate. excluding root note in the chord name since we already have it
		chordName = ' '.join(chords.determine(randomChord)[0].split(' ')[1:])
		print(chordName)
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
		print(randomChord)
		b = Bar()
		# placing the chord as a half note in the bar
		b.place_notes(randomChord.chordTones, 2)
		rootGuess = ""
		typeGuess = ""
		nameGuess = ""
		while True:
			# play bar on channel 1 at 60bpm
			fluidsynth.play_Bar(b, 1, 60)

			if not rootGuess or rootGuess.lower() == "r":
				rootGuess = input("What do you think the root of that chord was? Press R to repeat it ")
				if(rootGuess.lower() == "r"):
					continue
			# only ask if user entered 'all' or more than one type and if a guess hasn't been made already/if user asked to repeat the chord
			if (not typeGuess or typeGuess.lower() == "r") and PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice:
				typeGuess = input("What do you think the type of that chord (triad, augmented, suspended, etc...)? Press R to repeat it ")
				if(typeGuess.lower() == "r"):
					continue
			if not nameGuess or nameGuess.lower() == "r":
				nameGuess = input("Excluding the root, what was the name of that chord (suspended second, major sixth, etc...)? Press R to repeat it ")
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
					print("Incorrect. You guessed: " + typeGuess + ". The chord type(s) were: " + randomChord.chordTypeList)
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
		return RandomNote(randomRoot, PythonEarTrainer.octave)

	@staticmethod
	def getRandomRoot():
		# https://github.com/bspaans/python-mingus/blob/master/mingus/core/notes.py#L36
		return notes.int_to_note(random.randint(0, PythonEarTrainer.noteRange - 1), "b" if random.random() > .5 else "#")

	@staticmethod
	def playAndGuessRandomNote(randomNote):
		while True:
			fluidsynth.play_Note(randomNote.randomNote)
			guess = input("What note do you think that was? Press R to repeat it ").upper()
			if guess.lower() == "r":
				continue
			elif not notes.is_valid_note(guess):
				raise ValueError("You entered: " + guess + ", which isn't a note. Must enter a valid note")
			else:
				if notes.note_to_int(guess) == notes.note_to_int(randomNote.randomNote.name):
					print("\nCorrect! That note was a '" + randomNote.randomNote.name + "'")
					PythonEarTrainer.updateStats(1.0)
				else:
					print("\nIncorrect. You guessed: '" + guess + "'. That note was a '" + randomNote.randomNote.name + "-" + str(randomNote.randomNote.octave) + "'")
					PythonEarTrainer.updateStats(0.0)
			break

	@staticmethod
	def getRandomInterval():
		print("TODO")

	@staticmethod
	def playAndGuessRandomInterval(randomInterval):
		print("TODO")

class RandomNote:
	def __init__(self, randomNote, octave):
		self.randomNote = Note(randomNote, octave)

	def return_note_and_octave_string(self):
		return self.randomNote + "-" + str(self.randomNote.octave)

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

# TODO add chord progression guessing
# TODO add inversions to interval guessing
while(True):
	if(PythonEarTrainer.firstAttempt):
		PythonEarTrainer.getSettings()
		PythonEarTrainer.firstAttempt = False
	else:
		settings = input("Press R to repeat the same settings as last time. Enter N for new settings ")
		if(settings.lower() == "n" ):
			PythonEarTrainer.getSettings()
		elif(settings.lower() == "r" ):
			if(PythonEarTrainer.randomizedOctave):
				PythonEarTrainer.randomizeOctave()
		else:
			raise ValueError("Need to enter R or N next time")
	if( PythonEarTrainer.isNote(PythonEarTrainer.noteChordOrInterval) ):
		PythonEarTrainer.playAndGuessRandomNote(PythonEarTrainer.getRandomNote())
	else if PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval):
		PythonEarTrainer.playAndGuessRandomChord(PythonEarTrainer.getRandomChord())
	else:
		PythonEarTrainer.playAndGuessRandomInterval(PythonEarTrainer.getRandomInterval())
		
	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonEarTrainer.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonEarTrainer.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonEarTrainer.percentCorrect) + "\n")

"""
Random interval guessing logic below:
	....

"""