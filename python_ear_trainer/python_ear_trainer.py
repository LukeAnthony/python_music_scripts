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
	chordDifficultyLevel = 0
	includeInversions = False
	majorMinorAllocation = 0
	randomizedOctave = False
	firstAttempt = True
	correctGuesses = 0.0
	totalAttempts = 0.0
	percentCorrect = ""
	randomOctaveFloor = 2
	randomOctaveCeiling = 4

	@staticmethod
	def updateStats(points):
		PythonEarTrainer.correctGuesses += points
		PythonEarTrainer.totalAttempts += 1
		PythonEarTrainer.percentCorrect = str(round(PythonEarTrainer.correctGuesses / PythonEarTrainer.totalAttempts, 2) * 100) + "%"

	@staticmethod
	def isChord(input):
		return input == "C" or input == "c"

	@staticmethod
	def isNote(input):
		return input == "N" or input == "n"

	@staticmethod
	# TODO add interval guess
	def getSettings():
		PythonEarTrainer.noteRange = int(input("Starting at C, How many notes would you like to shuffle between. Ex) 1 = (C), 2 = (C,C#), 3 = (C,Db,D)... "))
		if( PythonEarTrainer.noteRange < 1 or PythonEarTrainer.noteRange > 12 ):
			raise ValueError("Range must be between 1 and 12, inclusive")

		PythonEarTrainer.noteOrChord = input("Do you want to hear a random note or chord? Enter 'N' for note, 'C' for chord ")
		if( not PythonEarTrainer.isChord(PythonEarTrainer.noteOrChord) and not PythonEarTrainer.isNote(PythonEarTrainer.noteOrChord) ):
			raise ValueError("Input wasn't 'N' or 'C'")

		octaveString = input("Which octave, from 1-6, do you want to note to be in? Type R to randomize between octaves 1 and 4 (the range of a bass guitar)")
		if( octaveString == "R" or octaveString == "r" ):
			PythonEarTrainer.randomizeOctave()
			PythonEarTrainer.randomizedOctave = True
		else:
			PythonEarTrainer.octave = int(octaveString)
			if( PythonEarTrainer.octave > 6 or PythonEarTrainer.octave < 1 ):
				raise ValueError("Octave must be between 1 and 6")

	@staticmethod
	def randomizeOctave():
		PythonEarTrainer.octave =  random.randint(PythonEarTrainer.randomOctaveFloor, PythonEarTrainer.randomOctaveCeiling)

	# 3 difficulty levels
	# level 1 = triads 
	# level 2 = 4 or more tone chords 
	# level 3 = triads + 4 or more tone chords
	# option to include inversiions with all levels
	@staticmethod
	def getRandomChord(difficultyLevel, playInversions):
		randomRoot = PythonEarTrainer.getRandomRoot()
		randomChord = None
		# TODO adjust come up with a better input
			#### set major/minor weight share to 70% --> major and minor split it in half
			#### set suspended weight share to 20% of what's left --> 1 - 
		# random triad  -- could be major, minor, diminished, augmented, sus2, or sus4. skew so that most of the time you get major or minor --> maybe 70%
		if( difficultyLevel == 1 ):
			diceRoll = random.random()
			# 35% chance
			if( diceRoll < 0.35 ):
				randomChord = chords.major_triad(randomRoot)
			# 35% chance
			elif( diceRoll < 0.70 ):
				randomChord = chords.minor_triad(randomRoot)
			#10% chance
			elif( diceRoll < 0.80 ):
				randomChord = chords.suspended_second_triad(randomRoot)
			#10% chance
			elif( diceRoll < 0.90 ):
				randomChord = chords.suspended_fourth_triad(randomRoot)
			#5% chance
			elif( diceroll < 0.95 ):
				randomChord = chords.augmented_triad(randomRoot)
			#5% chance
			else:
				randomChord = chords.diminished_triad(randomRoot)
			print()
		# https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L255
		# random 4 or more tone chord. 27 options: maj7, m7, dom7, halfDim7, m7b5, dim7, mMaj7, m6, maj6, dom6, sixNinth, m9, maj9, dom9, domb9, dom#9, min11, min13, maj13, dom13, sus7, sus49, augM7, augm7, domb5, lydianDom7, hendrixChord
		elif( difficultyLevel == 2 ): 
			print()
		elif( difficultyLevel == 3 ):
			# random triad or 4+ chord
			print()
		else: 
			raise ValueError("Difficulty level must be 1, 2, or 3")
		# TODO adjust math? 32% chance of inversion, if inversion 8% chance of each type (first, second, third, fourth -- fourth inversion on a triad would be regular triad so 24% chance of inversion if triad)
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

			chords.randomChord
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
			if guess == "R" or guess == "r":
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
		if(settings == "N" or settings == "n"):
			PythonEarTrainer.getSettings()
		elif(settings == "r" or settings == "R"):
			if(PythonEarTrainer.randomizedOctave):
				PythonEarTrainer.randomizeOctave()
				print(PythonEarTrainer.octave)
		else:
			raise ValueError("Need to enter R or N next time")
	if( PythonEarTrainer.isNote(PythonEarTrainer.noteOrChord) ):
		# TODO collapse into one method??
		PythonEarTrainer.playAndGuessRandomNote(PythonEarTrainer.getRandomNote())
	else:
		# TODO exception handling
		chordDifficultyLevel = int(input("Select the difficulty level between 1 and 3.\nLevel 1: Just triads\nLevel 2: Just 4 or more tone chords\nLevel 3: Both triads and 4 tone chords"))
		if( chordDifficultyLevel < 1 and chordDifficultyLevel > 3 ):
			raise ValueError("Difficulty level must be between 1 and 3")
		majorMinorAllocation = int(input("What percentage, from 0 to 100, of major/minor chords would you like to receive? Ex) Entering 100 would guarantee hearing major or minor chord, 50 would mean you'd hear a major or minor chord half the time, etc..."))
		if( majorMinorAllocation < 1 or majorMinorAllocation > 100 ):
			raise ValueError("Must enter a number between 1 and 100")
		PythonEarTrainer.chordDifficultyLevel = chordDifficultyLevel
		includeInversions = input("Y/N Do you want to include inversions?")
		if( includeInversions != "y" and includeInversions != "Y" and includeInversions != "N" and includeInversions != "n" ):
			raise ValueError("Answer must be Y|y|N|n")
		PythonEarTrainer.includeInversions = includeInversions
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

