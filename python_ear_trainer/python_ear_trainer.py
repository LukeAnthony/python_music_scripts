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
		# random triad  -- could be major, minor, diminished, or augmented. skew so that most of the time you get major or minor --> maybe 70#
		if( difficultyLevel == 1 ):
			diceRoll = random.random()
			# 35% chance
			if( diceRoll < 0.35 ):
				randomChord = chords.major_triad(randomRoot)
			# 35% chance
			elif( diceRoll < 0.70 ):
				randomChord = chords.minor_triad(randomRoot)
			#15% chance
			elif( diceRoll < 0.85 ):
				randomChord = chords.diminished_triad(randomRoot)
			#15% chance
			else:
				randomChord = chords.augmented_triad(randomRoot)
			print()
		# random 4 or more tone chord. could be 
		elif( difficultyLevel == 2 ):
			# random 4 or more tones
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
	def playAndGuessRandomChord(randomChord):
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
	def __init__(self, randomRoot, numNotes, quality):
		# serves as root note
		self.randomRoot = randomRoot
		#  number of notes in the chord
		self.numNotes = numNotes
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
		PythonEarTrainer.chordDifficultyLevel = chordDifficultyLevel
		includeInversions = input("Y/N Do you want to include inversions?")
		if( includeInversions != "y" and includeInversions != "Y" and includeInversions != "N" and includeInversions != "n" ):
			raise ValueError("Answer must be Y|y|N|n")
		PythonEarTrainer.includeInversions = includeInversions
		# TODO collapse into one method??
		PythonEarTrainer.playAndGuessRandomChord(PythonEarTrainer.getRandomChord())
	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonEarTrainer.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonEarTrainer.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonEarTrainer.percentCorrect) + "\n")

