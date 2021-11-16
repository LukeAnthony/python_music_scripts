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
	firstAttempt = True
	correctGuesses = 0.0
	totalAttempts = 0.0
	percentCorrect = ""

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
			PythonEarTrainer.octave = random.randint(2,4)
		else:
			PythonEarTrainer.octave = int(octaveString)
			if( PythonEarTrainer.octave > 6 or PythonEarTrainer.octave < 1 ):
				raise ValueError("Octave must be between 1 and 6")

	@staticmethod
	def getRandomChord(octave, range):
		print(random.randint(0,11))
		print("TODO")

	@staticmethod
	def playAndGuessRandomChord(octave, range):
		print("TODO")

	@staticmethod
	def getRandomNote(octave, range):
		# https://github.com/bspaans/python-mingus/blob/master/mingus/core/notes.py#L36
		randomNote = notes.int_to_note(random.randint(0,range - 1), "b" if random.random() > .5 else "#")
		return RandomNote(randomNote, octave)
	
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
				print()
				if notes.note_to_int(guess) == notes.note_to_int(randomNote.randomNote.name):
					print("Correct! That note was a '" + randomNote.randomNote.name + "'")
					return 1.0;
					break
				else:
					print("Incorrect. You guessed: '" + guess + "'. That note was a '" + randomNote.randomNote.name + "'")
					return 0.0;
					break
class RandomNote:
	def __init__(self, randomNote, octave):
		self.randomNote = Note(randomNote, octave)

	def return_note_and_octave_string(self):
		return self.randomNote + "-" + str(self.octave)

class RandomChord:
	def __init__(self, randomRootMidi, randomFreqs, randomChordToneMidis, majorOrMinor, triadOrSeventh):
		# serves as root note
		self.randomRootMidi = randomRootMidi
		# array of chord tones
		self.randomFreqs = randomFreqs
		# will serve to look up chord tone note names
		self.randomChordToneMidis = randomChordToneMidis
		# false = minor, true = major
		self.majorOrMinor = majorOrMinor
		#  false = triad, true = seventh
		self.triadOrSeventh = triadOrSeventh

### TODO loop this and add in stats. add option to attempt again without re-entering choices
while(True):
	if(PythonEarTrainer.firstAttempt):
		PythonEarTrainer.getSettings()
		PythonEarTrainer.firstAttempt = False
	else:
		settings = input("Press R to repeat the same settings as last time. Enter N for new settings")
		if(settings == "N" or settings == "n"):
			PythonEarTrainer.getSettings()
		elif(settings != "r" and settings != "R"):
			raise ValueError("Need to enter R or N next time")
	if( PythonEarTrainer.isNote(PythonEarTrainer.noteOrChord) ):
		randomNote = PythonEarTrainer.getRandomNote(PythonEarTrainer.octave, PythonEarTrainer.noteRange)
		points = PythonEarTrainer.playAndGuessRandomNote(randomNote)
		PythonEarTrainer.updateStats(points)
	else:
		PythonEarTrainer.getRandomChord(PythonEarTrainer.octave, PythonEarTrainer.noteRange)
	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonEarTrainer.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonEarTrainer.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonEarTrainer.percentCorrect))
	print()

