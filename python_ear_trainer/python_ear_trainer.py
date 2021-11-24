import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.scales as scales
from mingus.containers import Note
from mingus.containers import NoteContainer
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
	noteOrChord = ""
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
	chordTypes = ["triads", "sevenths", "augmented", "suspended", "sixths", "ninths", "elevenths", "thirteenths", "altered"]
	chordChoices = []
	evenChordProbability = False
	# contains a map of the chord types to the functions that generate the chords of that type. will have to pass each function the note
	chordTypesMap = { 
		# Triads: 'm', 'M', 'dim', aug, sus4, sus2
			# minor triad, major tiriad, diminished triad, augmented triad, suspended fourth triad, suspended second triad
		"triads": [chords.minor_triad, chords.major_triad, chords.diminished_triad, chords.augmented_triad, chords.suspended_fourth_triad, chords.suspended_second_triad],
		# Sevenths: 'm7', 'M7', '7', 'm7b5', 'dim7', 'm/M7', 7sus4, 7#11, 7+, m7+
			# minor 7th, major 7th, dominant 7th, half dim 7th, dim 7th, minor/major 7th, suspended 7th, lydian dominant seventh, augmented major 7th augmented minor 7th
		"sevenths": [chords.minor_seventh, chords.major_seventh, chords.dominant_seventh, chords.half_diminished_seventh, chords.diminished_seventh, chords.minor_major_seventh, chords.suspended_seventh, chords.lydian_dominant_seventh, chords.augmented_major_seventh, chords.augmented_minor_seventh ],
		# Augmented: 'aug', 'M7+'', 'm7+',
			# augmented triad, augmented major seventh, augmented minor seventh, 
		"augmented": [chords.augmented_triad, chords.augmented_major_seventh, chords.augmented_minor_seventh],
		# Suspended: 'sus4', 'sus2', '7sus4',  'susb9'
			# suspended fourth triad, suspended second triad, suspended seventh, suspended fourth ninth
		"suspended": [chords.suspended_fourth_triad, chords.suspended_second_triad, chords.suspended_seventh, chords.suspended_fourth_ninth],
		# Sixths: '6', 'm6', '6/7', '6/9'
			# major sixth, minor sixth, dominant sixth, six ninth
		"sixths": [chords.major_sixth, chords.minor_sixth, chords.dominant_sixth, chords.sixth_ninth],
		# Ninths: '9' , 'M9', 'm9', '7b9', '7#9', '6/9'
			# dominant ninth, major ninth, minor ninth, dominant flat ninth, dominant sharp ninth, sixth ninth
		"ninths": [chords.dominant_ninth, chords.major_ninth, chords.minor_ninth, chords.dominant_flat_ninth, chords.dominant_sharp_ninth, chords.sixth_ninth],
		# Elevenths: '7#11', 'm11'
			# lydian dominant 7th, minor eleventh
		"elevenths": [chords.lydian_dominant_seventh, chords.minor_eleventh],
		# Thirteenths: '13' , 'M13', 'm13'
			# dominant thirteenth, major 13th, minor 13th
		"thirteenths": [chords.dominant_thirteenth, chords.major_thirteenth, chords.minor_thirteenth],
		# Altered: '7b5', '7b9', '7#9', '6/7', '7b12'
			# dominant flat five, dominant flat ninth, dominant sharp ninth, dominant sixth, hendrix chord
		"altered": [chords.dominant_flat_five, chords.dominant_flat_ninth, chords.dominant_sharp_ninth, chords.dominant_sixth, chords.hendrix_chord]
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
	# TODO add interval guess
	def getSettings():
		# resetting choices so you don't add to a populated list
		PythonEarTrainer.chordChoices = []
		PythonEarTrainer.noteRange = int(input("Starting at C, How many notes would you like to shuffle between. Ex) 1 = (C), 2 = (C,C#), 3 = (C,Db,D)... "))
		if( PythonEarTrainer.noteRange < 1 or PythonEarTrainer.noteRange > 12 ):
			raise ValueError("Range must be between 1 and 12, inclusive")

		PythonEarTrainer.noteOrChord = input("Do you want to hear a random note or chord? Enter 'N' for note, 'C' for chord ")
		if( not PythonEarTrainer.isChord(PythonEarTrainer.noteOrChord) and not PythonEarTrainer.isNote(PythonEarTrainer.noteOrChord) ):
			raise ValueError("Input wasn't 'N' or 'C'")

		# TODO add chord choice logic here
		octaveString = input("Which octave, from 1-6, do you want to note to be in? Type R to randomize between octaves 1 and 4 (the range of a bass guitar)")
		if( octaveString.lower() == "r" ):
			PythonEarTrainer.randomizeOctave()
			PythonEarTrainer.randomizedOctave = True
		else:
			PythonEarTrainer.octave = int(octaveString)
			if( PythonEarTrainer.octave > 6 or PythonEarTrainer.octave < 1 ):
				raise ValueError("Octave must be between 1 and 6")

	@staticmethod
	def randomizeOctave():
		PythonEarTrainer.octave =  random.randint(PythonEarTrainer.randomOctaveFloor, PythonEarTrainer.randomOctaveCeiling)

	@staticmethod
	def getRandomChord(chorodTypes):
		randomRoot = PythonEarTrainer.getRandomRoot()
		randomChord = None
		

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

		print("TODO")

	@staticmethod
	# use 'tonic' method to get root https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L571
	def playAndGuessRandomChord(randomChord):
		# Need to use chords.determine https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L919 
		print("TODO")

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
					break
				else:
					print("\nIncorrect. You guessed: '" + guess + "'. That note was a '" + randomNote.randomNote.name + "-" + str(randomNote.randomNote.octave) + "'")
					PythonEarTrainer.updateStats(0.0)
					break

class RandomNote:
	def __init__(self, randomNote, octave):
		self.randomNote = Note(randomNote, octave)

	def return_note_and_octave_string(self):
		return self.randomNote + "-" + str(self.randomNote.octave)

class RandomChord:
	def __init__(self, randomRoot, chordTones, quality):
		# serves as root note
		self.randomRoot = randomRoot
		#  notes in the chord
		self.chordTones = chordTones
		# ex) major, minor, augmented, ninth, suspended, etc...
		self.quality = quality

while(True):
	if(PythonEarTrainer.firstAttempt):
		PythonEarTrainer.getSettings()
		PythonEarTrainer.firstAttempt = False
	else:

		settings = input("Press R to repeat the same settings as last time. Enter N for new settings")
		if(settings.lower() == "n" ):
			PythonEarTrainer.getSettings()
		elif(settings.lower() == "r" ):
			if(PythonEarTrainer.randomizedOctave):
				PythonEarTrainer.randomizeOctave()
				print(PythonEarTrainer.octave)
		else:
			raise ValueError("Need to enter R or N next time")
	if( PythonEarTrainer.isNote(PythonEarTrainer.noteOrChord) ):
		# TODO collapse into one method??
		PythonEarTrainer.playAndGuessRandomNote(PythonEarTrainer.getRandomNote())
	else:
		# TODO move chord choice logic to get settings
		# TODO exception handling
		# TODO adjust come up with a better input
		chordChoices = input("What chord types would you like to select from? Choices are " + str(PythonEarTrainer.chordTypes) + ".\n Type the groups you want to select from separated by a comma (ex: Ninths,Thirteenths,Triads). To select from all chord types, type 'all'.")
		# TODO better input validation
		if( chordChoices.lower() == "all" ):
			PythonEarTrainer.chordChoices = PythonEarTrainer.chordTypes
			print(PythonEarTrainer.chordChoices)
		else:
			chordChoices = chordChoices.split(',')
			for chord in chordChoices:
				if chord not in PythonEarTrainer.chordTypes:
					print("Didn't recognize input " + chord)
				#if valid chord
				else:
					PythonEarTrainer.chordChoices.append(chord)
			print(PythonEarTrainer.chordChoices)
		includeInversions = input("Y/N Do you want to include inversions?")
		if( includeInversions.lower() != "y" and includeInversions.lower() != "n" ):
			raise ValueError("Answer must be Y/N")
		PythonEarTrainer.includeInversions = includeInversions.lower() == "y"
		evenChordProbability = input("Do you want the chords in each chord type to have the same probability of appearing or for each to have the probability listed in line ___? Y for same probability, N for custom")
		if( evenChordProbability.lower() != "y" and evenChordProbability.lower() != "n" ):
			raise ValueError("Answer must be Y/N")
		PythonEarTrainer.evenChordProbability = evenChordProbability.lower() == "y"
		# TODO collapse into one method??
		PythonEarTrainer.playAndGuessRandomChord(PythonEarTrainer.getRandomChord())
	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonEarTrainer.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonEarTrainer.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonEarTrainer.percentCorrect) + "\n")

