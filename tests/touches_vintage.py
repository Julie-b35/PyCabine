import numpy as np
import pygame
import time
#from pad4pi import rpi_gpio
from Touches import Touches
import sys
import os
from pathlib import Path

# Ajoute le dossier ~/Pycabine/src au path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import Api

api = Api.Api()
api.configure()

#touches = GetCls_Touches()

#import RPi.GPIO as GPIO

# Initialisation de pygame.mixer
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Fréquences DTMF (Hz)
DTMF_FREQS = Touches.DTMF_FREQS

# Générer un son pour une combinaison de fréquences
def generate_dtmf(frequencies, duration=0.2, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = sum(np.sin(2 * np.pi * f * t) for f in frequencies)
    wave = (wave * 32767 / np.max(np.abs(wave))).astype(np.int16)  # Normaliser
    return pygame.sndarray.make_sound(wave)

# Associer chaque touche à un son
dtmf_sounds = {key: generate_dtmf(freqs) for key, freqs in DTMF_FREQS.items()}

# Jouer un son pour une touche
def play_dtmf(key):
    if key in dtmf_sounds:
        print(f"Jouer le son pour la touche : {key}")
        sound = dtmf_sounds[key]
        sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.05)

# Configuration du clavier matriciel
KEYPAD = Touches.KEYPAD

ROW_PINS = Touches.ROW_PINS  # Numérotation BCM
COL_PINS = Touches.COL_PINS    # Numérotation BCM


touches = Touches.Touches(api)
touches.configure()
touches.pre_run()


print(touches)
import sys
sys.exit(1)
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

# Fonction appelée à chaque pression de touche
def handle_key_press(key):
    print(f"Touche appuyée : {key}")
    play_dtmf(key)  # Jouer la note associée à la touche

# Associer la fonction de gestion des touches au clavier
keypad.registerKeyPressHandler(handle_key_press)

try:
    print("Appuyez sur les touches du clavier matriciel (Ctrl+C pour quitter)...")
    while True:
        time.sleep(0.1)  # Attente pour éviter une utilisation CPU excessive
finally:
    print("Nettoyage et arrêt...")
    GPIO.cleanup()
    pygame.mixer.quit()
