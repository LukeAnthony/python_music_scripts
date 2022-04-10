import mingus.core.notes as notes
import random, sys, math
import unittest

"""
Generates a random key, chord progression, and time signature
"""

class PracticeRoutineGenerator:

	@staticmethod
	def getRandomNote():
		randomNote = random.randint(0,11)
		flatOrSharp = random.random()
		if flatOrSharp < 0.5:
			return notes.int_to_note(randomNote, "#")
		else:
			return notes.int_to_note(randomNote, "b")

	@staticmethod
	def getChordProgression():


class TestPracticeRoutineGenerator(unittest.TestCase):

	def test_does_getRandomNote_generate_all_notes(self):
		allNotes = ['A', 'A#', 'Ab', 'B', 'Bb', 'C', 'C#', 'D', 'D#', 'Db', 'E', 'Eb', 'F', 'F#', 'G', 'G#', 'Gb']
		returnedValues = set()
		for x in range(5000):
			returnedValues.add(PracticeRoutineGenerator.getRandomNote())
		for note in allNotes:
			self.assertTrue(note in returnedValues)

inp = input("enter something")
print(inp)
