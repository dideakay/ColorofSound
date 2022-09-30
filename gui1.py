import copy
import os
import sys
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
from turtle import bgcolor
import numpy as np
import pyaudio
from pyaudio import PyAudio, paInt16

frequency = "Not Listening"
class ColorCalculator():
    global note_name_global

    def findColor():
        global bg_color
        global note_name_global
        if(note_name_global=="C"):
            bg_color='#28ff00'
        elif(note_name_global=="C#"):
            bg_color='#00ffe8'
        elif(note_name_global=="D"):
            bg_color='#007cff'
        elif(note_name_global=="D#"):
            bg_color='#0500ff'
        elif(note_name_global=="E"):
            bg_color='#4500ea'
        elif(note_name_global=="F"):
            bg_color='#57009e'
        elif(note_name_global=="F#"):
            bg_color='#740000'
        elif(note_name_global=="G"):
            bg_color='#b30000'
        elif(note_name_global=="G#"):
            bg_color='#ee0000'
        elif(note_name_global=="A"):
            bg_color='#ff6300'
        elif(note_name_global=="A#"):
            bg_color='#ffec00'
        else:
            bg_color='#99ff00'

class AudioListener():
    is_listening = True
    global note_name_global

    SAMPLING_RATE = 48000  # mac hardware: 44100, 48000, 96000
    CHUNK_SIZE = 1024  # number of samples
    BUFFER_TIMES = 50  # buffer length = CHUNK_SIZE * BUFFER_TIMES
    ZERO_PADDING = 3  # times the buffer length
    NUM_HPS = 3  # Harmonic Product Spectrum
    a4_freq = 440

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    def __init__(self, *args, **kwargs):
        
        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES)
        self.hanning_window = np.hanning(len(self.buffer))
        self.running = False

        self.audio_object = PyAudio()
        self.stream = self.audio_object.open(format=paInt16,
                                                channels=1,
                                                rate=self.SAMPLING_RATE,
                                                input=True,
                                                output=False,
                                                frames_per_buffer=self.CHUNK_SIZE)
    
    @staticmethod
    def frequency_to_number(freq, a4_freq):
        """ converts a frequency to a note number (for example: A4 is 69)"""

        if freq == 0:
            sys.stderr.write("Error: No frequency data. Program has potentially no access to microphone\n")
            return 0

        return 12 * np.log2(freq / a4_freq) + 69

    @staticmethod
    def number_to_frequency(number, a4_freq):
        """ converts a note number (A4 is 69) back to a frequency """

        return a4_freq * 2.0**((number - 69) / 12.0)

    @staticmethod
    def number_to_note_name(number):
        """ converts a note number to a note name (for example: 69 returns 'A', 70 returns 'A#', ... ) """
        global note_name_global
        note_name_global = AudioListener.NOTE_NAMES[int(round(number) % 12)] 
        return note_name_global + str(number/12 - 1)

    @staticmethod
    def frequency_to_note_name(frequency, a4_freq):
        """ converts frequency to note name (for example: 440 returns 'A') """
        global note_name_global
        number = AudioListener.frequency_to_number(frequency, a4_freq)
        note_name = AudioListener.number_to_note_name(number)
        return note_name
           
    def listenLoop(self, mainApp):
        self.running = True
        global frequency
        num_frames = 0
        self.stream.start_stream()

        while (self.stream.is_active() and self.is_listening and self.running):
            
            # read microphone data
            data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
            data = np.frombuffer(data, dtype=np.int16)

            # Shift the buffer down and new data in
            self.buffer[:-self.CHUNK_SIZE] = self.buffer[self.CHUNK_SIZE:]
            self.buffer[-self.CHUNK_SIZE:] = data

            # apply the fourier transformation on the whole buffer (with zero-padding + hanning window)
            magnitude_data = abs(np.fft.fft(np.pad(self.buffer * self.hanning_window,
                                                    (0, len(self.buffer) * self.ZERO_PADDING),
                                                    "constant")))
            # only use the first half of the fft output data
            magnitude_data = magnitude_data[:int(len(magnitude_data) / 2)]

            # HPS: multiply data by itself with different scalings (Harmonic Product Spectrum)
            magnitude_data_orig = copy.deepcopy(magnitude_data)
            for i in range(2, self.NUM_HPS+1, 1):
                hps_len = int(np.ceil(len(magnitude_data) / i))
                magnitude_data[:hps_len] *= magnitude_data_orig[::i]  # multiply every i element

            # get the corresponding frequency array
            frequencies = np.fft.fftfreq(int((len(magnitude_data) * 2) / 1),
                                            1. / self.SAMPLING_RATE)

            # set magnitude of all frequencies below 60Hz to zero
            for i, freq in enumerate(frequencies):
                if freq > 60:
                    magnitude_data[:i - 1] = 0
                    break
            # put the frequency of the loudest tone into the queue
                #self.queue.put(round(frequencies[np.argmax(magnitude_data)], 2))

            # Get frequency of maximum response in range
            freq = (round(frequencies[np.argmax(magnitude_data)], 2))
            #(np.abs(fft[self.imin:self.imax]).argmax() + self.imin) * self.FREQ_STEP

            # Get note number and nearest note
            n = self.frequency_to_number(freq, 440)
            n0 = int(round(n))
            # Console output once we have a full buffer
            num_frames += 1

            #AudioListener.note_to_rgb()

            if num_frames >= self.BUFFER_TIMES:
                frequency = 'freq: {:7.2f} Hz     note: {:>3s} {:+.2f}'.format(freq, self.number_to_note_name(n0), n-n0)
                print(frequency)
                
