import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.chords as chords
import mingus.core.scales as scales

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