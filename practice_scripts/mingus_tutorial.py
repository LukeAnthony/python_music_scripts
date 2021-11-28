import mingus.core.notes as notes
import mingus.core.keys as keys
from mingus.containers import Note
import mingus.core.chords as chords
import mingus.core.scales as scales
import mingus.core.intervals as intervals
from mingus.midi import fluidsynth
from mingus.containers import NoteContainer
from mingus.containers import Bar
import random

# should return F major or d minor
print(keys.get_key(-1))

print(keys.get_notes("d"))

print(keys.get_key_signature_accidentals("Eb"))

# mingus chord functions can be found here: https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L35

# (3,7) represents the position of the semitones. in this case, this prints the C major scale, since semitones in major scales occur after 3rd and 7th notes
cMajScale = scales.Diatonic('C', (3,7))
print("c major:")
print(cMajScale)

cHarmonicMajor = scales.HarmonicMajor("C")
print("c harmonic major:")
print(cHarmonicMajor)


randomChord = chords.major_seventh("C")
print(chords.first_inversion(randomChord))
print(chords.second_inversion(randomChord))
print(chords.third_inversion(randomChord))
# also do inversions

# https://github.com/bspaans/python-mingus/blob/master/mingus/core/chords.py#L35

# triads
# 	supports major, minor, diminished, augmented, sus2, sus4
# sevenths
#	

print() 
print()
fluidsynth.init("GeneralUser_GS_v1.471.sf2")
### THIS IS HOW YOU RANDOMLY GENERATE CHORDS
chordFunctionMap = {"triads": ( ["suspended second triad", "suspended fourth triad", "augmented triad", "hendrix chord"],
 [chords.suspended_second_triad, chords.suspended_fourth_triad, chords.augmented_triad, chords.hendrix_chord] )} 
randomNote = notes.int_to_note(random.randint(0, 11), "b" if random.random() > .5 else "#")
print(randomNote)
randomChord = chordFunctionMap["triads"][1][0](randomNote)
print(randomChord)
randoMChordWithTones = []
for s in randomChord:
	chordToneWithOctave = Note(s, 2)
	randoMChordWithTones.append(chordToneWithOctave)

print(randoMChordWithTones)

b = Bar()
b.place_notes(randoMChordWithTones, 2)
fluidsynth.play_Bar(b, 1, 60)
chordName = chords.determine(randomChord)
print(chordName)
chordNameLessRootList = chordName[0].split(' ')[1:]
chordNameLessRoot = ' '.join(chordNameLessRootList)
print(chordNameLessRoot)
print()
print()

#testing intervals
print("testing intervals")
randomNote = notes.int_to_note(random.randint(0, 11), "b" if random.random() > .5 else "#")
note = Note("C", 4)
print(randomNote)
print(note)
minorSecond = intervals.minor_second(note.name)
minorSecondNote = Note(minorSecond, 4)
print(minorSecondNote)
print(intervals.determine(note.name, minorSecond, False))

