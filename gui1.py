from tkinter import *
import numpy as np
import pyaudio

NOTE_MIN = 60       # C4
NOTE_MAX = 69       # A4
FSAMP = 22050       # Sampling frequency in Hz
FRAME_SIZE = 2048   # How many samples per frame?
FRAMES_PER_FFT = 16 # FFT takes average across how many frames?
listen = False

SAMPLES_PER_FFT = FRAME_SIZE*FRAMES_PER_FFT
FREQ_STEP = float(FSAMP)/SAMPLES_PER_FFT

NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(n/12 - 1)

def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))



# Allocate space to run an FFT. 
buf = np.zeros(SAMPLES_PER_FFT, dtype=np.float32)
num_frames = 0

# Initialize audio
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,
                                rate=FSAMP,
                                input=True,
                                frames_per_buffer=FRAME_SIZE)


def listenLoop(listenGlobal):
    global listen
    num_frames = 0
    stream.start_stream()
    
    # Create Hanning window function
    window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, SAMPLES_PER_FFT, False)))

    while (stream.is_active() and listen):

        # Shift the buffer down and new data in
        buf[:-FRAME_SIZE] = buf[FRAME_SIZE:]
        buf[-FRAME_SIZE:] = np.fromstring(stream.read(FRAME_SIZE), np.int16)

        # Run the FFT on the windowed buffer
        fft = np.fft.rfft(buf * window)

        # Get frequency of maximum response in range
        freq = (np.abs(fft[imin:imax]).argmax() + imin) * FREQ_STEP

        # Get note number and nearest note
        n = freq_to_number(freq)
        n0 = int(round(n))

        # Console output once we have a full buffer
        num_frames += 1

        if num_frames >= FRAMES_PER_FFT:
            print ('freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(
                freq, note_name(n0), n-n0))
        

def toggleListen():
    global listen
    if listen == True:
        listen = False
    else:
        listen = True
    print(listen)

def getListen():
     global listen
     return listen


root = Tk()

button1 = Button(root, text="start / stop",  command=toggleListen)
button1.grid(row=0, column=0)

button1 = Button(root, text="listening", command= lambda: listenLoop(listen))
button1.grid(row=0, column=1)

button1 = Button(root, text="stop")
button1.grid(row=0, column=2)

myLabel1 = Label(root, text="is listening:")
entryField = Entry(root, textvariable=listen)
entryField.grid(row=1, column=0)
myLabel2 = Label(root, text=getListen)




myLabel1.grid(row=1, column=0)
myLabel2.grid(row=1, column=1)

root.mainloop() 