class App(tk.Tk):
    global frequency
    global bg_color
    global note_name_global
    note_name_global = 'G'
    bg_color = '#40E0D0'
    def __init__(self, *args, **kwargs):
        super().__init__()

        # configure the root window
        self.title('Dides Tuner')
        self.geometry('400x150')
        
        
        #self.configure(bg=bg_color)
        #self.update_bg()

        # label
        self.label = tk.Label(self, text='Hello, Press to start!')
        self.label.pack()
        
        # buttons
        self.btnStart = tk.Button(self, text="Start", command=lambda: self.start_clicked())
        self.btnStart.pack()

        self.btnStop = tk.Button(self, text="Stop", command=lambda: self.stop_clicked())
        self.btnStop.pack()

        self.frequencyLabel = tk.Label(self, text=frequency)
        self.frequencyLabel.pack()
        self.frequencyLabel.after(1000, self.update)

        self.listener = AudioListener()
        self.listenLoopThread = threading.Thread(target=lambda: self.listener.listenLoop(self), daemon=True)
        self.bgColorThread = threading.Thread(target=lambda: self.update_bg() , daemon=True)
        
    def stop_clicked(self):
        print(frequency)
        self.listener.is_listening = False
        self.listenLoopThread.join()
        self.listenLoopThread = threading.Thread(target= lambda: self.listener.listenLoop(self), daemon=True)
        self.btnStart['state'] = NORMAL
        self.btnStop['state'] = DISABLED
        self.frequencyLabel["text"]="Not Listening"
        
    def start_clicked(self):
        self.listener.is_listening = True
        self.listenLoopThread.start()
        self.bgColorThread.start()
        self.btnStart['state'] = DISABLED
        self.btnStop['state'] = NORMAL
    
    def update(self):
    # update the label every 1 second 
        if(self.listener.is_listening == True):
            self.frequencyLabel.configure(text=frequency)
            #self.configure(bg=bg_color)

        # schedule another timer
        self.frequencyLabel.after(1000, self.update)

    def update_bg(self):
        while(True):
            ColorCalculator.findColor()
            self.configure(bg=bg_color)
            print("----------------------------------------------------------------------")
            print(bg_color)

    

if __name__ == "__main__":
    app = App()
    app.mainloop()