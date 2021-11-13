import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.scales as scales
from mingus.containers import Note
from mingus.containers import NoteContainer
from mingus.midi import fluidsynth

def isChord(input):
	return input == "C" or input == "c"

def isNote(input):
	return input == "N" or input == "n"


class RandomNote:
	def __init__(self, randomMidi, randomFreq):
		self.randomMidi = randomMidi
		self.randomFreq = randomFreq


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




def getRandomChord(octave, range):
	print("TODO")


def getRandomNote(octave, range):
	print("TODO")





correctGuesses = 0
totalAttempts = 0
percentCorrect = 0.0

fluidsynth.init("Studio_FG460s_II_Pro_Guitar_Pack.sf2")
fluidsynth.play_Note(Note())

noteRange = int(input("Starting at E, How many notes would you like to shuffle between. Ex) 1 = (E), 2 = (E,F), 3 = (E,F,F#/Gb)... "))
if( noteRange < 1 or noteRange > 12 ):
	raise ValueError("Range must be between 1 and 12, inclusive")

noteOrChord = input("Do you want to hear a random note or chord? Enter 'N' for note, 'C' for chord ")
if( not isChord(noteOrChord) and not isNote(noteOrChord) ):
	raise ValueError("Input wasn't 'N' or 'C'")

octave = int(input("From octave do you want the lowest possible note to come from? Enter 1 for E1, 2 for E2...."))
if( octave == 0 or octave > 7 ):
	raise ValueError("Octave must be between 1 and 7, inclusive")

if( isNote(noteOrChord) ):
	getRandomNote(octave, noteRange)
else:
	getRandomChord(octave, noteRange)