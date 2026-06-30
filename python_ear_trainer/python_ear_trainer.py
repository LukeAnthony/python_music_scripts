#!/usr/bin/env python3
"""
Python Ear Trainer - Tkinter GUI

A desktop front end for the command-line ear trainer. All of the music-theory
generation and the fluidsynth audio playback are reused unchanged from the
original program; only the interaction layer has been swapped from
input()/print() prompts to GUI widgets.

Run:
    python3 ear_trainer_gui.py /path/to/soundfont.sf2
If no soundfont path is supplied on the command line, a file picker opens.
"""

import os
import sys
import random
import threading

import mingus.core.notes as notes
import mingus.core.chords as chords
import mingus.core.intervals as intervals
from mingus.containers import Note
from mingus.containers import Bar
from mingus.midi import fluidsynth

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# ---------------------------------------------------------------------------
# Music-theory + generation logic (reused from the original program).
# The static generation methods read their configuration from class-level
# state, so the GUI just sets that state and then calls these methods.
# ---------------------------------------------------------------------------
class PythonEarTrainer:
    octave = 0
    invertChordOrInterval = False
    guessRootOfChord = False
    guessChordType = False
    correctGuesses = 0.0
    totalAttempts = 0.0
    percentCorrect = ""

    defaultOctaveList = [1, 2, 3, 4, 5, 6]
    octaveChoices = []
    # notes are converted to int values so only listing flats here is fine
    defaultNoteList = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    noteChoices = []
    # use same list for interval type choices and chord type choices
    chordOrIntervalTypeChoices = []

    # a dictionary of chord names --> their mingus functions
    chordsDictionary = {
        "major triad": chords.major_triad,
        "major sixth": chords.major_sixth,
        "major seventh": chords.major_seventh,
        "major ninth": chords.major_ninth,
        "major thirteenth": chords.major_thirteenth,
        "minor triad": chords.minor_triad,
        "minor sixth": chords.minor_sixth,
        "minor seventh": chords.minor_seventh,
        "minor ninth": chords.minor_ninth,
        "minor/major seventh": chords.minor_major_seventh,
        "minor thirteenth": chords.minor_thirteenth,
        "dominant flat five": chords.dominant_flat_five,
        "dominant sixth": chords.dominant_sixth,
        "dominant seventh": chords.dominant_seventh,
        "dominant ninth": chords.dominant_ninth,
        "dominant flat ninth": chords.dominant_flat_ninth,
        "dominant sharp ninth": chords.dominant_sharp_ninth,
        "dominant thirteenth": chords.dominant_thirteenth,
        "diminished triad": chords.diminished_triad,
        "diminished seventh": chords.diminished_seventh,
        "half-diminished seventh": chords.half_diminished_seventh,
        "augmented triad": chords.augmented_triad,
        "augmented major seventh": chords.augmented_major_seventh,
        "augmented minor seventh": chords.augmented_minor_seventh,
        "suspended second triad": chords.suspended_second_triad,
        "suspended fourth triad": chords.suspended_fourth_triad,
        "suspended fourth ninth": chords.suspended_fourth_ninth,
        "suspended seventh": chords.suspended_seventh,
        "six ninth": chords.sixth_ninth,
        "eleventh": chords.eleventh,
        "minor eleventh": chords.minor_eleventh,
        "lydian dominant seventh": chords.lydian_dominant_seventh,
        "hendrix chord": chords.hendrix_chord,
    }

    intervalTypesDictionary = {
        "P1": intervals.major_unison,
        "m2": intervals.minor_second,
        "M2": intervals.major_second,
        "m3": intervals.minor_third,
        "M3": intervals.major_third,
        "P4": intervals.perfect_fourth,
        "A4": intervals.minor_fifth,
        "dim5": intervals.minor_fifth,  # mingus uses the minor fifth function for both names
        "P5": intervals.perfect_fifth,
        "m6": intervals.minor_sixth,
        "M6": intervals.major_sixth,
        "m7": intervals.minor_seventh,
        "M7": intervals.major_seventh,
    }

    # maps interval names to their abbreviations
    intervalNamesToAbbreviations = {
        "major unison": ["P1"],
        "minor second": ["m2"],
        "major second": ["M2"],
        "minor third": ["m3"],
        "major third": ["M3"],
        "perfect fourth": ["P4"],
        # the tritone: mingus spells it "minor fifth" (Gb) or "augmented fourth" (F#)
        # depending on the root/inversion, so both names must map to the tritone abbreviations
        "minor fifth": ["A4", "dim5"],
        "augmented fourth": ["A4", "dim5"],
        "perfect fifth": ["P5"],
        "minor sixth": ["m6"],
        "major sixth": ["M6"],
        "minor seventh": ["m7"],
        "major seventh": ["M7"],
        "perfect octave": ["P8"],
    }

    @staticmethod
    def updateStats(points):
        PythonEarTrainer.correctGuesses += points
        PythonEarTrainer.totalAttempts += 1
        PythonEarTrainer.percentCorrect = (
            str(round(PythonEarTrainer.correctGuesses / PythonEarTrainer.totalAttempts, 2) * 100) + "%"
        )

    @staticmethod
    def setRandomOctave():
        PythonEarTrainer.octave = PythonEarTrainer.octaveChoices[
            random.randrange(len(PythonEarTrainer.octaveChoices))
        ]

    @staticmethod
    def getRandomRoot():
        return PythonEarTrainer.noteChoices[random.randint(0, len(PythonEarTrainer.noteChoices) - 1)]

    @staticmethod
    def getRandomNote():
        randomRoot = PythonEarTrainer.getRandomRoot()
        return Note(randomRoot, PythonEarTrainer.octave, None, 127, 1)

    @staticmethod
    def getRandomChord():
        randomRoot = PythonEarTrainer.getRandomRoot()
        # track the selected chord type by name (not just its function) so we can report
        # back the exact label the user chose from, instead of relying on chords.determine.
        # list(...) handles both the dict_keys view ("all") and the list (comma choices).
        chordTypeChoices = list(PythonEarTrainer.chordOrIntervalTypeChoices)
        randomChordType = chordTypeChoices[random.randrange(len(chordTypeChoices))]
        # giving each chord an equal chance of being selected
        randomChord = PythonEarTrainer.chordsDictionary[randomChordType](randomRoot)

        if PythonEarTrainer.invertChordOrInterval:
            secondDiceRoll = random.random()
            if secondDiceRoll < 0.00:
                pass
            elif secondDiceRoll < 0.34:
                randomChord = chords.first_inversion(randomChord)
            elif secondDiceRoll < 0.67:
                randomChord = chords.second_inversion(randomChord)
            else:
                randomChord = chords.third_inversion(randomChord)

        randomChordAsNoteObjects = []
        currentOctaveAboveRoot = 0
        previousNoteValue = 0
        for tone in randomChord:
            randomChordAsNoteObjectsIndex = len(randomChordAsNoteObjects) - 1
            toneValue = notes.note_to_int(tone)
            if randomChordAsNoteObjectsIndex == -1:
                toneAsNote = Note(tone, PythonEarTrainer.octave, None, 110, 1)
                randomChordAsNoteObjects.append(toneAsNote)
            else:
                toneDistanceFromPreviousNote = toneValue - previousNoteValue
                if toneDistanceFromPreviousNote < 0:
                    while toneValue - previousNoteValue < 0:
                        toneValue = toneValue + 12
                        currentOctaveAboveRoot = currentOctaveAboveRoot + 1
                toneAsNote = Note(tone, PythonEarTrainer.octave + currentOctaveAboveRoot, None, 110, 1)
                randomChordAsNoteObjects.append(toneAsNote)
            previousNoteValue = toneValue
            currentOctaveAboveRoot = 0

        # use the chord type we actually generated as the name, so it matches the
        # choices presented to the user. chords.determine renames inverted voicings
        # and can phrase types differently than our chordsDictionary keys.
        return RandomChord(randomRoot, randomChord, randomChordAsNoteObjects, randomChordType)

    @staticmethod
    def getRandomChordWithMissingTone(randomChord):
        # separate lists so python doesn't mutate the original chord by reference
        randomChordChordTones = [x for x in randomChord.chordTones]
        randomChordChordTonesAsNoteObjects = [x for x in randomChord.chordTonesAsNoteObjects]
        # first argument is 1 so we never remove the root
        indexOfNoteToRemove = random.randint(1, len(randomChordChordTonesAsNoteObjects) - 1)
        randomChordChordTones.pop(indexOfNoteToRemove)
        randomChordChordTonesAsNoteObjects.pop(indexOfNoteToRemove)
        return RandomChord(
            randomChord.randomRoot,
            randomChordChordTones,
            randomChordChordTonesAsNoteObjects,
            randomChord.chordName,
        )

    @staticmethod
    def figureOutMissingTone(tonesOfRandomChord, tonesOfRandomChordWithAMissingTone):
        return set(tonesOfRandomChord).symmetric_difference(
            set(tonesOfRandomChordWithAMissingTone)
        ).pop()

    @staticmethod
    def calculateIntervalType(firstNoteName, secondNoteName):
        intervalType = intervals.determine(firstNoteName, secondNoteName)
        return PythonEarTrainer.intervalNamesToAbbreviations[intervalType]

    @staticmethod
    def getRandomInterval():
        randomRootNote = Note(PythonEarTrainer.getRandomRoot(), PythonEarTrainer.octave, None, 105, 1)
        randomRootName = randomRootNote.name
        listOfIntervalFunctions = []
        for intervalType in PythonEarTrainer.chordOrIntervalTypeChoices:
            listOfIntervalFunctions.append(PythonEarTrainer.intervalTypesDictionary[intervalType])
        randomIntervalFunction = listOfIntervalFunctions[random.randrange(len(listOfIntervalFunctions))]
        randomIntervalName = randomIntervalFunction(randomRootName)
        secondNoteOctave = (
            PythonEarTrainer.octave
            if (notes.note_to_int(randomIntervalName) - notes.note_to_int(randomRootName) > 0)
            else PythonEarTrainer.octave + 1
        )
        if PythonEarTrainer.invertChordOrInterval:
            diceRoll = random.random()
            if diceRoll < 0.5:
                return RandomInterval(
                    Note(randomIntervalName, secondNoteOctave, None, 105, 1),
                    randomRootNote,
                    PythonEarTrainer.calculateIntervalType(randomIntervalName, randomRootName),
                )
            else:
                return RandomInterval(
                    randomRootNote,
                    Note(randomIntervalName, secondNoteOctave, None, 105, 1),
                    PythonEarTrainer.calculateIntervalType(randomRootName, randomIntervalName),
                )
        else:
            return RandomInterval(
                randomRootNote,
                Note(randomIntervalName, secondNoteOctave, None, 105, 1),
                PythonEarTrainer.calculateIntervalType(randomRootName, randomIntervalName),
            )


