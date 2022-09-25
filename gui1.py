from ast import Break
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
import numpy as np
import pyaudio

class AudioListener():
    is_listening = True
    def __init__(self, *args, **kwargs):
        
        self.NOTE_MIN = 60       # C4
        self.NOTE_MAX = 69       # A4
        self.FSAMP = 22050       # Sampling frequency in Hz
        self.FRAME_SIZE = 2048   # How many samples per frame?
        self.FRAMES_PER_FFT = 16 # FFT takes average across how many frames?

        self.SAMPLES_PER_FFT = self.FRAME_SIZE*self.FRAMES_PER_FFT
        self.FREQ_STEP = float(self.FSAMP)/self.SAMPLES_PER_FFT

        self.NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

        self.imin = max(0, int(np.floor(self.note_to_fftbin(self.NOTE_MIN-1))))
        self.imax = min(self.SAMPLES_PER_FFT, int(np.ceil(self.note_to_fftbin(self.NOTE_MAX+1))))

        # Allocate space to run an FFT. 
        self.buf = np.zeros(self.SAMPLES_PER_FFT, dtype=np.float32)

        # Initialize audio
        self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=self.FSAMP,
                                        input=True,
                                        frames_per_buffer=self.FRAME_SIZE)

       
    def freq_to_number(self, f): return 69 + 12*np.log2(f/440.0)
    def number_to_freq(self, n): return 440 * 2.0**((n-69)/12.0)
    def note_name(self, n): return self.NOTE_NAMES[n % 12] + str(n/12 - 1)

    def note_to_fftbin(self, n): return self.number_to_freq(n)/self.FREQ_STEP

    def listenLoop(self):
        num_frames = 0
        self.stream.start_stream()

        # Create Hanning window function
        window = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, self.SAMPLES_PER_FFT, False)))

        while (self.stream.is_active() and self.is_listening):
            if (self.is_listening==False):
                Break
            # Shift the buffer down and new data in
            self.buf[:-self.FRAME_SIZE] = self.buf[self.FRAME_SIZE:]
            self.buf[-self.FRAME_SIZE:] = np.fromstring(self.stream.read(self.FRAME_SIZE), np.int16)

            # Run the FFT on the windowed buffer
            fft = np.fft.rfft(self.buf * window)

            # Get frequency of maximum response in range
            freq = (np.abs(fft[self.imin:self.imax]).argmax() + self.imin) * self.FREQ_STEP

            # Get note number and nearest note
            n = self.freq_to_number(freq)
            n0 = int(round(n))

            # Console output once we have a full buffer
            num_frames += 1

            if num_frames >= self.FRAMES_PER_FFT:
                print ('freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(
                    freq, self.note_name(n0), n-n0))

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__()

        # configure the root window
        self.title('Dides Tuner')
        self.geometry('300x150')

        # label
        self.label = tk.Label(self, text='Hello, Press to start! You can read the notes from console output!')
        self.label.pack()
        
        # button
        self.btnStart = tk.Button(self, text="Start", command=lambda: self.start_clicked())
        self.btnStart.pack()

        self.btnStop = tk.Button(self, text="Stop", command=lambda: self.stop_clicked())
        self.btnStop.pack()

        self.listener = AudioListener()

        self.listenLoopThread = threading.Thread(target= self.listener.listenLoop, daemon=True)
    
    def stop_clicked(self):
        self.listener.is_listening = False
        self.listenLoopThread.join()
        self.listener = AudioListener()
        self.listenLoopThread = threading.Thread(target= self.listener.listenLoop, daemon=True)
        self.btnStart['state'] = NORMAL
        self.btnStop['state'] = DISABLED
        

    def start_clicked(self):
        self.listener.is_listening = True
        self.listenLoopThread.start()
        self.btnStart['state'] = DISABLED
        self.btnStop['state'] = NORMAL
      
if __name__ == "__main__":
    app = App()
    app.mainloop()