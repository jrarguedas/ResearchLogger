# ResearchLogger
Extension of PyKeylogger, an open-source Python keylogger. Intended for all kinds of writing processes studies.

## Features:
- Portable
- Generates a log with mouse and keyboard activity.
- Takes fixed timed screenshots.
- Takes small pictures of the area around click strokes.

## How to use:
- To start the keylogger:
````
python ResearchLogger.py
````
- To start the translation window (without the keylogger):
````
python ResearchLoggerInterface.py -d YOUR_CHOSEN_PATH
````
where YOUR_CHOSEN_PATH is the directory where you would like to save the target text (the output). If you do not specify a directory:
````
python ResearchLoggerInterface.py
````
by default it will save the file on the current directory.

## Supported platforms:
- Linux (Ubuntu / Debian).
- Windows XP/7