import pyttsx3
import random

def play_line():
    engine = pyttsx3.init()
    with open("./lines", "r") as voice_lines:
        line_list: list = voice_lines.readlines()
        rng = random.Random().randint(0, line_list.__len__() - 1)
        text = line_list[rng].split(":", 1)[1].strip()
        engine.say(text)
    engine.runAndWait()
    engine.stop()