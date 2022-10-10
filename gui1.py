import copy
import os
import sys
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
import numpy as np
import pyaudio
from pyaudio import PyAudio, paInt16
import math

frequency = "Not Listening"
class ColorCalculator():
    
    def findColor(note_name):
        bg_color = '#000000'
        
        if(note_name=="C"):
            bg_color='#28ff00'
        elif(note_name=="C#"):
            bg_color='#00ffe8'
        elif(note_name=="D"):
            bg_color='#007cff'
        elif(note_name=="D#"):
            bg_color='#0500ff'
        elif(note_name=="E"):
            bg_color='#4500ea'
        elif(note_name=="F"):
            bg_color='#57009e'
        elif(note_name=="F#"):
            bg_color='#740000'
        elif(note_name=="G"):
            bg_color='#b30000'
        elif(note_name=="G#"):
            bg_color='#ee0000'
        elif(note_name=="A"):
            bg_color='#ff6300'
        elif(note_name=="A#"):
            bg_color='#ffec00'
        else:
            bg_color='#99ff00'
        return bg_color
    
    @staticmethod
    def sound_frequency_to_wavelength(frequency):
        c=299792458
        #print(frequency)
        for i in range(30,50):
            upper_octave_freq=frequency*math.pow(2, i)
            upper_octave_freq_THz=(upper_octave_freq/(math.pow(10,12)))
            AudioListener.CURRENT_FREQUENCY_THZ = upper_octave_freq_THz

            if(upper_octave_freq_THz>= 380.0 and upper_octave_freq_THz<= 770.0):
                if(upper_octave_freq_THz != 0.0):
                    wavelenght=(c/upper_octave_freq)*math.pow(10,9) #wavelenght in nanometer
                    App.wavelenght=wavelenght
                    AudioListener.CURRENT_OCTAVE=i
                    print("upper freq: {0} THz \t wavelenght: {1}".format(str(upper_octave_freq_THz), str(wavelenght)))
        
        
    def WaveLength_to_RGB(WaveLength):
        #print(WaveLength)
        R=App.R / 255
        G=App.G / 255
        B=App.B/ 255
        if ((WaveLength >= 380.0) and (WaveLength <= 410.0)):
            R =0.6-0.41*(410.0-WaveLength)/30.0
            G = 0.0
            B = 0.39+0.6*(410.0-WaveLength)/30.0

        elif ((WaveLength >= 410.0) and (WaveLength <= 440.0)):
            R =0.19-0.19*(440.0-WaveLength)/30.0
            G = 0.0
            B = 1.0

        elif ((WaveLength >= 440.0) and (WaveLength<= 490.0)):
            R =0
            G = 1-(490.0-WaveLength)/50.0
            B = 1.0

        elif ((WaveLength >= 490.0) and (WaveLength <= 510.0)):
            R =0
            G = 1
            B = (510.0-WaveLength)/20.0

        elif ((WaveLength >= 510.0) and (WaveLength <= 580.0)):
            R =1-(580.0-WaveLength)/70.0
            G = 1
            B = 0
        elif ((WaveLength >= 580.0) and (WaveLength<= 640.0)):
            R =1
            G = (640-WaveLength)/60
            B = 0
        elif ((WaveLength >= 640.0) and (WaveLength <= 700.0)):
            R =1
            G = 0
            B = 0
        elif ((WaveLength >= 700.0) and (WaveLength<= 780.0)):
            R =0.35+0.65*(780.0-WaveLength)/80.0
            G = 0
            B = 0
        
        result=255*np.array([R,G,B])
        #print(result)
        App.R = R * 255
        App.G = G * 255
        App.B = B * 255
        return result
    
    @staticmethod
    def rgb_to_hex(rgb):
        """translates an rgb tuple of int to a tkinter friendly color code
        """
        return "#%02x%02x%02x" % rgb 

    @staticmethod
    def rgbtohex(r,g,b):
        return f'#{r:02x}{g:02x}{b:02x}'

        

class AudioListener():
    is_listening = True

    SAMPLING_RATE = 48000  # mac hardware: 44100, 48000, 96000
    CHUNK_SIZE = 1024  # number of samples
    BUFFER_TIMES = 50  # buffer length = CHUNK_SIZE * BUFFER_TIMES
    ZERO_PADDING = 3  # times the buffer length
    NUM_HPS = 3  # Harmonic Product Spectrum
    a4_freq = 440

    CURRENT_NOTE_NAME = ''
    CURRENT_FREQUENCY = 0
    CURRENT_FREQUENCY_THZ = 0
    CURRENT_OCTAVE = 0

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    def __init__(self, *args, **kwargs):
        
        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES)
        self.hanning_window = np.hanning(len(self.buffer))
        self.running = False
        self.frequency = 0
        
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
        AudioListener.CURRENT_NOTE_NAME = AudioListener.NOTE_NAMES[int(round(number) % 12)] 
        return AudioListener.CURRENT_NOTE_NAME + str(number/12 - 1)

    @staticmethod
    def frequency_to_note_name(frequency, a4_freq):
        """ converts frequency to note name (for example: 440 returns 'A') """
        number = AudioListener.frequency_to_number(frequency, a4_freq)
        note_name = AudioListener.number_to_note_name(number)
        return note_name
           
    def listenLoop(self, mainApp):
        self.running = True
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
            # Get frequency of maximum response in range
            frequency = (round(frequencies[np.argmax(magnitude_data)], 2))

            # Get note number and nearest note
            n = self.frequency_to_number(frequency, 440)
            n0 = int(round(n))

            num_frames += 1

            if num_frames >= self.BUFFER_TIMES:
                AudioListener.CURRENT_FREQUENCY = frequency
                self.frequency = 'note: {:>3s} {:+.2f} \n freq: {:7.2f} Hz \n {}th octave freq: {:7.2f} THz'.format(self.number_to_note_name(n0), n-n0, AudioListener.CURRENT_FREQUENCY, AudioListener.CURRENT_OCTAVE, AudioListener.CURRENT_FREQUENCY_THZ)
                
                
class App(tk.Tk):
    BG_COLOR = '#000000'
    R = 0
    G = 0
    B = 0
    wavelenght=0
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.title('Dides Tuner')
        self.geometry('400x150')

        self.label = tk.Label(self, text='Hello, Press to start!')
        self.label.pack()

        self.btnStart = tk.Button(self, text="Start", command=lambda: self.start_clicked())
        self.btnStart.pack()

        self.btnStop = tk.Button(self, text="Stop", command=lambda: self.stop_clicked())
        self.btnStop.pack()

        self.frequencyLabel = tk.Label(self, text=frequency)
        self.frequencyLabel.pack()
        self.frequencyLabel.after(100, self.update)

        self.listener = AudioListener()
        self.listenLoopThread = threading.Thread(target=lambda: self.listener.listenLoop(self), daemon=True)
        self.bgColorThread = threading.Thread(target=lambda: self.update_bg() , daemon=True)
        
    def stop_clicked(self):
        #print(frequency)
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
            self.frequencyLabel.configure(text=self.listener.frequency)

        self.frequencyLabel.after(100, self.update)

    def update_bg(self):
        while(True):
            ColorCalculator.sound_frequency_to_wavelength(AudioListener.CURRENT_FREQUENCY)
            ColorCalculator.WaveLength_to_RGB(App.wavelenght)
            color_code_from_freq = ColorCalculator.rgb_to_hex((int(App.R),
                                                                int(App.G),
                                                                int(App.B)))
            self.configure(bg=color_code_from_freq) 

if __name__ == "__main__":
    app = App()
    app.mainloop()