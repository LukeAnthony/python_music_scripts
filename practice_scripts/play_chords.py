from mingus.containers import NoteContainer
from mingus.midi import fluidsynth
from mingus.containers import Note
from mingus.containers import Bar
from mingus.containers import NoteContainer

fluidsynth.init("GeneralUser_GS_v1.471.sf2")

b = Bar()
chordList = ['D-2', 'F#-2', 'A-2']
b.place_notes(chordList, 2)


fluidsynth.play_Bar(b, 1, 60)