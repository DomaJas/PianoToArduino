# PianoToArduino
Use your midi keyboard, midi file or mouse to create songs with arduino buzzer.
OR you can use simple 0.5W speaker with this sheme.

<img width="1175" height="759" alt="circ" src="https://github.com/user-attachments/assets/a635d193-e086-4e0c-b1c1-f079402c7c4d" />

or Simple:
<img width="878" height="662" alt="image" src="https://github.com/user-attachments/assets/78e6e12e-572e-419e-bdc8-842d6cbeb1f4" />


To use Python script just download main.py file and dependencies.

Dependencies: `pygame mido numpy tkinter`

Command: `python -m pip install pygame mido numpy`

Push this script to arduino to get all work:


```CPP
#define REST 0
#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1568
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951
#define NOTE_C8  4186
#define NOTE_CS8 4435
#define NOTE_D8  4699
#define NOTE_DS8 4978

#define BUZZER_PIN 8

int melody[] = {
// Paste Melody From Python Program
};

int durations[] = {
 // Paste Durations From Python Program
};

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

int tempo = 120; // BPM
int isLoop = false; // IsLoop?

void loop() {
  PlayMusic(melody, durations, sizeof(melody) / sizeof(int));
  if (!isLoop) delay(5000);
}

void PlayMusic(int melody[], int durations[], int size) {

  int quarter = 60000 / tempo;

  for (int note = 0; note < size; note++) {

    int noteDuration = quarter * 4 / durations[note];

    if (melody[note] == REST) {
        delay(noteDuration);
    } else {
        tone(BUZZER_PIN, melody[note]);
        delay(noteDuration);
        noTone(BUZZER_PIN);
    }
  }
}
```

![img.png](img.png)

1. Record button, starts record from first pressed note.
2. Debug window with all pressed notes and hold time.
3. Clear debug window from all lines.
4. Stop button for recording.
5. Export button, exports all durations and melody in console.
6. Import .midi file button imports midi file to recording and it ready to export.
7. Local volume slider, does not affect output melody.

# How to use?

1. Run main.py app.
2. When it starts it automatically detects midi keyboard.
3. Whenever you want press "Record" button and start playing when you are ready.
4. After you played your song, press "Stop" button for save.
5. Then press "Export" button for exporting melody and durations to console.
6. Import melody and durations to Arduino file (replace old).
7. Done now when arduino starts you hear your song!

# How import midi?

1. Press "Import Midi" button and select your .midi file.
2. Then when in console you see "MIDI imported: C:/midifile.mid, 33 notes" you are ready to export.
3. Press "Export" button to export whole song in console (melody and durations).
4. Done!

# Recommendations ⚠

This program only supports monophonic MIDI files, where only one instrument/note plays at a time.
Files with multiple instruments or simultaneous notes (polyphony) are not supported and may cause errors or incorrect playback.
