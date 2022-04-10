"""
This script will do one of two things. Given a combination of possible chords, it will
	1) Generate a random chord name and ask the user to provide the proper chord notation
		ex) "C augmented triad" --> C+ | Caug | CM#5, C+5
	2) Generate a random chord notation and ask the user to provide the proper chord name
		ex) "Cø" --> C half-diminished | C half-diminished 7th

The user will be able to select which mode they want (either only 1, only 2, or both) before the quizzing starts.
Stats will be kept along the way


How to type symbols on mac, windows
	diminished
		option k  = ˚
		alt 248 = ° 
		TODO (need to figure out how to get that on mac...they clearly are different) 
	half-diminished chords
		option o = ø
		alt 0248 = ø
	major
		option j = ∆
		alt 30? = ▲
	augmented
		+, #
	flat
		b
"""

"""
The formula for notating chords is:
	chord = rqe
	r = root of the chord 
		ex) C, D, C#
	q = quality of the chord
		ex) major, minor, half-diminished, altered
	e = extensions
		ex) 7, add9

Chords supported
	major 
		C, D, C# = major triad
		CM || CM7 = major seventh
		C6, C2, C4 = major w/ extra notes
	minor 
		Cm, Dm, C#m || C-, D-, C#- = minor triad
		minor seventh
	diminished
		diminished triad
	augmented
		C+, Caug = augmented triad
	suspended 
	dominant
		dominant seventh
	half-diminished
	altered chord
	slash chord
	extensions
"""
class PythonChordNotation:
	isFirstAttempt = True
	correctGuesses = 0.0
	totalAttempts = 0.0
	percentCorrect = ""
	
	@staticMethod
	def getSettings():


class NotationGenerator:


class NameGenerator: 


while(True):
	mode = input("There are three game modes.\n\t#1 = given a chord name, enter the notation.\n\t#2 = given a notation, enter the chord name.\n\t#3 given either a chord name or notation, enter the opposite.\nEnter 1 for mode #1, 2 for mode #2, or 3 for mode #3")

	print("Current Stats: \n\t[Correct Guesses]= " + str(PythonChordNotation.correctGuesses) + "\n\t[Total Attempts]= " + str(PythonChordNotation.totalAttempts) + "\n\t[Percent Correct]= " + str(PythonChordNotation.percentCorrect) + "\n")

