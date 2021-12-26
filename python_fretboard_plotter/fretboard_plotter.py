import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Much of this code was taken directly from https://colab.research.google.com/github/diegopenilla/PythonGuitar/blob/master/How_to_learn_guitar_with_Python.ipynb#scrollTo=QqZpI0Pl9rw5
# 	and https://betterprogramming.pub/how-to-learn-guitar-with-python-978a1896a47. 
#	Thank you to Diego Penilla for making this easy for me
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

	
	MAJOR = "M"
	MINOR = "m"

	# Enums for fretboard
	MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
	MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

	# TODO need to support chords
	MAJOR_TRIAD = [0, 4, 7]
	MAJOR_SEVENTH = [0, 4, 7, 11]
	
	# have to support minor scales
	MINOR_TRIAD = [0, 3, 7]
	MINOR_SEVENTH = [0, 3, 7 ]

	def __init__(self):
		self.populate_strings()

	def get_key_notes(self, key, intervals):
		containsSharps = '#' in key
		root = self.whole_notes_sharps.index(key) if containsSharps else self.whole_notes_flats.index(key)
		octave = self.whole_notes_sharps[root:root+12] if containsSharps else self.whole_notes_flats[root:root+12]
		return [octave[i] for i in intervals]

	def populate_strings(self):
		strings = {i:0 for i in 'EADG'}
		for i in strings.keys():
			# combines sharps and flats into a list of tuples, with equal accidentals occupying the same index, with sharps in position 0 and flats in pos 1
			# 	[('C', 'C'), ('C#', 'Db'), ('D', 'D'), ('D#', 'Eb'), ('E', 'E'), ('F', 'F'), ('F#', 'Gb'), ('G', 'G'), ('G#', 'Ab').....
			sharpsAndFlats = list(zip(self.whole_notes_sharps, self.whole_notes_flats))
			#start = index of the first tuple containing E|A|D|G in sharpsAndFlats
			start = [x[0] for x in sharpsAndFlats].index(i) 
			strings[i] = sharpsAndFlats[start:start+21]
		self.strings = strings
		print()

	# look at scale value being passed in. if sharp look for sharps, if flat look for flats
	# sharps will always be first element in tuple, flats will always be second element in tuple
	def find_notes(self, scale):
	    notes_strings = {i:0 for i in "EADG"}
	    # for every string 
	    for key in self.strings.keys():
	        indexes = []
	        tuplesOfStringNotes = self.strings[key]
	        print("Tuples of string notes for string " + str(key) + " " + str(tuplesOfStringNotes))
	        print("Scale = " + str(scale))
	        for note in scale:
	            # Diego: "append index where note of the scale is found in"
	            ind = -1
	            #tuplesOfStringNotes = self.strings[key]
	            for index, tup in enumerate(tuplesOfStringNotes):
	            	#print("Tuple list " + str(tup))
	            	#print("Note " + str(note))
	            	if note in tup:
	            		#print("Note matched " + str(note))
	            		ind = index
	            		print("Index of matched note " + str(ind))
	            		#ind = self.strings[key].index(note)
	            		indexes.append(ind)
	            #because there are 20 frets (plus 1 open string), there are duplicate notes in the string
	            #if ind <= 8:
	                #indexes.append(ind+12)
	        # list notes in order of appearance on the fretboard
	        indexes.sort()
	        print("Final list of indexes for string " + str(key) + " = " + str(indexes))
	        notes_strings[key] = indexes
	    print(notes_strings)
	    return notes_strings

	#index 0 = right handed plot, index 1 = left handed plot
	def plot(self, key, intervals, graphTitle, night=True):
		scale = self.get_key_notes(key, intervals)
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
		to_plot = self.find_notes(scale)
		
		#find_notes returns a map of strings with the indexes of the notes that are in the given scale
			#ex: to_plot(C major scale) = {'E': [19, 17, 15, 13, 12, 10, 8, 7, 5, 3, 1, 0], 'A': [19, 17, 15, 14, 12, 10, 8, 7, 5, 3, 2, 0]...
			# below for loop iterates through EADG keys of the map
		for y_val, stringName in zip([1,2,3,4], 'EADG'):
			#  looks up the values corresponding to EADG keys of find_notes map aka the indexes of the notes that were in the given scale
			for i in to_plot[stringName]:
				font = 12
				color = 'w'
				circleSize = 0.2
				# i = 0 means an open string note (E,A,D,G)
				xLefty = (21 - i - 0.7) if i == 0 else (21 - i - 0.45)
				xRighty = (i + 0.55) if i == 0 else (i + 0.55)
				# strings is a map of each string and their notes. 
				# gets the list of notes for a given string and looks up the note at the index
				noteTuple = self.strings[stringName][i]
				print("Note tuple = " + str(noteTuple))
				note = noteTuple[0] if key in self.accidentalsToKeysMap["sharps"] else noteTuple[1]
				print("Note  = " + str(note))
				# make the root slightly larger and yellow
				if note == scale[0]:
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
	#should return a list of integers corresponding to the indexes of the notes within a key that should be plotted
	def get_notes() -> list[int]:
		pass


fretboardPlotter = FretboardPlotter()

#plot needs to have the following arguments
	#root note (char), which will indicate the root of the key
	#majorOrMinor (enum), which will indicate whether key is major or minor
		#these first two arguments serve the purpose of figuring out whether to plot sharps or flats. they do not indicate what notes within the key to plot
		# will append 'm' to root note if minor. will then look up appended key name in accidentalsToKeysMap. if in sharps, use whole_notes_sharps to get notes. if not, use whole_notes_flates to get notes
	#a class of type Plottable, which indicates what notes to plot
		#will need to use 
fretboardPlotter.plot('D', fretboardPlotter.MAJOR_SCALE, "D Major Scale")