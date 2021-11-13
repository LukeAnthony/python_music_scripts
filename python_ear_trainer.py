import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.scales as scales
from mingus.containers import Note
from mingus.containers import NoteContainer
from mingus.midi import fluidsynth
import random

fluidsynth.init("Studio_FG460s_II_Pro_Guitar_Pack.sf2")
correctGuesses = 0
totalAttempts = 0
percentCorrect = 0.0

class Util:
	@staticmethod
	def isChord(input):
		return input == "C" or input == "c"

	@staticmethod
	def isNote(input):
		return input == "N" or input == "n"

	@staticmethod
	def getRandomChord(octave, range):
		print(random.randint(0,11))
		print("TODO")

	@staticmethod
	def getRandomNote(octave, range):
		# https://github.com/bspaans/python-mingus/blob/master/mingus/core/notes.py#L36
		randomNote = notes.int_to_note(random.randint(0,range - 1), "b" if random.random() > .5 else "#")
		return RandomNote(randomNote, octave)
	
	@staticmethod
	def playRandomNote(randomNote):
		while True:
			fluidsynth.play_Note(randomNote.randomNote)
			guess = input("What note do you think that was? Press R to repeat it ")
			if guess == "R" or guess == "r":
				continue
			elif not notes.is_valid_note(guess):
				raise ValueError("Must enter a valid note")
			else:
				print(guess)
				print(randomNote.randomNote.name)
				if notes.note_to_int(guess) == notes.note_to_int(randomNote.randomNote.name):
					print("Correct! That note was a '" + notes.name + "'")
					break
				else:
					print("Incorrect. You guessed: '" + guess + "'. That note was a '" + randomNote.randomNote.name + "'")
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












# fluidsynth.play_Note(Note())

### TODO loop this and add in stats. add option to attempt again without re-entering choices

noteRange = int(input("Starting at C, How many notes would you like to shuffle between. Ex) 1 = (C), 2 = (C,C#), 3 = (C,Db,D)... "))
if( noteRange < 1 or noteRange > 12 ):
	raise ValueError("Range must be between 1 and 12, inclusive")

noteOrChord = input("Do you want to hear a random note or chord? Enter 'N' for note, 'C' for chord ")
if( not Util.isChord(noteOrChord) and not Util.isNote(noteOrChord) ):
	raise ValueError("Input wasn't 'N' or 'C'")

octave = int(input("From octave do you want the lowest possible note to come from? Enter 1 for E1, 2 for E2...."))
if( octave == 0 or octave > 7 ):
	raise ValueError("Octave must be between 1 and 7, inclusive")

if( Util.isNote(noteOrChord) ):
	randomNote = Util.getRandomNote(octave, noteRange)
	Util.playRandomNote(randomNote)
else:
	Util.getRandomChord(octave, noteRange)