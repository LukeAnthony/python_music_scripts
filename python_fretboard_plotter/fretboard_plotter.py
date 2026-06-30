# The below code was heavily influenced by and, in a few cases (especially the matlab plotting), directly copied from https://colab.research.google.com/github/diegopenilla/PythonGuitar/blob/master/How_to_learn_guitar_with_Python.ipynb#scrollTo=QqZpI0Pl9rw5
# 	and https://betterprogramming.pub/how-to-learn-guitar-with-python-978a1896a47. 
#	Thank you to Diego Penilla for making this a lot easier for me

# TODO add octaves to notes (E1, C2, etc...)
# TODO color tones of each chord the same if plotting multiple chords??
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import sys

# contains all logic to plot Plottable objects
class FretboardPlotter:
	# multiplying lists by 3 bc of populate strings method. looks 21 notes past the starting point of the strings, 
	# 	so need to make sure there's enough notes to choose from
	numFrets = 24
	whole_notes_flats = ['C' , 'Db', 'D', 'Eb', 'E', 'F', 'Gb' , 'G', 'Ab', 'A', 'Bb', 'B']*3
	whole_notes_sharps = ['C' , 'C#', 'D', 'D#', 'E', 'F', 'F#' , 'G', 'G#', 'A', 'A#', 'B']*3
	strings = {}
	tunings = {
		"guitar" : {
			"standard" : "EADGBE",
			"dropD" : "DADGBE"
		},
		"bass" : {
			"standard" : "EADG",
			"dropD" : "DADG",
			"fiveStringStandard" : "BEADG",
			"fiveStringDropD" : "BDADG",
			"fiveStringDropA": "AEADG",
		}
	}

	accidentalsToKeysMap = {
		"sharps" : ['C', 'Am', 'G', 'Em', 'D', 'Bm', 'A', 'F#m', 'E', 'C#m', 'B', 'G#m', 'F#', 'D#m', 'C#', 'A#m',],
		"flats": ['C', 'Am', 'F', 'Dm', 'Bb', 'Gm', 'Eb', 'Cm', 'Ab', 'Fm', 'Db', 'Bbm', 'Gb', 'Ebm', 'Cb', 'Abm',]
	}

	# can refer to chords here: https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py
	chordsToChordIndexesDictionary = {
		# Indexes  	 	   0     1     2    3     4    5    6      7    8     9    10    11
						#['C' , 'Db', 'D', 'Eb', 'E', 'F', 'Gb' , 'G', 'Ab', 'A', 'Bb', 'B']
		# maj scale notes  1     	   2          3    4           5          6          7

		# major triad
		#       [C  E  G]
		"maj (major triad)" : ("(R 3rd 5th)", [0, 4, 7]),
		# major 7th
		#       [C  E  G  B]
		"maj7 (major 7th)": ("(R 3rd 5th 7th)", [0, 4, 7, 11]),
		# minor triad
		#	  C  Eb G
		"m (minor triad)": ("(R b3rd 5th)", [0, 3, 7]),
		# minor 7th
		#     C  Eb  G  Bb
		"m7 (minor 7th)": ("(R b3rd 5th b7th)", [0, 3, 7, 10]),
		# minor 7th flat 5 (aka half-diminished)
		#     C  Eb  Gb  Bb
		"m7b5 (minor 7th flat 5 (aka half-diminished))": ("(R b3rd b5th b7th)", [0, 3, 6, 10]),
		# minor-major seventh
		# 		C  Eb G  B
		"m/M7 (minor-major seventh)": ("(R b3rd 5th 7th)", [0, 3, 7, 11]),
		# diminished triad
		#	  C  Eb  Gb
		"dim (diminished triad)": ("(R b3rd b5th)", [0, 3,  6]),
		# minor sixth
		# 	   C  Eb G  A
		"m6 (minor sixth)": ("(R b3rd 5th 6th)", [0, 3, 7, 9]),
		# major sixth
		# 	   C  E  G  A
		"M6 (major sixth)": ("(R 3rd 5th 6th)", [0, 4, 7, 9]),
		# dominant 7
		# 	  C  E  G  Bb
		"7 (dominant 7)": ("(R 3rd 5th b7th)", [0, 4, 7, 10]),
		# diminished seventh
		#   	 C  Eb Gb Bbb
		"dim7 (dim7)": ("(R b3rd b5th bb7th)", [0, 3, 6, 9]),
		# major 9th
		# 		 C  E  G  B   D
		"maj9 (major 9th)": ("(R 3rd 5th 7th 9th)", [0, 4, 7, 11, 2]),
		# minor 9th
		# 		 C  Eb G  Bb  D
		"m9 (minor 9th)":   ("(R b3rd 5th b7th 9th)", [0, 3, 7, 10, 2]),
		# dominant 9th
		# 		C  E  G  Bb  D
		"9 (dominant 9th)":   ("(R 3rd 5th b7th 9th)", [0, 4, 7, 10, 2]),
		# 11th 
		# 	   C  E  G  Bb  D  F
		"11 (11th)": ("(R 3rd 5th b7th 9th 11th)", [0, 4, 7, 10, 2, 5]),
		# minor 11th
		# 		  C  Eb G  Bb  D  F
		"m11 (minor 11th)":   ("(R b3rd 5th b7th 9th 11th)", [0, 3, 7, 10, 2, 5]),
		# 13th (dominant 13th)
		#        C  E  G  Bb  D  F  A
		"13 (13th (dominant 13th))":   ("(R 3rd 5th b7th 9th 11th 13th)", [0, 4, 7, 10, 2, 5, 9]),
		# minor 13th
		# 		  C  Eb G  Bb  D  F  A
		"m13 (minor 13th)":   ("(R b3rd 5th b7th 9th 11th 13th)", [0, 3, 7, 10, 2, 5, 9]),
		# major 13th
		# 		  C  E  G  B   D  A
		"maj13 (major 13th)": ("(R 3rd 5th 7th 9th 13th)", [0, 4, 7, 11, 2, 9]),
		# augmented triad
		# 		C  E  G#
		"aug (augmented triad)": ("(R 3rd #5th)", [0, 4, 8]),
		# augmented seventh/augmented minor seventh
		# 		 C  E  G#  Bb
		"m7+ (augmented seventh/augmented minor seventh)": ("(R 3rd #5th b7th)", [0, 4, 8, 10]),
		# augmented major seventh
		# 		 C   E  G#  B
		"M7+ (augmented major seventh)": ("(R 3rd #5th 7th)", [0, 4, 8, 11]),
		# suspended second triad
		#		 C  D  G
		"sus2 (suspended second triad)": ("(R 2nd 5th)", [0, 2, 7]),
		# suspended triad/suspended fourth triad
		#		C  F  G
		"sus (suspended triad/suspended fourth triad)": ("(R 4th 5th)", [0, 5, 7]),
		# suspended seventh
		# 		  C  F  G  Bb
    	"7sus4 (suspended seventh)": ("(R 4th 5th b7th)", [0, 5, 7, 10]),
		# same as above suspended seventh
		# 		  C  F  G  Bb
    	"dom7sus4 (dominant suspended seventh)": ("(R 4th 5th b7th)", [0, 5, 7, 10]),
    	# suspended flat ninth/suspended fourth flat ninth
    	#     C  F  G  Db
    	"susb9 (suspended flat ninth/suspended fourth flat ninth)": ("(R 4th 5th b9th)", [0, 5, 7, 1]),
    	# dominant flat ninth
    	#    C  E  G  Bb  Db
    	"7b9 (dominant flat ninth)": ("(R 3rd 5th b7th b9th)", [0, 4, 7, 10, 1]),
    	# dominant sharp ninth
    	# 	 C  E  G  Bb  D#
    	"7#9 (dominant sharp ninth)": ("(R 3rd 5th b7th #9th)", [0, 4, 7, 10, 3]),
    	# dominant flat five
    	#   C   E  Gb  Bb
    	"7b5 (dominant flat five)": ("(R 3rd b5th b7th)", [0, 4, 6, 10]),
    	# sixth_ninth
    	#    C  E  G  A  D
    	"6/9 (sixth_ninth)": ("(R 3rd 5th 6th 9th)", [0, 4, 7, 9, 2]),
    	# hendrix chord (7b12)
    	#    C  E  G  Bb  Eb
    	"7b12 (hendrix)": ("(R 3rd 5th b7th #9th)", [0, 4, 7, 10, 3])
	}

	scalesToScaleIndexesDictionary = {
		# Indexes: 	 	  	   0     1     2    3     4    5    6      7    8     9    10    11
							#['C' , 'Db', 'D', 'Eb', 'E', 'F', 'Gb' , 'G', 'Ab', 'A', 'Bb', 'B']
		# maj scale notes: 	   1     	   2          3    4           5          6          7

		#		   C  D  E  F  G  A  B
		"major" : ("(R 2nd 3rd 4th 5th 6th 7th)", [0, 2, 4, 5, 7, 9, 11]),
		#          C  D  Eb F  G  Ab  Bb
		"minor" : ("(R 2nd b3rd 4th 5th b6th b7th)", [0, 2, 3, 5, 7, 8, 10]),
		#          		   C  D  Eb F  G  Ab  B
		"harmonic minor": ("(R 2nd b3rd 4th 5th b6th 7th)", [0, 2, 3, 5, 7, 8, 11]),
		#         	 	  C  D  Eb F  G  A  B
		"melodic minor": ("(R 2nd b3rd 4th 5th 6th 7th)", [0, 2, 3, 5, 7, 9, 11]),
		#          C  D  Eb F  G  A  Bb
		"dorian": ("(R 2nd b3rd 4th 5th 6th b7th)", [0, 2, 3, 5, 7, 9, 10]),
		#		   	 C  Db Eb F  G  Ab Bb 
		"phrygian": ("(R b2nd b3rd 4th 5th b6th b7th)", [0, 1, 3, 5, 7, 8, 10]),
		#		   C  D  E  F#  G  A  B
		"lydian": ("(R 2nd 3rd #4th 5th 6th 7th)", [0, 2, 4, 6, 7, 9, 11]),
		#			   C  D  E  F  G  A  Bb
		"mixolydian": ("(R 2nd 3rd 4th 5th 6th b7th)", [0, 2, 4, 5, 7, 9, 10]),
		#           C  Db  Eb  F  Gb  Ab  Bb
		"locrian": ("(R b2nd b3rd 4th b5th b6th b7th)", [0, 1, 3, 5, 6, 8, 10]),
		#			  C   Db D  Eb E  F  Gb G  Ab A  Bb  B 
		"chromatic": ("(R b2nd 2nd b3rd 3rd 4th b5th 5th b6th 6th b7th 7th)", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
		#					 C  D  E  G  A
		"major pentatonic": ("(R 2nd 3rd 5th 6th)", [0, 2, 4, 7, 9]),
		#					 C  Eb F  G  Bb
		"minor pentatonic": ("(R b3rd 4th 5th b7th)", [0, 3, 5, 7, 10]),
		#				C  D  Eb E  G  A
		"major blues": ("(R 2nd b3rd 3rd 5th 6th)", [0, 2, 3, 4, 7, 9]),
		#				C  Eb F  Gb G  Bb
		"minor blues": ("(R b3rd 4th b5th 5th b7th)", [0, 3, 5, 6, 7, 10])
	}

	@staticmethod
	def get_plottable_notes(plottable):
		root = plottable.get_root()
		intervals = plottable.get_intervals()
		# TODO should use accidentals to keys map here
		containsSharps = root in FretboardPlotter.accidentalsToKeysMap["sharps"]
		rootIndex = FretboardPlotter.whole_notes_sharps.index(root) if containsSharps else FretboardPlotter.whole_notes_flats.index(root)
		noteAlphabetStartingWithThatRoot = FretboardPlotter.whole_notes_sharps[rootIndex:rootIndex+12] if containsSharps else FretboardPlotter.whole_notes_flats[rootIndex:rootIndex+12]
		return [noteAlphabetStartingWithThatRoot[i] for i in intervals]

	def populate_strings(instrument, tuning):
		strings = {i:0 for i in tuning}
		for i in strings.keys():
			# combines sharps and flats into a list of tuples with equal accidentals occupying the same index & sharps in position 0 and flats in pos 1
			# 	[('C', 'C'), ('C#', 'Db'), ('D', 'D'), ('D#', 'Eb'), ('E', 'E'), ('F', 'F'), ('F#', 'Gb'), ('G', 'G'), ('G#', 'Ab').....
			sharpsAndFlats = list(zip(FretboardPlotter.whole_notes_sharps, FretboardPlotter.whole_notes_flats))
			#start = index of the first tuple containing E|A|D|G in sharpsAndFlats
			start = [x[0] for x in sharpsAndFlats].index(i)
			# +1 for the open string
			strings[i] = sharpsAndFlats[start:start+FretboardPlotter.numFrets + 1]
		FretboardPlotter.strings = strings

	# look at plottable notes being passed in. if sharp look for sharps, if flat look for flats
	# sharps will always be first element in tuple, flats will always be second element in tuple
	def find_notes(plottable_notes, tuning):
		notes_strings = {i:0 for i in tuning}
	    # for every string 
		for string in FretboardPlotter.strings.keys():
			indexes = []
			tuplesOfStringNotes = FretboardPlotter.strings[string]
	        #iterating through the notes of the plottable and saving the indexes of the string notes that match them
			for note in plottable_notes:
				ind = -1
	            #tuplesOfStringNotes = self.strings[key]
				for index, tup in enumerate(tuplesOfStringNotes):
					if note in tup:
						ind = index
						indexes.append(ind)
	        # list notes in order of appearance on the fretboard to make it easier to debug
			indexes.sort()
			notes_strings[string] = indexes
		return notes_strings

	@staticmethod
	def plot(rootNote, scaleOrChordDegree, scaleOrChordTuple, filePath, instrument, tuning, night=True):
		numFrets = FretboardPlotter.numFrets
		nStrings = len(tuning)
		listOfPlottables = [Plottable(rootNote, scaleOrChordTuple[1])]
		graphTitle = "{} {}\n{}\n{}".format(
			rootNote, scaleOrChordDegree, scaleOrChordTuple[0],
			FretboardPlotter.get_plottable_notes(listOfPlottables[0]))

		FretboardPlotter.populate_strings(instrument, tuning)

		fig, ax = plt.subplots(2, figsize=(max(8, numFrets * 0.9), nStrings + 1))
		background = ['white', 'black']
		fretLineColor = background[night - 1]

		# index 0 = right handed, index 1 = left handed
		for index, graph in enumerate(ax):
			graph.set_facecolor(background[night])
			graph.set_axisbelow(True)
			graph.set_ylim([0.4, nStrings + 0.6])
			# board ends flush with the last fret; small gap behind the nut for the open labels
			if index == 0:
				graph.set_xlim([0.3, numFrets + 0.5])
			else:
				graph.set_xlim([-0.5, numFrets - 0.3])
			# horizontal string lines (one plot call per string keeps the multi-color cycle)
			for y in range(1, nStrings + 1):
				graph.plot([-0.7, numFrets + 0.7], [y, y], zorder=1)
			# vertical fret wires sit halfway between note slots; numFrets wires total
			# (the nut + inner wires) -- no wire after the last fret
			for w in range(numFrets):
				xw = (w + 0.5) if index == 0 else (numFrets - w - 0.5)
				if w == 0:                       # the nut
					graph.axvline(x=xw, color='gold', linewidth=5.5, zorder=2)
				elif w in (11, 12) and numFrets >= 12:  # emphasize the 12th fret
					graph.axvline(x=xw, color='gray', linewidth=4.0, zorder=2)
				else:
					graph.axvline(x=xw, color=fretLineColor, linewidth=0.5, zorder=2)

		# gather note positions
		to_plot = {}
		plottableRoots = []
		for plottable in listOfPlottables:
			plottableRoots.append(plottable.get_root())
			notes = FretboardPlotter.get_plottable_notes(plottable)
			plottableNotes = FretboardPlotter.find_notes(notes, tuning)
			if len(to_plot) == 0:
				to_plot = plottableNotes
			else:
				for key in to_plot.keys():
					to_plot[key] += plottableNotes[key]

		useFlats = any(pr in FretboardPlotter.accidentalsToKeysMap["flats"] for pr in plottableRoots)

		def bubble(graph, x, y, note, isRoot):
			graph.annotate(
				note, (x, y), color=('yellow' if isRoot else 'white'),
				weight='bold', fontsize=(14 if isRoot else 11), ha='center', va='center', zorder=3,
				bbox=dict(boxstyle='circle,pad=0.32', facecolor='#1f77b4',
						  edgecolor=('gold' if isRoot else 'none'), linewidth=(2.0 if isRoot else 0.0)))

		# fretted notes only -- skip index 0 (open string); the open note is drawn on the axis
		for y_val, stringName in zip(range(1, nStrings + 1), tuning):
			for i in to_plot[stringName]:
				if i == 0:
					continue
				noteTuple = FretboardPlotter.strings[stringName][i]
				note = noteTuple[1] if useFlats else noteTuple[0]
				isRoot = note in plottableRoots
				for index, graph in enumerate(ax):
					x = i if index == 0 else (numFrets - i)
					bubble(graph, x, y_val, note, isRoot)

		fig.suptitle(graphTitle)
		# reserve title room proportional to figure height so it never overlaps the board
		plt.subplots_adjust(top=1 - 1.25 / (nStrings + 1), hspace=0.5, left=0.05, right=0.95)
		for index, graph in enumerate(ax):
			if index == 0:                       # right handed: frets 1..numFrets left-to-right
				graph.set_xticks(range(1, numFrets + 1), range(1, numFrets + 1))
			else:                                # left handed: frets numFrets..1 left-to-right
				graph.yaxis.tick_right()
				graph.set_xticks(range(0, numFrets), range(numFrets, 0, -1))
			graph.set_yticks(range(1, nStrings + 1), list(tuning))

		# string labels: uniform size/weight for every string; circle the open-string
		# note when it's in the scale/chord (gold ring + yellow when it's the root)
		for index, graph in enumerate(ax):
			for k, label in enumerate(graph.get_yticklabels()):
				label.set_fontsize(12)
				label.set_fontweight('bold')
				stringName = list(tuning)[k]
				if 0 not in to_plot[stringName]:
					continue  # open note isn't in the scale/chord -> plain (but same size)
				openNote = FretboardPlotter.strings[stringName][0][1 if useFlats else 0]
				isRoot = openNote in plottableRoots
				label.set_color('yellow' if isRoot else 'white')
				label.set_bbox(dict(boxstyle='circle,pad=0.3', facecolor='#1f77b4',
									 edgecolor=('gold' if isRoot else 'none'),
									 linewidth=(2.0 if isRoot else 0.0)))

		plt.savefig(filePath + "/{} {} {} - {} string {}.png".format(
			rootNote, str(scaleOrChordDegree).replace("/", "|"), instrument, nStrings, tuning))
		plt.close()

# Anything that will be plotted on the fretboard
# For now, only scales and chords are supported
class Plottable:
	
	def __init__(self, root, intervals):
		self.root = root
		self.intervals = intervals

	#notes should be a list of integers corresponding to the indexes of the notes within a key that should be plotted
	def get_intervals(self) -> list[int]:
		return self.intervals

	def get_root(self) -> str:
		return self.root

# END classes
# ********************************************************************************************************************************************************
# Program Execution Logic Below

# for each note, create every chord and every scale
outputDestination = sys.argv[1]
guitar = "guitar"
bass = "bass"
standardTuning = "standard"
dropDTuning = "dropD" 
fiveStringStandardTuning = "fiveStringStandard"
fiveStringDropDTuning = "fiveStringDropD" 
fiveStringDropATuning = "fiveStringDropA"

allNotes = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb' , 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B' ]
for note in allNotes:
	for scale in FretboardPlotter.scalesToScaleIndexesDictionary.keys():
		# note, scaleOrChord, isScale, outputDestination, filePath, instrument, tuning, night=True
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), guitar, FretboardPlotter.tunings[guitar][standardTuning])
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), bass, FretboardPlotter.tunings[bass][standardTuning])
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), bass, FretboardPlotter.tunings[bass][fiveStringStandardTuning])
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), guitar, FretboardPlotter.tunings[guitar][dropDTuning])
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), bass, FretboardPlotter.tunings[bass][dropDTuning])
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), bass, FretboardPlotter.tunings[bass][fiveStringDropDTuning])
		FretboardPlotter.plot(note, scale, FretboardPlotter.scalesToScaleIndexesDictionary[scale], outputDestination.format(note, scale), bass, FretboardPlotter.tunings[bass][fiveStringDropATuning])
	for chord in FretboardPlotter.chordsToChordIndexesDictionary.keys():
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), guitar, FretboardPlotter.tunings[guitar][standardTuning])
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), bass, FretboardPlotter.tunings[bass][standardTuning])
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), bass, FretboardPlotter.tunings[bass][fiveStringStandardTuning])
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), guitar, FretboardPlotter.tunings[guitar][dropDTuning])
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), bass, FretboardPlotter.tunings[bass][dropDTuning])
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), bass, FretboardPlotter.tunings[bass][fiveStringDropDTuning])
		FretboardPlotter.plot(note, chord, FretboardPlotter.chordsToChordIndexesDictionary[chord], outputDestination.format(note, chord), bass, FretboardPlotter.tunings[bass][fiveStringDropATuning])