"""
Random Chord matching logic


#6 triads below
majTriad --> major triad
minTriad --> minor triad
dimTriad --> diminished triad
augTriad --> augmented triad
sus4Triad --> suspended fourth triad
sus2Triad --> suspended second triad


#27 chords below
maj7 --> major seventh
m7 --> minor seventh
dom7 --> dominant seventh
halfDim7 --> half diminished seventh
m7b5 --> half diminished seventh
dim7 --> diminished seventh
mMaj7 --> minor/major seventh
m6 --: minor sixth
maj6 --> major sixth
dom6 --> dominant sixth
sixNinth --> sixth ninth
m9 --> major ninth
maj9 --> minor ninth
dom9 --> dominant ninth
domb9 --> dominant flat ninth
dom#9 --> dominant sharp ninth 
min11 --> minor eleventh
min13 --> minor thirteenth
maj13 --> major thirteenth
dom13 --> dominant thirteenth
sus7 --> suspended seventh
sus49 --> suspended fourth ninth
augM7 --> augmented major seventh
augm7 --> augmented minor seventh
domb5(7b5) --> dominant flat five
lydianDom7 --> lydian dominant seventh
hendrixChord --> hendrix chord



chords.determine(randomChord) will print ['__root__ __chord type that = value in chord_shorthand_meaning__']
['D# suspended fourth triad'] 

need to split the string on space
	first entry in array is the note
	concat all other entries to get the chord type
	
may split according to this modified lsit which is found in the from_shorthand method
	https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L786

HOW TO DETERMINE WHAT CHORDS TO GENERATE

Each of the methods in chords.py maps to a chord_shorthand_meaning key/value
https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L111

Shorthand meaning per category with their full names below

	Triads: 'm', 'M', 'dim', aug, sus4, sus2
		minor triad, major tiriad, diminished triad, augmented triad, suspended fourth triad, suspended second triad
	Sevenths: 'm7', 'M7', '7', 'm7b5', 'dim7', 'm/M7', 7sus4, 7#11, 7+, m7+
		minor 7th, major 7th, dominant 7th, half dim 7th, dim 7th, minor/major 7th, suspended 7th, lydian dominant seventh, augmented major 7th augmented minor 7th
	Augmented: 'aug', 'M7+'', 'm7+',
		augmented triad, augmented major seventh, augmented minor seventh, 
	Suspended: 'sus4', 'sus2', '7sus4',  'susb9'
		suspended fourth triad, suspended second triad, suspended seventh, suspended fourth ninth
	Sixths: '6', 'm6', '6/7', '6/9'
		major sixth, minor sixth, dominant sixth, six ninth
	Ninths: '9' , 'M9', 'm9', '7b9', '7#9', '6/9'
		dominant ninth, major ninth, minor ninth, dominant flat ninth, dominant sharp ninth, sixth ninth
	Elevenths: '7#11', 'm11'
		lydian dominant 7th, minor eleventh
	Thirteenths: '13' , 'M13', 'm13'
		dominant thirteenth, major 13th, minor 13th
	Altered: '7b5', '7b9', '7#9', '6/7', '7b12'
		dominant flat five, dominant flat ninth, dominant sharp ninth, dominant sixth, hendrix chord

	to get full name from shorthand meaning:
		print(chords.chord_shorthand_meaning.get("7#11").lstrip(' ')) #lstrip gets rid of leading white space


Need to create a dictionary, with the key being the category and the value being a list of all of the chords.py functions that generate those kinds of chords
	







	listChordTypes = [Triads, Sevenths, Augmented chords, Suspended Chords, Sixths, Ninths, Elevenths, Thirteenths, Altered Chords]
	print("What chord types would you like to select from? Choices are [Triads, Sevenths, Augmented, Suspended, Sixths, Ninths, Elevenths, Thirteenths, Altered]. Type the groups you want to hear separated by a comma (ex: Ninths,Thirteenths,Triads). For all, type 'all'.  type  ")
	if all 
		set chord choices to chords list
	else 
		set chord choices to a list of the inputs with each comma separated chord as an entry in the list
	create a blank list called randomChordFunctions
	for each entry in chord choices
		randomChrodFunctons.append(chordTypesMap[entry]) #getting the lsit of functions for the desired categories
	generate a random number between 0 and the length of randomChordFunctions-1 to be the index
	select the function at the random index and call it using the random root generated
	...




"""