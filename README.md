# AudioBeat
### 15-112-Term-Project
**AudioBeat** - A procedurally generated rhythm game for the 15-112 final Term Project.

This game takes any song the user puts in (via the file's path), as well as a few pre-loaded songs, performs beat analysis, then generates a rhythm game to that song. The placement of the buttons, called "Beats" are randomized, so will be different every time the user starts up a song.

A demonstration video can be found [here](https://youtu.be/EWh84U0GZ4I)

The rhythm game itself is heavily based on the game [osu!](http://osu.ppy.sh/), while the beat generation is inspired by [Audiosurf](http://www.audio-surf.com/).

The instructions on how to play the game are included in the game itself. To start AudioBeat, open game.py and run it. Everything else will be taken from the other files in the game folder.

**Note:** AudioBeat was made solely with Windows functionality in mind. As such, *there is no support for other OS's*, and the instructions posted here will most likely only work for Windows computers.

### Modules
AudioBeat was programmed using Python 3.4, with the following modules:

1. Pygame

  Where the game was built on, and runs in. To install, go [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame) and install the correct .whl for your computer by running it with pip.

2. Eztext (module built from Pygame)

  A module for Pygame created by another user. It can be found [here](http://pygame.org/project-EzText-920-.html). The version of the module used in AudioBeat is a modified version of Eztext, where I have made modifications to add functionality to it. The specific additions to Eztext can be found in the comments in the beginning of eztext.py.

3. Librosa
  
  This is what does the beat analysis. Librosa takes in an audio file, and gets the times at which the beats are present. To install, open up the terminal and type 'pip install librosa', without the quotes. Librosa is used in the audio.py file.
  
If you find any bugs, please open an issue on GitHub, and I will attempt to fix the issue.

Enjoy!