# ---------------------------------------------------------------------------
# Data holder classes (reused from the original program)
# ---------------------------------------------------------------------------
class RandomChord:
    def __init__(self, randomRoot, chordTones, chordTonesAsNoteObjects, chordName):
        self.randomRoot = randomRoot
        self.chordTones = chordTones
        self.chordTonesAsNoteObjects = chordTonesAsNoteObjects
        self.chordName = chordName

    def __str__(self):
        return (
            f"{self.randomRoot} {self.chordName}: Tones={self.chordTones}, "
            f"note objects = {self.chordTonesAsNoteObjects}"
        )


class RandomInterval:
    def __init__(self, firstNote, secondNote, intervalType):
        self.firstNote = firstNote
        self.secondNote = secondNote
        self.intervalType = intervalType

    def get_first_note_name(self):
        return self.firstNote.name

    def get_first_note_name_and_octave(self):
        return self.firstNote.name + "-" + str(self.firstNote.octave)

    def get_second_note_name(self):
        return self.secondNote.name

    def get_second_note_name_and_octave(self):
        return self.secondNote.name + "-" + str(self.secondNote.octave)


# ---------------------------------------------------------------------------
# GUI constants
# ---------------------------------------------------------------------------
# canonical pitch-class spelling fed to mingus, plus a friendly enharmonic label
CHROMATIC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_LABELS = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

