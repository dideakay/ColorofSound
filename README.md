
# Color of Sound Tuner


![image](https://user-images.githubusercontent.com/59506252/196058085-725fa613-4c45-41a2-8f35-1dbaee6165ad.png)


## Table of Contents

- [Project Owner's Goal](#project-owners-goal)
- [Features](#features)
    - [Existing features](#existing-features)
    - [Features that will be implemented](#features-that-will-be-implemented)
- [Technologies Used](#technologies-used)
- [Credits](#credits)

## Project Owner's Goal

In physics, sound and light can both be represented as waves. Although the nature of sound and light is different, it is possible to map sound frequencies to light frequencies. With this project it is aimed to experience sound not only with hearing but also with the sight.

## Features

### Existing features

- Detecting frequency and note from audio input 
- Conversion of sound frequency to light frequency
- Changing of background color according to audio input

### Features that will be implemented

- Allow users to change A4 reference frequency
- Detecting harmonic frequencies in the audio input
- gui2.py has limited range of wavelengths - the json file should be made enough to cover all wavelengths


## Technologies used

 Python
 tkinter for UI
 
#### Obtaining RGB values:
- Wolfram Alpha's "Convert Wavelength to Color" widget is used to obtain the json file used in gui2.py
- Repository "shadercoder/wavelength_to_rgb.R" is used to implement the conversion in gui1.py
 

## Credits

- https://www.flutopedia.com/sound_color.htm 
- https://www.wolframalpha.com/widgets/gallery/view.jsp?id=5072e9b72faacd73c9a4e4cb36ad08d
- https://gist.github.com/shadercoder/00dfd19d44d0fdbce95b38cdc476c162