Each of the methods in chords.py maps to a chord_shorthand_meaning key/value
https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L111





chords.determine(randomChord) will print ['__root__ __chord type that = value in chord_shorthand_meaning__']
['D# suspended fourth triad'] 

need to split the string on space
	first entry in array is the note
	concat all other entries to get the chord type


HOW TO DETERMINE WHAT CHORDS TO GENERATE
	originally was determining levels based off of triads vs 4+ but that's not a great way to do it
	may split according to this modified lsit which is found in the from_shorthand method
		https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L786

	Triads: 'm', 'M', 'dim', aug, sus4, sus2
		minor triad, major tiriad, diminished triad, augmented triad, suspended fourth triad, suspended second triad
	Sevenths: 'm7', 'M7', '7', 'm7b5', 'dim7', 'm/M7', 7sus4, 7#11, 7+, m7+
		minor 7th, major 7th, dominant 7th, half dim 7th, dim 7th, minor/major 7th, suspended 7th, lydian dominant seventh, augmented major 7th augmented minor 7th
	Augmented chords: 'aug', 'M7+'', 'm7+',
		augmented triad, augmented major seventh, augmented minor seventh, 
	Suspended chords: 'sus4', 'sus2', '7sus4',  'susb9'
		suspended fourth triad, suspended second triad, suspended seventh, suspended fourth ninth
	Sixths: '6', 'm6', '6/7', '6/9'
		major sixth, minor sixth, dominant sixth, six ninth
	Ninths: '9' , 'M9', 'm9', '7b9', '7#9', '6/9'
		dominant ninth, major ninth, minor ninth, dominant flat ninth, dominant sharp ninth, sixth ninth
	Elevenths: '7#11', 'm11'
		lydian dominant 7th, minor eleventh
	Thirteenths: '13' , 'M13', 'm13'
		dominant thirteenth, major 13th, minor 13th
	Altered chords: '7b5', '7b9', '7#9', '6/7', '7b12'
		dominant flat five, dominant flat ninth, dominant sharp ninth, dominant sixth, hendrix chord
	
	listChordTypes = [Triads, Sevenths, Augmented chords, Suspended Chords, Sixths, Ninths, Elevenths, Thirteenths, Altered Chords]
	print("What chord type would you like to hear? Type all for all of them " + listChordTypes)
	if all play

"""