GAME_MODES = {
    "note": "Guess Random Note",
    "interval": "Guess Random Interval",
    "chord": "Guess Random Chord",
    "missing": "Guess Missing Chord Tone",
}


# ---------------------------------------------------------------------------
# Reusable note-picker widget: a grid of 12 toggle buttons, single selection.
# ---------------------------------------------------------------------------
class NotePicker(ttk.Frame):
    def __init__(self, master, label="", allowed=None):
        """allowed: an iterable of note names to restrict the choices to. When
        None, all 12 chromatic notes are shown. Names are matched by pitch class,
        so sharp/flat spellings are interchangeable."""
        super().__init__(master)
        self.selected = tk.IntVar(value=-1)
        if label:
            ttk.Label(self, text=label).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 2))

        if allowed is None:
            indices = list(range(len(NOTE_LABELS)))
        else:
            allowed_ints = {notes.note_to_int(n) for n in allowed}
            indices = [i for i in range(len(NOTE_LABELS)) if notes.note_to_int(CHROMATIC[i]) in allowed_ints]

        for slot, i in enumerate(indices):
            r = 1 + slot // 6
            c = slot % 6
            ttk.Radiobutton(
                self, text=NOTE_LABELS[i], value=i, variable=self.selected, style="Toolbutton", width=7
            ).grid(row=r, column=c, padx=1, pady=1)

        # if there's only one option there's nothing to guess, so pre-select it
        self._default = indices[0] if len(indices) == 1 else -1
        self.selected.set(self._default)

    def get(self):
        idx = self.selected.get()
        return CHROMATIC[idx] if idx >= 0 else None

    def reset(self):
        self.selected.set(self._default)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
class EarTrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Ear Trainer")
        self.minsize(640, 560)

        try:
            ttk.Style().theme_use("clam")
        except tk.TclError:
            pass

        self.is_playing = False

        # persistent settings widgets / state
        self.mode_var = tk.StringVar(value="note")
        self.note_vars = [tk.IntVar(value=0) for _ in CHROMATIC]
        self.octave_vars = [tk.IntVar(value=0) for _ in range(6)]
        self.invert_var = tk.IntVar(value=0)
        self.guess_root_var = tk.IntVar(value=1)
        self.guess_type_var = tk.IntVar(value=1)
        self.interval_listbox = None
        self.chord_listbox = None

        # current-question state
        self.note = None
        self.interval = None
        self.chord = None
        self.chord_missing = None
        self.missing_tone = None

        # guess widgets for the active round
        self.root_picker = None
        self.first_picker = None
        self.second_picker = None
        self.missing_picker = None
        self.interval_combo = None
        self.type_combo = None

        self.container = ttk.Frame(self, padding=12)
        self.container.pack(fill="both", expand=True)

        self._build_settings_screen()

    # ----- screen management -------------------------------------------------
    def _clear_container(self):
        for child in self.container.winfo_children():
            child.destroy()

    # ----- settings screen ---------------------------------------------------
    def _build_settings_screen(self):
        self._clear_container()
        ttk.Label(self.container, text="Ear Trainer Settings", font=("TkDefaultFont", 16, "bold")).pack(
            anchor="w"
        )

        # game mode
        mode_frame = ttk.LabelFrame(self.container, text="Game", padding=8)
        mode_frame.pack(fill="x", pady=(8, 6))
        for key, label in GAME_MODES.items():
            ttk.Radiobutton(
                mode_frame, text=label, value=key, variable=self.mode_var,
                command=self._render_mode_options
            ).pack(anchor="w")

        # notes to draw from (common to every game)
        notes_frame = ttk.LabelFrame(self.container, text="Notes to choose from", padding=8)
        notes_frame.pack(fill="x", pady=6)
        for i, lab in enumerate(NOTE_LABELS):
            r = i // 6
            c = i % 6
            ttk.Checkbutton(notes_frame, text=lab, variable=self.note_vars[i]).grid(
                row=r, column=c, sticky="w", padx=4, pady=2
            )
        btns = ttk.Frame(notes_frame)
        btns.grid(row=2, column=0, columnspan=6, sticky="w", pady=(4, 0))
        ttk.Button(btns, text="All", width=6,
                   command=lambda: [v.set(1) for v in self.note_vars]).pack(side="left", padx=2)
        ttk.Button(btns, text="None", width=6,
                   command=lambda: [v.set(0) for v in self.note_vars]).pack(side="left", padx=2)

        # octaves (common to every game)
        oct_frame = ttk.LabelFrame(self.container, text="Octaves (1-6)", padding=8)
        oct_frame.pack(fill="x", pady=6)
        for i in range(6):
            ttk.Checkbutton(oct_frame, text=str(i + 1), variable=self.octave_vars[i]).grid(
                row=0, column=i, padx=6
            )

        # mode-specific options get rebuilt whenever the game changes
        self.mode_frame = ttk.Frame(self.container)
        self.mode_frame.pack(fill="both", expand=True, pady=6)
        self._render_mode_options()

        ttk.Button(self.container, text="Start", command=self._start_game).pack(pady=(6, 0))

    def _render_mode_options(self):
        for child in self.mode_frame.winfo_children():
            child.destroy()
        self.interval_listbox = None
        self.chord_listbox = None

        mode = self.mode_var.get()

        if mode == "interval":
            self._build_type_listbox(
                "Interval types to choose from", list(PythonEarTrainer.intervalTypesDictionary.keys())
            )
        if mode in ("chord", "missing"):
            self._build_type_listbox(
                "Chord types to choose from", list(PythonEarTrainer.chordsDictionary.keys())
            )
            guess_frame = ttk.LabelFrame(self.mode_frame, text="What to guess", padding=8)
            guess_frame.pack(fill="x", pady=4)
            ttk.Checkbutton(guess_frame, text="Guess the root", variable=self.guess_root_var).pack(anchor="w")
            ttk.Checkbutton(guess_frame, text="Guess the chord type", variable=self.guess_type_var).pack(
                anchor="w"
            )
            if mode == "missing":
                ttk.Label(guess_frame, text="(the missing tone is always guessed)").pack(anchor="w")

        if mode in ("interval", "chord", "missing"):
            ttk.Checkbutton(
                self.mode_frame, text="Include inversions", variable=self.invert_var
            ).pack(anchor="w", pady=4)

    def _build_type_listbox(self, title, values):
        frame = ttk.LabelFrame(self.mode_frame, text=title, padding=8)
        frame.pack(fill="both", expand=True, pady=4)
        inner = ttk.Frame(frame)
        inner.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(inner, orient="vertical")
        lb = tk.Listbox(inner, selectmode="extended", height=8, exportselection=False,
                        yscrollcommand=scroll.set)
        scroll.config(command=lb.yview)
        for v in values:
            lb.insert("end", v)
        lb.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        ctl = ttk.Frame(frame)
        ctl.pack(fill="x", pady=(4, 0))
        ttk.Button(ctl, text="Select all", command=lambda: lb.select_set(0, "end")).pack(side="left", padx=2)
        ttk.Button(ctl, text="Clear", command=lambda: lb.selection_clear(0, "end")).pack(side="left", padx=2)

        if title.startswith("Interval"):
            self.interval_listbox = lb
        else:
            self.chord_listbox = lb

    # ----- start: validate, push config into PythonEarTrainer ----------------
    def _start_game(self):
        chosen_notes = [CHROMATIC[i] for i, v in enumerate(self.note_vars) if v.get()]
        chosen_octaves = [i + 1 for i, v in enumerate(self.octave_vars) if v.get()]
        if not chosen_notes:
            messagebox.showerror("Missing selection", "Pick at least one note.")
            return
        if not chosen_octaves:
            messagebox.showerror("Missing selection", "Pick at least one octave.")
            return

        mode = self.mode_var.get()
        type_choices = []
        if mode == "interval":
            type_choices = [self.interval_listbox.get(i) for i in self.interval_listbox.curselection()]
            if not type_choices:
                messagebox.showerror("Missing selection", "Pick at least one interval type.")
                return
        elif mode in ("chord", "missing"):
            type_choices = [self.chord_listbox.get(i) for i in self.chord_listbox.curselection()]
            if not type_choices:
                messagebox.showerror("Missing selection", "Pick at least one chord type.")
                return
            if mode == "chord" and not (self.guess_root_var.get() or self.guess_type_var.get()):
                messagebox.showerror(
                    "Missing selection", "For the chord game, choose to guess the root, the type, or both."
                )
                return

        PythonEarTrainer.noteChoices = chosen_notes
        PythonEarTrainer.octaveChoices = chosen_octaves
        PythonEarTrainer.chordOrIntervalTypeChoices = type_choices
        PythonEarTrainer.invertChordOrInterval = bool(self.invert_var.get())
        PythonEarTrainer.guessRootOfChord = bool(self.guess_root_var.get())
        PythonEarTrainer.guessChordType = bool(self.guess_type_var.get())

        self._build_game_screen(mode)

    # ----- game screen -------------------------------------------------------
    def _build_game_screen(self, mode):
        self._clear_container()
        self.current_mode = mode

        ttk.Label(self.container, text=GAME_MODES[mode], font=("TkDefaultFont", 16, "bold")).pack(anchor="w")

        controls = ttk.Frame(self.container)
        controls.pack(fill="x", pady=8)
        self.play_btn = ttk.Button(controls, text="\u25b6 Play", command=self._play_current)
        self.play_btn.pack(side="left", padx=2)
        self.replay_btn = ttk.Button(controls, text="Replay", command=self._play_current)
        self.replay_btn.pack(side="left", padx=2)
        ttk.Button(controls, text="\u2190 Settings", command=self._build_settings_screen).pack(
            side="right", padx=2
        )

        self.guess_frame = ttk.LabelFrame(self.container, text="Your guess", padding=10)
        self.guess_frame.pack(fill="x", pady=6)

        action = ttk.Frame(self.container)
        action.pack(fill="x", pady=6)
        self.submit_btn = ttk.Button(action, text="Submit", command=self._submit, state="disabled")
        self.submit_btn.pack(side="left", padx=2)
        self.next_btn = ttk.Button(action, text="Next \u2192", command=self._new_question, state="disabled")
        self.next_btn.pack(side="left", padx=2)

        self.feedback = ttk.Label(self.container, text="", justify="left", wraplength=580)
        self.feedback.pack(anchor="w", pady=6)

        self.stats_label = ttk.Label(self.container, text="", justify="left")
        self.stats_label.pack(anchor="w", side="bottom")

        self._new_question()

    def _build_guess_widgets(self):
        for child in self.guess_frame.winfo_children():
            child.destroy()
        self.root_picker = self.first_picker = self.second_picker = None
        self.missing_picker = self.interval_combo = self.type_combo = None

        mode = self.current_mode
        if mode == "note":
            self.first_picker = NotePicker(
                self.guess_frame, "Which note did you hear?",
                allowed=PythonEarTrainer.noteChoices,
            )
            self.first_picker.pack(anchor="w")

        elif mode == "interval":
            self.first_picker = NotePicker(self.guess_frame, "First note")
            self.first_picker.pack(anchor="w", pady=(0, 6))
            self.second_picker = NotePicker(self.guess_frame, "Second note")
            self.second_picker.pack(anchor="w", pady=(0, 6))
            row = ttk.Frame(self.guess_frame)
            row.pack(anchor="w")
            ttk.Label(row, text="Interval ").pack(side="left")
            self.interval_combo = ttk.Combobox(
                row, state="readonly", width=8,
                values=list(PythonEarTrainer.intervalTypesDictionary.keys())
            )
            self.interval_combo.pack(side="left")

        elif mode in ("chord", "missing"):
            if PythonEarTrainer.guessRootOfChord:
                self.root_picker = NotePicker(
                    self.guess_frame, "Root note",
                    allowed=PythonEarTrainer.noteChoices,
                )
                self.root_picker.pack(anchor="w", pady=(0, 6))
            if PythonEarTrainer.guessChordType:
                row = ttk.Frame(self.guess_frame)
                row.pack(anchor="w", pady=(0, 6))
                ttk.Label(row, text="Chord type ").pack(side="left")
                self.type_combo = ttk.Combobox(
                    row, state="readonly", width=24,
                    values=list(PythonEarTrainer.chordOrIntervalTypeChoices)
                )
                self.type_combo.pack(side="left")
            if mode == "missing":
                self.missing_picker = NotePicker(self.guess_frame, "Which note went missing?")
                self.missing_picker.pack(anchor="w")

    def _new_question(self):
        PythonEarTrainer.setRandomOctave()
        mode = self.current_mode
        if mode == "note":
            self.note = PythonEarTrainer.getRandomNote()
        elif mode == "interval":
            self.interval = PythonEarTrainer.getRandomInterval()
        elif mode == "chord":
            self.chord = PythonEarTrainer.getRandomChord()
        elif mode == "missing":
            self.chord = PythonEarTrainer.getRandomChord()
            self.chord_missing = PythonEarTrainer.getRandomChordWithMissingTone(self.chord)
            self.missing_tone = PythonEarTrainer.figureOutMissingTone(
                self.chord.chordTones, self.chord_missing.chordTones
            )

        self._build_guess_widgets()
        self.feedback.config(text="Press Play to hear it.")
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        self.play_btn.config(state="normal")
        self.replay_btn.config(state="normal")
        self._update_stats_label()

    # ----- audio (threaded so the UI stays responsive) -----------------------
    def _build_bar(self):
        mode = self.current_mode
        b = Bar()
        if mode == "note":
            b.place_notes(self.note.name, 2)
            b.place_notes(self.note.name, 2)
        elif mode == "interval":
            b.place_notes(self.interval.get_first_note_name_and_octave(), 2)
            b.place_notes(self.interval.get_second_note_name_and_octave(), 2)
        elif mode == "chord":
            b.place_notes(self.chord.chordTonesAsNoteObjects, 2)
            b.place_notes(self.chord.chordTonesAsNoteObjects, 2)
        elif mode == "missing":
            b.place_notes(self.chord.chordTonesAsNoteObjects, 2)
            b.place_notes(self.chord_missing.chordTonesAsNoteObjects, 2)
        return b

    def _play_current(self):
        if self.is_playing:
            return
        bar = self._build_bar()
        self.is_playing = True
        self.play_btn.config(state="disabled")
        self.replay_btn.config(state="disabled")
        threading.Thread(target=self._play_worker, args=(bar,), daemon=True).start()

    def _play_worker(self, bar):
        try:
            fluidsynth.play_Bar(bar, 1, 60)
            fluidsynth.play_Bar(bar, 1, 60)
        finally:
            self.after(0, self._on_play_done)

    def _on_play_done(self):
        self.is_playing = False
        self.play_btn.config(state="normal")
        self.replay_btn.config(state="normal")
        self.submit_btn.config(state="normal")
        if self.feedback.cget("text") == "Press Play to hear it.":
            self.feedback.config(text="Make your guess, then Submit.")

    # ----- evaluation --------------------------------------------------------
    def _submit(self):
        mode = self.current_mode
        lines = []

        if mode == "note":
            guess = self.first_picker.get()
            if guess is None:
                messagebox.showinfo("Pick a note", "Select the note you heard.")
                return
            if notes.note_to_int(guess) == notes.note_to_int(self.note.name):
                PythonEarTrainer.updateStats(1.0)
                lines.append("Correct!")
            else:
                PythonEarTrainer.updateStats(0.0)
                lines.append("Incorrect.")
            lines.append(f"That note was {self.note.name}-{self.note.octave}.")

        elif mode == "interval":
            g1 = self.first_picker.get()
            g2 = self.second_picker.get()
            gi = self.interval_combo.get()
            if g1 is None or g2 is None or not gi:
                messagebox.showinfo("Incomplete", "Pick both notes and an interval.")
                return
            if notes.note_to_int(g1) == notes.note_to_int(self.interval.get_first_note_name()):
                PythonEarTrainer.updateStats(1.0)
                lines.append(f"First note: correct ({self.interval.get_first_note_name()}).")
            else:
                PythonEarTrainer.updateStats(0.0)
                lines.append(f"First note: incorrect. It was {self.interval.get_first_note_name()}.")
            if notes.note_to_int(g2) == notes.note_to_int(self.interval.get_second_note_name()):
                PythonEarTrainer.updateStats(1.0)
                lines.append(f"Second note: correct ({self.interval.get_second_note_name()}).")
            else:
                PythonEarTrainer.updateStats(0.0)
                lines.append(f"Second note: incorrect. It was {self.interval.get_second_note_name()}.")
            if gi in self.interval.intervalType:
                PythonEarTrainer.updateStats(1.0)
                lines.append(f"Interval: correct ({gi}).")
            else:
                PythonEarTrainer.updateStats(0.0)
                lines.append(f"Interval: incorrect. It was {self.interval.intervalType}.")

        elif mode in ("chord", "missing"):
            chord = self.chord
            if PythonEarTrainer.guessRootOfChord:
                rg = self.root_picker.get()
                if rg is None:
                    messagebox.showinfo("Incomplete", "Pick the root note.")
                    return
                if notes.note_to_int(rg) == notes.note_to_int(chord.randomRoot):
                    PythonEarTrainer.updateStats(1.0)
                    lines.append(f"Root: correct ({chord.randomRoot}).")
                else:
                    PythonEarTrainer.updateStats(0.0)
                    lines.append(f"Root: incorrect. It was {chord.randomRoot}.")
            if PythonEarTrainer.guessChordType:
                tg = self.type_combo.get()
                if not tg:
                    messagebox.showinfo("Incomplete", "Pick the chord type.")
                    return
                if tg == chord.chordName:
                    PythonEarTrainer.updateStats(1.0)
                    lines.append(f"Type: correct ({chord.chordName}).")
                else:
                    PythonEarTrainer.updateStats(0.0)
                    lines.append(f"Type: incorrect. It was {chord.chordName}.")
            if mode == "missing":
                mg = self.missing_picker.get()
                if mg is None:
                    messagebox.showinfo("Incomplete", "Pick the missing note.")
                    return
                if notes.note_to_int(mg) == notes.note_to_int(self.missing_tone):
                    PythonEarTrainer.updateStats(1.0)
                    lines.append(f"Missing tone: correct ({self.missing_tone}).")
                else:
                    PythonEarTrainer.updateStats(0.0)
                    lines.append(f"Missing tone: incorrect. It was {self.missing_tone}.")
            lines.append(f"The chord was {chord.randomRoot} {chord.chordName} ({', '.join(chord.chordTones)}).")

        self.feedback.config(text="\n".join(lines))
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="normal")
        self._update_stats_label()

    def _update_stats_label(self):
        self.stats_label.config(
            text=(
                f"Correct: {PythonEarTrainer.correctGuesses}   "
                f"Attempts: {PythonEarTrainer.totalAttempts}   "
                f"Percent: {PythonEarTrainer.percentCorrect or '-'}"
            )
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = EarTrainerApp()
    app.withdraw()  # hide until the soundfont is loaded

    soundfont = sys.argv[1] if len(sys.argv) > 1 else None
    if not soundfont:
        soundfont = filedialog.askopenfilename(
            parent=app,
            title="Select a SoundFont (.sf2)",
            filetypes=[("SoundFont", "*.sf2"), ("All files", "*.*")],
        )
    if not soundfont:
        messagebox.showerror("No soundfont", "A soundfont file is required to play audio.")
        app.destroy()
        return

    try:
        # In Docker we force the PulseAudio driver (EAR_TRAINER_AUDIO_DRIVER=pulseaudio)
        # so audio reaches the host PulseAudio server over TCP. On a native host the var
        # is unset and fluidsynth picks the platform default (coreaudio on macOS, etc.).
        driver = os.environ.get("EAR_TRAINER_AUDIO_DRIVER")
        if driver:
            fluidsynth.init(soundfont, driver)
        else:
            fluidsynth.init(soundfont)
    except Exception as exc:  # surfaces the libfluidsynth / soundfont errors
        messagebox.showerror("Audio init failed", f"Couldn't initialize fluidsynth:\n{exc}")
        app.destroy()
        return

    app.deiconify()
    app.mainloop()


if __name__ == "__main__":
    main()