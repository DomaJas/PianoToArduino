import pygame
import mido
import time
import numpy as np
import tkinter as tk
from tkinter import filedialog

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=256)
pygame.mixer.set_num_channels(64)

WIDTH = 1400
HEIGHT = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arduino Piano Composer")

WHITE=(255,255,255)
BLACK=(0,0,0)
GRAY=(200,200,200)
RED=(200,0,0)
GREEN=(0,200,0)
BLUE=(0,100,200)
YELLOW=(255,255,0)

font=pygame.font.SysFont("Arial",20)

note_names=["C","CS","D","DS","E","F","FS","G","GS","A","AS","B"]
active_channels={}
press_times = {}
debug_lines = []
MAX_DEBUG = 6
def midi_to_note(n):
    octave=(n//12)-1
    name=note_names[n%12]
    return f"NOTE_{name}{octave}"

def midi_to_freq(n):
    return 440*2**((n-69)/12)

def import_midi():
    global recorded, record_start_time

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid *.midi")])
    if not file_path:
        return

    midi_file = mido.MidiFile(file_path)
    recorded = []
    current_time = 0

    note_on_times = {}

    for msg in midi_file:
        current_time += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            note_on_times[msg.note] = current_time
        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in note_on_times:
                start = note_on_times[msg.note]
                dur = current_time - start
                recorded.append((msg.note, start, dur))
                del note_on_times[msg.note]

    print(f"MIDI imported: {file_path}, {len(recorded)} notes")

def add_debug(midi, duration):

    name = midi_to_note(midi)

    text = f"{name}  {duration:.3f}s"

    debug_lines.insert(0, text)

    if len(debug_lines) > MAX_DEBUG:
        debug_lines.pop()

# ---------- SOUND ----------

sound_cache={}

BPM = 120

quarter = 60000 / BPM

def quantize(ms):

    table = [
        (quarter*4, 1),
        (quarter*2, 2),
        (quarter, 4),
        (quarter/2, 8),
        (quarter/4, 16)
    ]

    for dur, val in table:
        if ms >= dur*0.75:
            return val

    return 16

def play_note(midi):

    if midi in sound_cache:
        sound = sound_cache[midi]
    else:

        freq = midi_to_freq(midi)

        brightness = min(1.5, freq / 500)

        duration = 1.5
        sr = 44100

        t = np.linspace(0, duration, int(sr * duration), False)

        wave = (
                1.0 * np.sin(freq * 2 * np.pi * t) +
                0.35 * np.sin(freq * 2 * 2 * np.pi * t) +
                0.15 * np.sin(freq * 3 * 2 * np.pi * t) +
                0.08 * np.sin(freq * 4 * 2 * np.pi * t)
        )

        # ADSR envelope
        attack = int(sr*0.02)
        decay = int(sr*0.05)
        release = int(sr*0.2)

        sustain_level = 0.6

        envelope = np.ones_like(wave)

        envelope[:attack] = np.linspace(0,1,attack)
        envelope[attack:attack+decay] = np.linspace(1,sustain_level,decay)
        envelope[-release:] = np.linspace(sustain_level,0,release)

        wave /= np.max(np.abs(wave))

        wave *= 0.2 * brightness

        audio = (wave * 32767).astype(np.int16)

        audio = np.column_stack((audio, audio))

        sound = pygame.sndarray.make_sound(audio)

        sound_cache[midi] = sound

    sound.set_volume(volume)
    sound.play()
# ---------- PIANO ----------

WHITE_KEYS=[]
BLACK_KEYS=[]

white_w = WIDTH / 52
white_h = 200

start_midi = 21

white_index = 0
white_positions = {}

for i in range(88):

    midi = start_midi + i
    note = midi % 12

    # White
    if note not in [1,3,6,8,10]:

        x = white_index * white_w

        rect = pygame.Rect(x,200,white_w,white_h)

        WHITE_KEYS.append((rect,midi))

        white_positions[midi] = x

        white_index += 1


# Black
for i in range(88):

    midi = start_midi + i
    note = midi % 12

    if note in [1,3,6,8,10]:

        prev_white = midi - 1

        if prev_white in white_positions:

            x = white_positions[prev_white] + white_w * 0.7

            rect = pygame.Rect(x,200,white_w*0.6,120)

            BLACK_KEYS.append((rect,midi))

pressed=set()

# ---------- RECORDING ----------

recording = False
recorded = []

note_start_times = {}
record_start_time = None

# ---------- MIDI ----------

try:
    port=mido.open_input()
    print("MIDI connected:",port)
except:
    port=None
    print("No MIDI keyboard")

# ---------- BUTTONS ----------

import_btn = pygame.Rect(480, 20, 140, 40)
record_btn=pygame.Rect(20,20,120,40)
stop_btn=pygame.Rect(160,20,120,40)
export_btn=pygame.Rect(300,20,160,40)
clear_btn = pygame.Rect(180,70,100,30)

volume = 0.4
slider_rect = pygame.Rect(700, 30, 200, 10)
slider_knob = pygame.Rect(700 + volume*200 - 5, 25, 10, 20)
dragging_slider = False

# ---------- MAIN LOOP ----------

running=True

while running:

    screen.fill(GRAY)

    pygame.draw.rect(screen,RED,record_btn)
    pygame.draw.rect(screen,BLUE,stop_btn)
    pygame.draw.rect(screen,BLACK,export_btn)

    pygame.draw.rect(screen, (120, 120, 120), slider_rect)
    pygame.draw.rect(screen, (220, 220, 220), slider_knob)

    screen.blit(font.render("Volume", True, BLACK), (630, 20))

    screen.blit(font.render("RECORD",True,WHITE),(30,30))
    screen.blit(font.render("STOP",True,WHITE),(185,30))
    screen.blit(font.render("EXPORT",True,WHITE),(320,30))

    pygame.draw.rect(screen, (150, 0, 150), import_btn)
    screen.blit(font.render("IMPORT MIDI", True, WHITE), (485, 30))

    pygame.draw.rect(screen, GREEN, clear_btn)
    screen.blit(font.render("CLEAR", True, WHITE), (195, 75))

    # white keys
    for rect,midi in WHITE_KEYS:

        color=YELLOW if midi in pressed else WHITE

        pygame.draw.rect(screen,color,rect)
        pygame.draw.rect(screen,BLACK,rect,1)

    # black keys
    for rect,midi in BLACK_KEYS:

        color=YELLOW if midi in pressed else BLACK

        pygame.draw.rect(screen,color,rect)

    y = 70

    for line in debug_lines:
        txt = font.render(line, True, BLACK)

        screen.blit(txt, (20, y))

        y += 20

    pygame.display.flip()

    if dragging_slider:
        mx = pygame.mouse.get_pos()[0]

        mx = max(slider_rect.left, min(mx, slider_rect.right))

        slider_knob.x = mx - 5

        volume = (mx - slider_rect.left) / slider_rect.width

    # ---------- MIDI INPUT ----------

    if port:

        for msg in port.iter_pending():

            if msg.type == "note_on" and msg.velocity > 0:

                pressed.add(msg.note)
                play_note(msg.note)

                press_times[msg.note] = time.perf_counter()

                if recording:
                    if record_start_time is None:
                        record_start_time = time.perf_counter()

                    note_start_times[msg.note] = time.perf_counter()

            if msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):

                if msg.note in pressed:
                    pressed.remove(msg.note)

                if msg.note in press_times:
                    duration = time.perf_counter() - press_times[msg.note]
                    add_debug(msg.note, duration)
                    del press_times[msg.note]

                # --- Note Write ---
                if recording and msg.note in note_start_times:
                    start = note_start_times[msg.note]
                    dur = time.perf_counter() - start
                    offset = start - record_start_time

                    recorded.append((msg.note, offset, dur))

                    del note_start_times[msg.note]

    # ---------- EVENTS ----------

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.MOUSEBUTTONDOWN:

            pos=pygame.mouse.get_pos()

            if record_btn.collidepoint(pos):

                recording=True
                recorded=[]
                last_time=None
                record_start_time = None
                print("Recording...")

            elif import_btn.collidepoint(pos):
                import_midi()

            elif slider_knob.collidepoint(event.pos):
                dragging_slider = True

            elif stop_btn.collidepoint(pos):
                if recording == False:
                    print("Nothing to stop!")
                    break

                recording=False
                print("Stopped")



            elif export_btn.collidepoint(pos):

                melody = []

                durations = []

                last_end = 0

                for note, offset, dur in recorded:

                    # --- Pause ---

                    rest = offset - last_end

                    if rest > 0.05:

                        melody.append("REST")

                        durations.append(quantize(rest * 1000))

                    # --- Note ---

                    melody.append(midi_to_note(note))

                    durations.append(quantize(dur * 1000))

                    last_end = offset + dur

                print("\nint melody[] = {")

                print(",".join(melody))

                print("};")

                print("\nint durations[] = {")

                print(",".join(map(str, durations)))

                print("};")

            elif clear_btn.collidepoint(pos):

                debug_lines.clear()

            else:

                # check piano click
                for rect,midi in BLACK_KEYS:

                    if rect.collidepoint(pos):

                        pressed.add(midi)
                        play_note(midi)

                        press_times[midi] = time.perf_counter()

                for rect,midi in WHITE_KEYS:

                    if rect.collidepoint(pos):

                        pressed.add(midi)
                        play_note(midi)

                        press_times[midi] = time.perf_counter()

        if event.type==pygame.MOUSEBUTTONUP:

            dragging_slider = False

            for midi in list(pressed):

                if midi in press_times:
                    duration = time.perf_counter() - press_times[midi]

                    add_debug(midi, duration)

                    if recording:
                        if record_start_time is None:
                            record_start_time = press_times[midi]

                        start = press_times[midi]
                        dur = duration
                        offset = start - record_start_time

                        recorded.append((midi, offset, dur))

                    del press_times[midi]

            pressed.clear()

pygame.quit()