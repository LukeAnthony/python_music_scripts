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
		containsSharps = '#' in root
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
			strings[i] = sharpsAndFlats[start:start+21]
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
	#index 0 = right handed plot, index 1 = left handed plot
	def plot(plottables, graphTitle, filePath, instrument, tuning, night=True):
		FretboardPlotter.populate_strings(instrument, tuning)
		#creating two plots, top right handed, bottom left handed
		fig, ax = plt.subplots(2, figsize=(21,6))
		background = ['white', 'black']
		# creates 6 lines in each plot for the 6 strings
		for i in range(1,7):
			for index, graph in enumerate(ax):
				graph.plot([i for a in range(22)])
				graph.set_axisbelow(True)
				#setting height and width of displayed guitar
				if index == 0:
					graph.set_xlim([0.45, 21])
				elif index == 1:
					graph.set_xlim([0, 20.1])
				graph.set_ylim([0.4, 6.5])
				graph.set_facecolor(background[night])
		
		#creates the lines to simulate the fretboard in each graph
		for i in range(1,21):
			for index, graph in enumerate(ax):
				# draw gray line completely around 12 fret
				if (index == 0 and (i == 12 or i ==13)) or (index == 1 and (i == 8 or i == 9)):
					graph.axvline(x=i, color='gray', linewidth=4.5)
				# draw gold line before first fret to symbolize open notes
				elif (i == 1 and index == 0) or (i == 20 and index == 1):
					graph.axvline(x=i if index == 1 else i-.2, color='gold', linewidth=6.5)
				else:
					graph.axvline(x=i, color=background[night-1], linewidth=0.5)

		to_plot  = {}
		plottableRoots = []
		for plottable in plottables:
			plottableRoots.append(plottable.get_root())
			#ex) notes = ['C', 'E', 'G']
			notes = FretboardPlotter.get_plottable_notes(plottable)
			#ex) plottableNootes = {'E': [0, 3, 8, 12, 15, 20], 'A': [3, 7, 10, 15, 19], 'D': [2, 5, 10, 14, 17], 'G': [0, 5, 9, 12, 17]
			plottableNotes = FretboardPlotter.find_notes(notes, tuning)
			# need to combine the dictionary lists together for multiple plottables
			if len(to_plot) == 0:
				to_plot = plottableNotes
			else:
				for key in to_plot.keys():
					to_plot[key] += plottableNotes[key]

		#find_notes returns a map of strings with the indexes of the notes that are in the given scale
			#ex: to_plot(C major scale) = {'E': [19, 17, 15, 13, 12, 10, 8, 7, 5, 3, 1, 0], 'A': [19, 17, 15, 14, 12, 10, 8, 7, 5, 3, 2, 0]...
			# below for loop iterates through EADGBE keys of the map

		#need to create a list of 1-n where n is number of strings or the length of the tuning string
		for y_val, stringName in zip(list(range(1, len(tuning) + 1)), tuning):
			#  looks up the values corresponding to EADGBE keys of find_notes map aka the indexes of the notes that were in the given scale
			# ex) iterating through to_plot[E] = [19, 17, 15, 13, 12, 10, 8, 7, 5, 3, 1, 0]
			for i in to_plot[stringName]:
				font = 12
				color = 'w'
				circleSize = 0.2
				# i = 0 means an open string note (E,A,D,G)
				xLefty = (21 - i - 0.7) if i == 0 else (21 - i - 0.45)
				xRighty = (i + 0.55) if i == 0 else (i + 0.55)
				# strings is a map of each string and their notes. 
				# gets the list of notes for a given string and looks up the note at the index
				noteTuple = FretboardPlotter.strings[stringName][i]
				note = noteTuple[1] if any(pr in FretboardPlotter.accidentalsToKeysMap["flats"] for pr in plottableRoots) else noteTuple[0]
				# make the root slightly larger and yellow
				if(note in plottableRoots):
					font = 15
					color = 'yellow'
					circleSize = 0.3
				for index, graph in enumerate(ax):
					p = mpatches.Circle((xRighty if index == 0 else xLefty, y_val), circleSize)
					graph.add_patch(p)
					graph.annotate(note, (xRighty if index == 0 else xLefty, y_val), color=color, weight='bold', fontsize=font, ha='center', va='center')

		fig.suptitle(graphTitle)
		# adding more space between the two graphs
		plt.subplots_adjust(None, None, None, None, None, 0.5)
		for index, graph in enumerate(ax):
			if index == 0:
				graph.set_xticks(np.arange(21)+0.45, np.arange(0,21))
			elif index == 1:
				graph.yaxis.tick_right()
				graph.set_xticks(np.arange(21)+0.45, np.arange(20,-1,-1))
			if instrument == "guitar":
				graph.set_yticks(np.arange(1,7), list(tuning))
			elif instrument == "bass" and "fiveString" in tuning:
				 graph.set_yticks(np.arange(1,5),list(tuning))
			elif instrument == "bass":
				 graph.set_yticks(np.arange(1,5), list(tuning))
			else: raise ValueError("{} or {} not recognized as tunings or instruments".format(instrument, tuning))
		#plt.show()
		plt.savefig(filePath)
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
allNotes = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb' , 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B' ]
for note in allNotes:
	for scale in FretboardPlotter.scalesToScaleIndexesDictionary.keys():
		listOfPlottables = []
		plottable = Plottable(note,FretboardPlotter.scalesToScaleIndexesDictionary[scale])
		listOfPlottables.append(plottable)
		graphTitle = "{} {}\n{}".format(note, scale, FretboardPlotter.get_plottable_notes(plottable))
		print(graphTitle)
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "guitar", FretboardPlotter.tunings["guitar"]["standard"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "bass", FretboardPlotter.tunings["bass"]["standard"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "bass", FretboardPlotter.tunings["bass"]["fiveStringStandard"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "guitar", FretboardPlotter.tunings["guitar"]["dropD"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "bass", FretboardPlotter.tunings["bass"]["dropD"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "bass", FretboardPlotter.tunings["bass"]["fiveStringDropD"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, scale), "bass", FretboardPlotter.tunings["bass"]["fiveStringDropA"])
	for chord in FretboardPlotter.chordsToChordIndexesDictionary.keys():
		listOfPlottables = []
		plottable = Plottable(note,FretboardPlotter.scalesToScaleIndexesDictionary[chord])
		listOfPlottables.append(plottable)
		graphTitle = "{} {}\n{}".format(note, chord, FretboardPlotter.get_plottable_notes(plottable))
		print(graphTitle)
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "guitar", FretboardPlotter.tunings["guitar"]["standard"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "bass", FretboardPlotter.tunings["bass"]["standard"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "bass", FretboardPlotter.tunings["bass"]["fiveStringStandard"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "guitar", FretboardPlotter.tunings["guitar"]["dropD"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "bass", FretboardPlotter.tunings["bass"]["dropD"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "bass", FretboardPlotter.tunings["bass"]["fiveStringDropD"])
		FretboardPlotter.plot(listOfPlottables, graphTitle, "C:/Users/lukeb/Desktop/Fretboard Plotter Pics/{} {}".format(note, chord), "bass", FretboardPlotter.tunings["bass"]["fiveStringDropA"])

