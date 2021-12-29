# The below code was heavily influenced by and, in a few cases (especially the matlab plotting), directly copied from https://colab.research.google.com/github/diegopenilla/PythonGuitar/blob/master/How_to_learn_guitar_with_Python.ipynb#scrollTo=QqZpI0Pl9rw5
# 	and https://betterprogramming.pub/how-to-learn-guitar-with-python-978a1896a47. 
#	Thank you to Diego Penilla for making this a lot easier for me

# TODO add octaves to notes (E1, C2, etc...)
# TODO figure out how to make root of each chord larger & gold on plot

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

class FretboardPlotter:
	# multiplying lists by 3 bc of populate strings method. looks 21 notes past the starting point of the strings, 
	# 	so need to make sure there's enough notes to choose from
	whole_notes_flats = ['C' , 'Db', 'D', 'Eb', 'E', 'F', 'Gb' , 'G', 'Ab', 'A', 'Bb', 'B']*3
	whole_notes_sharps = ['C' , 'C#', 'D', 'D#', 'E', 'F', 'F#' , 'G', 'G#', 'A', 'A#', 'B']*3
	strings = {}

	"""
		Need a map of keys that take sharps and keys that take flats
		Then need to look up sharps.values() in plot method to see if it's in there. if so, plot sharps. If not, plot flats
	"""
	accidentalsToKeysMap = {
		"sharps" : ['C', 'Am', 'G', 'Em', 'D', 'Bm', 'A', 'F#m', 'E', 'C#m', 'B', 'G#m', 'F#', 'D#m', 'C#', 'A#m',],
		"flats": ['C', 'Am', 'F', 'Dm', 'Bb', 'Gm', 'Eb', 'Cm', 'Ab', 'Fm', 'Db', 'Bbm', 'Gb', 'Ebm', 'Cb', 'Abm',]
	}

	#Map<String,List[Int]>
	chordsToChordIndexesDictionary = {
		"maj" : [0, 4, 7],
		"maj7": [0, 4, 7, 11]
	}

	#Map<String,List[Int]>
	scalesToScaleIndexesDictionary = {
		"major" : [0, 2, 4, 5, 7, 9, 11],
		"minor" : [0, 2, 3, 5, 7, 8, 10]
	}

	@staticmethod
	def get_plottable_notes(plottable):
		root = plottable.get_root()
		intervals = plottable.get_intervals()
		containsSharps = '#' in root
		rootIndex = FretboardPlotter.whole_notes_sharps.index(root) if containsSharps else FretboardPlotter.whole_notes_flats.index(root)
		noteAlphabetStartingWithThatRoot = FretboardPlotter.whole_notes_sharps[rootIndex:rootIndex+12] if containsSharps else FretboardPlotter.whole_notes_flats[rootIndex:rootIndex+12]
		return [noteAlphabetStartingWithThatRoot[i] for i in intervals]

	def populate_strings():
		strings = {i:0 for i in 'EADG'}
		for i in strings.keys():
			# combines sharps and flats into a list of tuples, with equal accidentals occupying the same index, with sharps in position 0 and flats in pos 1
			# 	[('C', 'C'), ('C#', 'Db'), ('D', 'D'), ('D#', 'Eb'), ('E', 'E'), ('F', 'F'), ('F#', 'Gb'), ('G', 'G'), ('G#', 'Ab').....
			sharpsAndFlats = list(zip(FretboardPlotter.whole_notes_sharps, FretboardPlotter.whole_notes_flats))
			#start = index of the first tuple containing E|A|D|G in sharpsAndFlats
			start = [x[0] for x in sharpsAndFlats].index(i)
			strings[i] = sharpsAndFlats[start:start+21]
		FretboardPlotter.strings = strings

	# look at plottable notes being passed in. if sharp look for sharps, if flat look for flats
	# sharps will always be first element in tuple, flats will always be second element in tuple
	def find_notes(plottable_notes, plottable):
	    notes_strings = {i:0 for i in "EADG"}
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
	        # list notes in order of appearance on the fretboard
	        indexes.sort()
	        notes_strings[string] = indexes
	    return notes_strings

	@staticmethod
	#index 0 = right handed plot, index 1 = left handed plot
	def plot(plottables, graphTitle, night=True):
		FretboardPlotter.populate_strings()
		#creating two plots, top right handed, bottom left handed
		fig, ax = plt.subplots(2, figsize=(21,4))
		background = ['white', 'black']
		# creates 4 lines in each plot for the 4 strings
		for i in range(1,5):
			for index, graph in enumerate(ax):
				graph.plot([i for a in range(22)])
				graph.set_axisbelow(True)
				#setting height and width of displayed guitar
				if index == 0:
					graph.set_xlim([0.45, 21])
				elif index == 1:
					graph.set_xlim([0, 20.1])
				graph.set_ylim([0.4, 5])
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
		# C, G, Bb, C#
		plottableRoots = []
		for plottable in plottables:
			plottableRoots.append(plottable.get_root())
			#ex) notes = ['C', 'E', 'G']
			notes = FretboardPlotter.get_plottable_notes(plottable)
			#ex) plottableNootes = {'E': [0, 3, 8, 12, 15, 20], 'A': [3, 7, 10, 15, 19], 'D': [2, 5, 10, 14, 17], 'G': [0, 5, 9, 12, 17]
			plottableNotes = FretboardPlotter.find_notes(notes, plottable)
			# need to combine the dictionary lists together for multiple plottables
			if len(to_plot) == 0:
				to_plot = plottableNotes
			else:
				for key in to_plot.keys():
					to_plot[key] += plottableNotes[key]

		#find_notes returns a map of strings with the indexes of the notes that are in the given scale
			#ex: to_plot(C major scale) = {'E': [19, 17, 15, 13, 12, 10, 8, 7, 5, 3, 1, 0], 'A': [19, 17, 15, 14, 12, 10, 8, 7, 5, 3, 2, 0]...
			# below for loop iterates through EADG keys of the map
		for y_val, stringName in zip([1,2,3,4], 'EADG'):
			#  looks up the values corresponding to EADG keys of find_notes map aka the indexes of the notes that were in the given scale
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

		fig.suptitle(graphTitle + "\n Righty (top graph). Lefty (bottom graph)")
		# adding more space between the two graphs
		plt.subplots_adjust(None, None, None, None, None, 0.5)
		for index, graph in enumerate(ax):
			if index == 0:
				graph.set_xticks(np.arange(21)+0.45, np.arange(0,21))
			elif index == 1:
				graph.yaxis.tick_right()
				graph.set_xticks(np.arange(21)+0.45, np.arange(20,-1,-1))
			graph.set_yticks(np.arange(1,5), ['E', 'A', 'D', 'G'])
		plt.show()

