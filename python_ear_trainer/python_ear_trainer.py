import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.scales as scales
import mingus.core.intervals as intervals
from mingus.containers import Note
from mingus.containers import NoteContainer
from mingus.containers import Bar
from mingus.midi import fluidsynth
import random, sys, math

try:
	# can find soundfonts here https://musical-artifacts.com/
	fluidsynth.init(sys.argv[1])
except IndexError:
	print("Error. Couldn't locate soundfont file")
	exit()

class PythonEarTrainer:
	noteRange = 0
	noteChordOrInterval = ""
	octave = 0
	invertChordOrInterval = False
	firstAttempt = True
	correctGuesses = 0.0
	totalAttempts = 0.0
	percentCorrect = ""
	defaultOctaveList = [ 1, 2, 3, 4, 5, 6 ]
	octaveChoices = []
	octave = 0
	# notes are converted to int values so only listing flats here is fine
	defaultNoteList = [ "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" ]
	noteChoices = []
	# use same list and boolean for interval type choices and chord type choice
	chordOrIntervalTypeChoices = []
	moreThanOneChordOrIntervalTypeChoice = len(chordOrIntervalTypeChoices) > 1
	# a dictionary of chord names --> their mingus functions
	chordsDictionary = {
		"major triad": chords.major_triad,
		"major sixth": chords.major_sixth,
		"major seventh": chords.major_seventh,
		"major ninth": chords.major_ninth,
		"major thirteenth": chords.major_thirteenth,
		"minor triad": chords.minor_triad,
		"minor sixth": chords.minor_sixth,
		"minor seventh": chords.minor_seventh,
		"minor ninth": chords.minor_ninth,
		"minor/major seventh": chords.minor_major_seventh,
		"minor thirteenth": chords.minor_thirteenth,
		"dominant flat five": chords.dominant_flat_five,
		"dominant sixth": chords.dominant_sixth,
		"dominant seventh": chords.dominant_seventh,
		"dominant ninth": chords.dominant_ninth,
		"dominant flat ninth": chords.dominant_flat_ninth,
		"dominant sharp ninth": chords.dominant_sharp_ninth,
		"dominant thirteenth": chords.dominant_thirteenth,
		"diminished triad": chords.diminished_triad,
		"diminished seventh": chords.diminished_seventh,
		"half-diminished seventh": chords.half_diminished_seventh, 
		"augmented triad": chords.augmented_triad,
		"augmented major seventh": chords.augmented_major_seventh,
		"augmented minor seventh": chords.augmented_minor_seventh,
		"suspended second triad": chords.suspended_second_triad,
		"suspended fourth triad": chords.suspended_fourth_triad,
		"suspended fourth ninth": chords.suspended_fourth_ninth,
		"suspended seventh": chords.suspended_seventh,
		"six ninth": chords.sixth_ninth,
		"eleventh": chords.eleventh,
		"minor eleventh": chords.minor_eleventh,
		"lydian dominant seventh": chords.lydian_dominant_seventh,
		"hendrix chord": chords.hendrix_chord
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
	
	@staticmethod
	def updateStats(points):
		PythonEarTrainer.correctGuesses += points
		PythonEarTrainer.totalAttempts += 1
		PythonEarTrainer.percentCorrect = str(round(PythonEarTrainer.correctGuesses / PythonEarTrainer.totalAttempts, 2) * 100) + "%"

	@staticmethod
	def isChord(input):
		return input.lower() == "c"

	@staticmethod
	def isProgression(input):
		return input.lower() == "p"

	@staticmethod
	def isNote(input):
		return input.lower() == "n"

	@staticmethod
	def isInterval(input):
		return input.lower() == "i"

	"""
		TODO Update 
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
		PythonEarTrainer.noteChoices = []

		PythonEarTrainer.noteChordOrInterval = input("\nDo you want to hear a random note, a random chord, or a random interval? Enter 'N' for note, 'C' for chord, 'I' for interval ")
		if( not PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval) and not PythonEarTrainer.isNote(PythonEarTrainer.noteChordOrInterval) and not PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval) ):
			raise ValueError("Input wasn't 'N','C', or 'I")
		
		noteRange = input("\nWhich notes would you like the program to randomly choose between?\nEnter them separated by commas (ex: C,Eb,G#,F).\nOr enter 'all' to shuffle between all notes.\nOr enter a range of numbers, from 1-12 in the format 'x-y' with C=1 and B=12, to shuffle between those (ex: 1-5 to shuffly between C,C#,D,D#,E) " )
		if noteRange.lower() == "all":
			PythonEarTrainer.noteChoices = PythonEarTrainer.defaultNoteList
		else:
			numRange = '-' in noteRange
			# if entered x-y (1-6, 2-4)
			if numRange:
				noteRangeSplit = noteRange.split('-')
				if len(noteRangeSplit) != 2:
					raise ValueError("Incorrectly entered range of numbers. Must be in format 'x-y")
				else:
					floor = int(noteRangeSplit[0]) - 1
					ceiling = int(noteRangeSplit[1])
					for x in range( floor, ceiling):
						PythonEarTrainer.noteChoices.append(notes.int_to_note(x))
			# if entered C,D,E...0
			else:
				noteRangeSplit = noteRange.split(',')
				for note in noteRangeSplit:
					if not notes.is_valid_note(note):
						raise ValueError("Don't recognzie note: " + note)
					else:
						PythonEarTrainer.noteChoices.append(note)

		octaveString = input("\nWhich octave(s), from 1-6, do you want to the program to randomly place the note/chord/root of the interval in? Type the octaves separated by a comma (ex: 1,2,3).\nType 'all' to randomly choose between octaves 1-6 ")
		if( octaveString.lower() == "all" ):
			PythonEarTrainer.octaveChoices = PythonEarTrainer.defaultOctaveList
		else:
			octaveChoices = octaveString.split(",")
			for octaveChoice in octaveChoices:
				octaveChoiceInt = int(octaveChoice)
				if octaveChoiceInt not in PythonEarTrainer.defaultOctaveList:
					raise ValueError("Don't recognize octave : " + octaveChoice)
				else:
					PythonEarTrainer.octaveChoices.append(octaveChoiceInt)
			# if no input was recognized
			if( not PythonEarTrainer.octaveChoices ):
				raise ValueError("Must input at least one random octave choice")
		PythonEarTrainer.setRandomOctave()

		if PythonEarTrainer.isInterval(PythonEarTrainer.noteChordOrInterval) or PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval):
			if PythonEarTrainer.isInterval( PythonEarTrainer.noteChordOrInterval ):
				intervalChoices = input("\nWhat intervals types would you like a random selection to be made from? Choices are: " + str(list(PythonEarTrainer.intervalTypesDictionary.keys())) + ".\nType the intervals separated by a comma (ex: major second, perfect fifth).\nTo select all interval types, type 'all'.\nNOTE: Choosing to include inversions later will add an additional interval type for every interval chosen here ")
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
				chordChoices = input("\nWhat chords would you like a random selection to be made from? Choices are\n\n " + str(list(PythonEarTrainer.chordsDictionary.keys())) + ".\n\nType the chords you want to select from separated by a comma (ex: Ninths,Thirteenths,Triads).\nTo select from all chord types, type 'all'. ")
				# TODO better input validation
				if( chordChoices.lower() == "all" ):
					PythonEarTrainer.chordOrIntervalTypeChoices = PythonEarTrainer.chordsDictionary.keys()
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = True
				else:
					chordChoices = chordChoices.split(',')
					for chord in chordChoices:
						if chord not in PythonEarTrainer.chordsDictionary.keys():
							print("Didn't recognize chord type: " + chord)
						#if valid chord
						else:
							PythonEarTrainer.chordOrIntervalTypeChoices.append(chord)
					PythonEarTrainer.moreThanOneChordOrIntervalTypeChoice = len(PythonEarTrainer.chordOrIntervalTypeChoices) > 1

			# both intervals and chords have the option to include inversions
			invertChordOrInterval = input("\nY/N Do you want to include inversions? ")
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
			listOfChordFunctions.append(PythonEarTrainer.chordsDictionary[chordType])
		# giving each chord an equal chance of being selected
		randomChord = listOfChordFunctions[random.randrange(len(listOfChordFunctions))](randomRoot)
		# DEBUG to see what the root and chord tones are
		# print("random root = " + str(randomRoot))
		# print("Random chord = " + str(randomChord))
		if( PythonEarTrainer.invertChordOrInterval ):
			secondDiceRoll = random.random()
			# will always invert given these odds. 
			# adjust odds manually as needed to mix inversions in with regular chords
			# TODO maybe have user pass in odds of inversion??
			if( secondDiceRoll < 0.00 ):
				pass
			elif( secondDiceRoll < 0.34 ):
				randomChord = chords.first_inversion(randomChord)
			elif( secondDiceRoll < 0.67 ):
				randomChord = chords.second_inversion(randomChord)
			else:
				randomChord = chords.third_inversion(randomChord)
		randomChordAsNoteObjects = []
		currentOctaveAboveRoot = 0
		# mingus' note_to_int + 12 for every octave higher than lowest octave in the chord
		previousNoteValue = 0
		for tone in randomChord:
			randomChordAsNoteObjectsIndex = len(randomChordAsNoteObjects) - 1
			toneValue = notes.note_to_int(tone)
			# if first note of the chord
			if randomChordAsNoteObjectsIndex == -1:
				toneAsNote = Note(tone, PythonEarTrainer.octave, None, 110, 1)
				randomChordAsNoteObjects.append(toneAsNote)
			else:
				previousNote = randomChordAsNoteObjects[randomChordAsNoteObjectsIndex]
				previousNoteOctave = previousNote.octave
				toneDistanceFromPreviousNote = toneValue - previousNoteValue
				if toneDistanceFromPreviousNote < 0:
					# TODO see if this works with inversions??
					while toneValue - previousNoteValue < 0:
						toneValue = toneValue + 12
						currentOctaveAboveRoot = currentOctaveAboveRoot + 1
				toneAsNote = Note(tone, PythonEarTrainer.octave + currentOctaveAboveRoot, None, 110, 1)
				randomChordAsNoteObjects.append(toneAsNote)
			previousNoteValue = toneValue
			currentOctaveAboveRoot = 0
			# DEBUG to see each tone in the chord, each tone's numerical note value, and each tone's octave
			# ex) Tone = C# tone value = 1 tone octave = 3
			#      Tone = E tone value = 4 tone octave = 3
			#      Tone = G tone value = 7 tone octave = 3
			# print("Tone = " + str(toneAsNote.name) + " tone value = " + str(toneValue) + " tone octave = " + str(toneAsNote.octave))
		#.determine() returns all matching names in list. first entry is most accurate. excluding root note in the chord name since we already have it
		chordName = ' '.join(chords.determine(randomChord)[0].split(' ')[1:])
		return RandomChord(randomRoot, randomChord, randomChordAsNoteObjects, chordName)

	@staticmethod
	# use 'tonic' method to get root https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L571
	# Need to use chords.determine https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L919 
	def playAndGuessRandomChord():
		randomChord = PythonEarTrainer.getRandomChord()
		b = Bar()
		# placing the chord as two half notes in the bar
		b.place_notes(randomChord.chordTones, 2)
		b.place_notes(randomChord.chordTones, 2)
		rootGuess = ""
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
			if not nameGuess or nameGuess.lower() == "r":
				nameGuess = input("Excluding the root, what is the name of this chord?\nYour choices are:\n\t" + str(PythonEarTrainer.chordOrIntervalTypeChoices) + "\nPress R to repeat it ")
				if(nameGuess.lower() == "r"):
					continue

			print("\nThat chord was a: " + str(randomChord))

			if(notes.note_to_int(rootGuess) == notes.note_to_int(randomChord.randomRoot)):
				PythonEarTrainer.updateStats(1.0)
				print("You were correct. The root is: " + rootGuess)
			else:
				print("Incorrect. You guessed: " + rootGuess + ". The root was: " + randomChord.randomRoot)
				PythonEarTrainer.updateStats(0.0)

			if(nameGuess == randomChord.chordName):
				PythonEarTrainer.updateStats(1.0)
				print("You were correct. The chord name is: " + nameGuess)
			else:
				print("Incorrect. You guessed: " + nameGuess + ". The chord name was: " + randomChord.chordName)
				PythonEarTrainer.updateStats(0.0)
			break

	@staticmethod
	def getRandomProgression():
		return None 

	@staticmethod
	def playAndGuessRandomProgression():
		return None 

	@staticmethod
	def getRandomNote():
		randomRoot = PythonEarTrainer.getRandomRoot()
		return Note(randomRoot, PythonEarTrainer.octave, None, 127, 1)

	@staticmethod
	def getRandomRoot():
		return PythonEarTrainer.noteChoices[random.randint(0, len(PythonEarTrainer.noteChoices) - 1)]
		# https://github.com/bspaans/python-mingus/blob/master/mingus/core/notes.py#L36
		# return notes.int_to_note(random.randint(0, PythonEarTrainer.noteRange - 1), "b" if random.random() > .5 else "#")

	@staticmethod
	def playAndGuessRandomNote():
		randomNote = PythonEarTrainer.getRandomNote()
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
		# TODO logic for perfect octave
		intervalType = intervals.determine( firstNoteName, secondNoteName )
		return PythonEarTrainer.intervalNamesToAbbreviations[intervalType]

	@staticmethod
	def getRandomInterval():
		# TODO replace this with getRandomNote???
		randomRootNote = Note( PythonEarTrainer.getRandomRoot(), PythonEarTrainer.octave, None, 105, 1 )
		randomRootName = randomRootNote.name
		listOfIntervalFunctions = []
		for intervalType in PythonEarTrainer.chordOrIntervalTypeChoices:
			listOfIntervalFunctions.append(PythonEarTrainer.intervalTypesDictionary[intervalType])
		# giving each interval an equal chance of being selected
		randomIntervalFunction = listOfIntervalFunctions[random.randrange(len(listOfIntervalFunctions))]
		#randomIntervalName = listOfIntervalFunctions[random.randrange(len(listOfIntervalFunctions))](randomRootName)
		randomIntervalName = randomIntervalFunction(randomRootName)
		secondNoteOctave = PythonEarTrainer.octave if (notes.note_to_int(randomIntervalName) - notes.note_to_int(randomRootName) > 0 ) else PythonEarTrainer.octave + 1
		if( PythonEarTrainer.invertChordOrInterval ):
			diceRoll = random.random()
			# 50% chance to invert
			# TODO adjust odds as needed
			if( diceRoll < 0.5 ):
				# returns an inverted interval
				return RandomInterval( Note( randomIntervalName, secondNoteOctave, None, 105, 1 ), randomRootNote, PythonEarTrainer.calculateIntervalType( randomIntervalName, randomRootName ) )
			else:
				# returns the normal interval
				return RandomInterval( randomRootNote, Note( randomIntervalName, secondNoteOctave, None, 105, 1 ), PythonEarTrainer.calculateIntervalType( randomRootName, randomIntervalName ) )
		else:
			# TODO bug where, if user doesnt want inversions but supplies only one octave to be randomized from, second note placed lower than first if the random interval type would have reached into the next octave
			# need to subtract first note from the second. if negative, second note should be up an octave
				# https://144notes.org/bass-guitar/
			# if secondNote - firstNote = 0, would be same note. should do a 50-50 coin flip for unison or perfect octave
			return RandomInterval( randomRootNote, Note( randomIntervalName, secondNoteOctave, None, 105, 1 ), PythonEarTrainer.calculateIntervalType( randomRootName, randomIntervalName ) )

	@staticmethod
	def playAndGuessRandomInterval():
		randomInterval = PythonEarTrainer.getRandomInterval()
		b = Bar()
		# quarter note each
		b.place_notes(randomInterval.get_first_note_name_and_octave(), 2)
		b.place_notes(randomInterval.get_second_note_name_and_octave(), 2)
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

class RandomProgression:
	def __init__(self, key, progressionInRomanNumerals, listOfChordsPerBar ):
		# the key that the progression is derived from
		# ex) Cm, E....
		self.key = key
		self.progressionInRomanNumerals = progressionInRomanNumerals
		# list of chords that make up each bar of the progression
		# ex) 12 bar blues in E = [E,E,E,E,A,A,E,E,B,A,E,E]
		# TODO these should probably be chord objects
		self.listOfChordsPerBar = listOfChordsPerBar

	def __str__(self):
		return f'{self.progressionInRomanNumerals} in {self.key}: {self.listOfChordsPerBar}'

class RandomChord:
	def __init__(self, randomRoot, chordTones, chordTonesAsNoteObjects, chordName):
		# serves as root note
		self.randomRoot = randomRoot
		#  notes in the chord
		self.chordTones = chordTones
		# list of note objects is what fluidsynth needs to play
		self.chordTonesAsNoteObjects = chordTonesAsNoteObjects
		# lydian dominant seventh, major sixth, suspended second, etc....
		self.chordName = chordName

	def __str__(self):
		return f'{self.randomRoot} {self.chordName}: Tones={self.chordTones}, note objects = {self.chordTonesAsNoteObjects}' 

class RandomInterval:
	def __init__(self, firstNote, secondNote, intervalType):
		self.firstNote = firstNote
		self.secondNote = secondNote
		self.intervalType = intervalType

	def get_first_note_name(self):
		return self.firstNote.name

	def get_first_note_name_and_octave(self):
		return self.firstNote.name + "-" + str(self.firstNote.octave)

	def get_second_note_name(self):
		return self.secondNote.name

	def get_second_note_name_and_octave(self):
		return self.secondNote.name + "-" + str(self.secondNote.octave)

# TODO add chord progression guessing
	# user input a list of possible keys
	# randomly generate a chord progression from a list of popular chord progressions
	# play those chords in the order of the progression
	# have the user guess what the key is, what the progression is, and what the chords are
# TODO chord tone removal guessing game
	# User enters a list of possible root notes, chord types, and the number of possible notes 
	# randomly generate a chord
	# play the full chord. then remove a note or notes from it 
	# user guesses 
		# the original chord name
		# the tones in the original chord
		# the tones removed from the chord 
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
	if( PythonEarTrainer.isNote(PythonEarTrainer.noteChordOrInterval)):
		PythonEarTrainer.playAndGuessRandomNote()
	elif PythonEarTrainer.isChord(PythonEarTrainer.noteChordOrInterval):
		PythonEarTrainer.playAndGuessRandomChord()
	else:
		PythonEarTrainer.playAndGuessRandomInterval()
	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonEarTrainer.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonEarTrainer.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonEarTrainer.percentCorrect) + "\n")