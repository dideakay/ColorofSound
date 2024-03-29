import copy
import json
from multiprocessing.connection import Listener
import os
import sys
import threading
import tkinter as tk
from tkinter import *
import numpy as np
from pyaudio import PyAudio, paInt16
import math

frequency = "Not Listening"

class ColorCalculator():
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.json_file = json.load(open('wolframalpha_wavelengths.json', 'r'))

    @staticmethod
    def sound_frequency_to_wavelength(frequency):
        c=299792458 #speed of light
        for i in range(30,50):
            upper_octave_freq=frequency*math.pow(2, i)
            upper_octave_freq_THz=(upper_octave_freq/(math.pow(10,12)))
            AudioListener.CURRENT_FREQUENCY_THZ = upper_octave_freq_THz

            if(upper_octave_freq_THz>= 380.0 and upper_octave_freq_THz<= 770.0):
                if(upper_octave_freq_THz != 0.0):
                    wavelenght=(c/upper_octave_freq)*math.pow(10,9) #wavelenght in nanometer
                    App.wavelenght=wavelenght
                    AudioListener.CURRENT_OCTAVE=i
        
    def WaveLength_to_RGB_Wolfram(self, WaveLength):
        R=App.R / 255
        G=App.G / 255
        B=App.B/ 255

        for(i, j) in self.json_file.items():
            if(int(i) == int(WaveLength)):
                R = j['r']
                G = j['g']
                B = j['b']
                break
        
        result=255*np.array([R,G,B])
        App.R = R * 255
        App.G = G * 255
        App.B = B * 255
        return result


    def WaveLength_to_RGB(WaveLength):
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
        App.R = R * 255
        App.G = G * 255
        App.B = B * 255
        return result
    
    @staticmethod
    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb 
        
class AudioListener():
    is_listening = True

    SAMPLING_RATE = 48000  # mac hardware: 44100, 48000, 96000
    CHUNK_SIZE = 1024  # number of samples
    BUFFER_TIMES = 10  # buffer length = CHUNK_SIZE * BUFFER_TIMES
    ZERO_PADDING = 3  # times the buffer length
    NUM_HPS = 3  # Harmonic Product Spectrum
    a4_freq = 440

    CURRENT_NOTE_NAME = ''
    CURRENT_FREQUENCY = 0
    CURRENT_FREQUENCY_THZ = 0
    CURRENT_OCTAVE = 0
    FREQUENCY_LABEL = ''

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

    class listenLoop(threading.Thread):
        def __init__(self, audio_listener_instance):
            threading.Thread.__init__(self)
            self.parent = audio_listener_instance

        def run(self):
            self.running = True
            num_frames = 0
            self.parent.stream.start_stream()

            while (self.parent.stream.is_active() and self.parent.is_listening and self.running):
                
                # read microphone data
                data = self.parent.stream.read(self.parent.CHUNK_SIZE, exception_on_overflow=False)
                data = np.frombuffer(data, dtype=np.int16)

                # Shift the buffer down and new data in
                self.parent.buffer[:-self.parent.CHUNK_SIZE] = self.parent.buffer[self.parent.CHUNK_SIZE:]
                self.parent.buffer[-self.parent.CHUNK_SIZE:] = data

                # apply the fourier transformation on the whole buffer (with zero-padding + hanning window)
                magnitude_data = abs(np.fft.fft(np.pad(self.parent.buffer * self.parent.hanning_window,
                                                        (0, len(self.parent.buffer) * self.parent.ZERO_PADDING),
                                                        "constant")))
                # only use the first half of the fft output data
                magnitude_data = magnitude_data[:int(len(magnitude_data) / 2)]

                # HPS: multiply data by itself with different scalings (Harmonic Product Spectrum)
                magnitude_data_orig = copy.deepcopy(magnitude_data)
                for i in range(2, self.parent.NUM_HPS+1, 1):
                    hps_len = int(np.ceil(len(magnitude_data) / i))
                    magnitude_data[:hps_len] *= magnitude_data_orig[::i]  # multiply every i element

                # get the corresponding frequency array
                frequencies = np.fft.fftfreq(int((len(magnitude_data) * 2) / 1),
                                                1. / self.parent.SAMPLING_RATE)

                # set magnitude of all frequencies below 60Hz to zero
                for i, freq in enumerate(frequencies):
                    if freq > 60:
                        magnitude_data[:i - 1] = 0
                        break
                # Get frequency of maximum response in range
                frequency = (round(frequencies[np.argmax(magnitude_data)], 2))

                # Get note number and nearest note
                n = AudioListener.frequency_to_number(frequency, int(AudioListener.a4_freq))
                n0 = int(round(n))

                num_frames += 1

                if num_frames >= self.parent.BUFFER_TIMES:
                    AudioListener.CURRENT_FREQUENCY = frequency
                    self.parent.frequency = 'note: {:s} \n freq: {:7.2f} Hz'.format(self.parent.number_to_note_name(n0).split('.')[0], AudioListener.CURRENT_FREQUENCY)
                
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
        self.listenLoopThread = self.listener.listenLoop(self.listener)

        self.bg_running = False


    def stop_clicked(self):
        self.listener.is_listening = False
        self.bg_running = False
        self.listenLoopThread.join()
        self.btnStart['state'] = NORMAL
        self.btnStop['state'] = DISABLED
        self.frequencyLabel["text"]="Not Listening"
        
    def start_clicked(self):
        self.listener.is_listening = True
        self.bg_running = True
        self.listenLoopThread = self.listener.listenLoop(self.listener)
        self.listenLoopThread.start()
        self.bgColorThread = self.update_bg(self)  
        self.bgColorThread.start()
        self.btnStart['state'] = DISABLED
        self.btnStop['state'] = NORMAL
    
    def update(self):
    # update the label every 0.1 second 
        if(self.listener.is_listening == True):
            self.frequencyLabel.configure(text=self.listener.frequency)

        self.frequencyLabel.after(100, self.update)

    class update_bg(threading.Thread):
        def __init__(self, main_app_instance):
            threading.Thread.__init__(self)
            self.parent = main_app_instance
            
        def run(self):
            color = ColorCalculator()
            while(self.parent.bg_running):
                color.sound_frequency_to_wavelength(AudioListener.CURRENT_FREQUENCY)
                color.WaveLength_to_RGB_Wolfram(self.parent.wavelenght)
                color_code_from_freq = ColorCalculator.rgb_to_hex((int(App.R),
                                                                    int(App.G),
                                                                    int(App.B)))
                self.parent.configure(bg=color_code_from_freq)

if __name__ == "__main__":
    app = App()
    app.mainloop()