class Plottable:
	
	def __init__(self, root, intervals):
		self.root = root
		self.intervals = intervals

	#notes should be a list of integers corresponding to the indexes of the notes within a key that should be plotted
	def get_intervals(self) -> list[int]:
		return self.intervals

	def get_root(self) -> str:
		return self.root

"""
	Program goal:
		To plot notes on the fretboard that correspond to certain chords, scales, or progressions within a scale
	Program algorithm:
		Get user input
			"Would you like to plot": A chord(s) or a scale?
				If chord(s):
					"Which chord type would you like to plot? ***display options which should come from some kind of data structure...maybe the keys of a map?***"
					"What should the root of this chord be ***expect a valid note as input***"
						TODO handle inversions --> would merely highlight the lowest note on the diagram
					"Would you like to plot another chord?"
						If yes:
							** redo **
				If individual scale:
					"Which scale would you like to ploat ***same as chord, options should be displayed that come from a list***"
					"What should the tonic of the scale be?" ***expect a valid note as input***"
				*** separating scales and chords to make it more readable ***
		Begin plotting 
			If scale

				plot in same way as normal --> maybe pass object in instead of the array of intervals???
			If chord
				plot same way as normal --> pass plottable object in instead of array of intervals


"""

#plot needs to have the following arguments
	#root note (char), which will indicate the root of the key
	#majorOrMinor (enum), which will indicate whether key is major or minor
		#these first two arguments serve the purpose of figuring out whether to plot sharps or flats. they do not indicate what notes within the key to plot
		# will append 'm' to root note if minor. will then look up appended key name in accidentalsToKeysMap. if in sharps, use whole_notes_sharps to get notes. if not, use whole_notes_flates to get notes
	#a class of type Plottable, which indicates what notes to plot
		#will need to use 
# fretboardPlotter = FretboardPlotter()
# fretboardPlotter.plot('D', [0, 2, 4, 5, 7, 9, 11], "D Major Scale")

listOfPlottables = []
graphTitle = ""

testList = [ Plottable("C", [0,2,4]), Plottable("Bb", [0, 2, 5]) ]
note = "D"
# print( note == x.gettestList[0].get_root())

chordOrScale = input("Would you like to plot a chord(s) or a scale? Type 'C' for chord, 'S' for scale ")
if chordOrScale.lower() != 'c' and chordOrScale.lower() != 's':
	raise ValueError("Must enter 'C' or 'S'")
#if chord
if chordOrScale.lower() == 'c':
	while(True):
		rootChoice = input("What should the root of the chord be? ")
		if rootChoice not in FretboardPlotter.whole_notes_flats and rootChoice not in FretboardPlotter.whole_notes_sharps:
			raise ValueError("Must enter valid note")
		chordChoice = input("What chord would you like to plot? Choices are: " + str(FretboardPlotter.chordsToChordIndexesDictionary.keys()) + " ")
		if chordChoice not in FretboardPlotter.chordsToChordIndexesDictionary.keys():
			raise ValueError("Must enter a valid chord name")
		# at this point get a plottable object 
		# add to listOfPlottables
		listOfPlottables.append(Plottable(rootChoice, FretboardPlotter.chordsToChordIndexesDictionary[chordChoice] ))
		enterAnotherChord = input("Would you like to plot another chord? Type 'Y' for yes, 'N' for no ")
		if enterAnotherChord.lower() == 'n':
			break
	graphTitle = input("What should the title of the graph be?")
	print(len(listOfPlottables))
#if scale
if chordOrScale.lower() == 's':
	rootChoice = input("What should the root of the scale be? ")
	if rootChoice not in FretboardPlotter.whole_notes_flats and rootChoice not in FretboardPlotter.whole_notes_sharps:
		raise ValueError("Must enter valid note")
	scaleChoice = input("What scale would you likee to plot? Choices are: " + str(FretboardPlotter.scalesToScaleIndexesDictionary.keys()) + " ")
	if scaleChoice not in FretboardPlotter.scalesToScaleIndexesDictionary.keys():
		raise ValueError("Must enter a valid scale name")
	graphTitle = input("What should the title of the graph be? ")
	listOfPlottables.append(Plottable(rootChoice, FretboardPlotter.scalesToScaleIndexesDictionary[scaleChoice] ))

FretboardPlotter.plot(listOfPlottables, graphTitle)
