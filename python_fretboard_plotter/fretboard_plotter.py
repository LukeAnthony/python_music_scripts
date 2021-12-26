import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches


# Much of this code was taken directly from https://colab.research.google.com/github/diegopenilla/PythonGuitar/blob/master/How_to_learn_guitar_with_Python.ipynb#scrollTo=QqZpI0Pl9rw5
# 	and https://betterprogramming.pub/how-to-learn-guitar-with-python-978a1896a47. 
#	Thank you to Diego Penilla for making this easy for me
class FretboardPlotter:
	# a sufficiently long list to take 12 notes out of any note
	whole_notes = ['C' , 'C#', 'D', 'D#', 'E', 'F', 'F#' , 'G', 'G#', 'A', 'A#', 'B']*3
	strings = {}

	# Enums for fretboard
	MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
	MAJOR_TRIAD = [0, 4, 7]
	MAJOR_SEVENTH = [0, 4, 7, 11]
	MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
	MINOR_TRIAD = [0, 3, 7]
	MINOR_SEVENTH = [0, 3, 7 ]

	def __init__(self):
		self.populate_strings()

	def get_notes(self, key, intervals):
		"""Diego: "Given any key C, C#... B
    	and intervals z.B Tone Tone Semitone" """
		root = self.whole_notes.index(key)
		octave = self.whole_notes[root:root+12]
		return [octave[i] for i in intervals]

	def populate_strings(self):
		start_strings = []
		strings = {i:0 for i in 'EADG'}
		for i in strings.keys():
			start = self.whole_notes.index(i)
			strings[i] = self.whole_notes[start:start+21]
		self.strings = strings

	def find_notes(self, scale):
	    notes_strings = {i:0 for i in "EADG"}
	    # for every string 
	    for key in self.strings.keys():
	        indexes = []
	        for note in scale:
	            # Diego: "append index where note of the scale is found in"
	            ind = self.strings[key].index(note)
	            indexes.append(ind)
	            #because there are 20 frets (plus 1 open string), there are duplicate notes in the string
	            if ind <= 8:
	                indexes.append(ind+12)
	        # list notes in order of appearance on the fretboard
	        indexes.sort()
	        notes_strings[key] = indexes
	    return notes_strings

	# TODO iterate through ax array rather than referencing each time. will be cleaner
	def plot(self, key, intervals, graphTitle, night=True):
		scale = self.get_notes(key, intervals)
		# Diego: "Plot Strings"
		fig, ax = plt.subplots(2, figsize=(21,4))
		background = ['white', 'black']
		# creates 4 lines in each plot for the 4 strings
		for i in range(1,5):
			for graph in ax:
				graph.plot([i for a in range(22)])
			#ax[0].plot([i for a in range(22)])
			#ax[1].plot([i for a in range(22)])
		
		#creates the lines to simulate the fretboard in each graph
		for i in range(1,21):
			# lefty --> i == 9? 8?
			# if i == 9:
			# righty
			if i == 9:
				ax[0].axvline(x=i, color='gray', linewidth=3.5)
				ax[1].axvline(x=i, color='gray', linewidth=3.5)
				continue
			if i == 12:
				ax[0].axvline(x=i, color='gray', linewidth=3.5)
				ax[1].axvline(x=i, color=background[night-1], linewidth=0.5)
				continue
			ax[0].axvline(x=i, color=background[night-1], linewidth=0.5)
			ax[1].axvline(x=i, color=background[night-1], linewidth=0.5)

		# Diego: "ax.grid(linestyle='-', linewidth='0.5', color='black')"
		ax[0].set_axisbelow(True)
		ax[1].set_axisbelow(True)
		
		# Diego: "setting height and width of displayed guitar"
		ax[0].set_xlim([0.5, 21])
		ax[1].set_xlim([0.5, 21])
		ax[0].set_ylim([0.4, 5])
		ax[1].set_ylim([0.4, 5])
		ax[0].set_facecolor(background[night])
		ax[1].set_facecolor(background[night])
		to_plot = self.find_notes(scale)
		
		#find_notes returns a map of strings with the indexes of the notes that are in the given scale
			#ex: to_plot(C major scale) = {'E': [19, 17, 15, 13, 12, 10, 8, 7, 5, 3, 1, 0], 'A': [19, 17, 15, 14, 12, 10, 8, 7, 5, 3, 2, 0]...
			# below for loop iterates through EADG keys of the map
		for y_val, key in zip([1,2,3,4], 'EADG'):
			#  looks up the values corresponding to EADG keys of find_notes map aka the indexes of the notes that were in the given scale
			for i in to_plot[key]:
				font = 12
				color = 'w'
				circleSize = 0.2
				#lefty
				xLefty = 21 - i - 0.3
				#righty 
				xRighty = i + 0.55
				# strings is a map of each string and their notes. 
				# gets the list of notes for a given string and looks up the note at the index
				note = self.strings[key][i]
				print("Note = " + note)
				# make the root slightly larger and yellow
				if note == scale[0]:
					font = 15
					color = 'yellow'
					circleSize = 0.3
				p = mpatches.Circle((xRighty, y_val), circleSize)
				pLefty = mpatches.Circle((xLefty, y_val), circleSize)
				ax[0].add_patch(p)
				ax[1].add_patch(pLefty)
				ax[0].annotate(note, (xRighty, y_val), color=color, weight='bold', fontsize=font, ha='center', va='center')
				ax[1].annotate(note, (xLefty, y_val), color=color, weight='bold', fontsize=font, ha='center', va='center')

		#plt.title(graphTitle)
		fig.suptitle(graphTitle + "\n Righty (top graph). Lefty (bottom graph)")
		plt.subplots_adjust(None, None, None, None, None, 0.5)
		ax[1].yaxis.tick_right()

		ax[0].set_yticks(np.arange(1,5), ['E', 'A', 'D', 'G'])
		ax[1].set_yticks(np.arange(1,5), ['E', 'A', 'D', 'G'])
		#plt.yticks(np.arange(1,5), ['E', 'A', 'D', 'G'])

		# Diego had offset at +0.5. shifting down slightly since i think it's easier to see open strings this way
		# plt.xticks(np.arange(21)+0.45, np.arange(0,20))
		ax[0].set_xticks(np.arange(21)+0.45, np.arange(0,21))
		ax[1].set_xticks(np.arange(21)+0.45, np.arange(-20,1))
		#plt.xticks(np.arange(21)+0.45, np.arange(-20,1))
		plt.show()

fretboardPlotter = FretboardPlotter()

# index where element 'B' is located.
root = fretboardPlotter.whole_notes.index('B')
# starting from this index, slice twelve elements
B = fretboardPlotter.whole_notes[root:root+12]
print('B chromatic scale: ', B)


# intervals of the major scale as indexes:
major_scale = [0, 2, 4, 5, 7, 9, 11]
# selecting the indexes of the octave we want
notes = [B[i] for i in major_scale]
print('B major scale:', notes)



another_scale = [0, 2, 5, 10, 11]
notes = [B[i] for i in another_scale]
print('Some scale ', notes)


print('Notes of C major scale:\n{}'.format(fretboardPlotter.get_notes('C', FretboardPlotter.MINOR_SCALE)))


cMajorNotes = fretboardPlotter.get_notes("C", fretboardPlotter.MAJOR_SCALE)
print()
print(cMajorNotes)

cMajorNotesOnStrings = fretboardPlotter.find_notes(cMajorNotes)
print(cMajorNotesOnStrings)

print(fretboardPlotter.strings)
fretboardPlotter.plot('B', fretboardPlotter.MAJOR_SCALE, "C Major Scale")