"""
This script will do one of two things. Given a combination of possible chords, it will
	1) Generate a random chord name and ask the user to provide the proper chord notation
		ex) "C augmented triad" --> C+ | Caug | CM#5, C+5
	2) Generate a random chord notation and ask the user to provide the proper chord name
		ex) "Cø" --> C half-diminished | C half-diminished 7th

The user will be able to select which mode they want (either only 1, only 2, or both) before the quizzing starts.
Stats will be kept along the way


How to type symbols on mac
	option k = ˚ (diminished)
	option o = ø (half-diminished chords)
	option j = ∆ (major)
	+ (augmented)
	# (augmented)
	b for flat
"""

# Chords supported
	# major 
		# major triad
		# major seventh
	# minor 
		# minor triad
		# minor seventh
	# diminished
	# augmented
	# suspended 
	# dominant
		# dominant seventh
