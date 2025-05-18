#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("This script is not executable.")

class Mixer :
    def __init__(self, api):
        self.__api = api
    
    def __configureDevice(self):
        import subprocess, os
        # Set the audio output to USB

        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if 'USB Audio' in line:
                device = line.split()[1]
                return device
                #break
        return None
    def configure(self):
        global _
        _ = self.__api._
        id_cart = self.__configureDevice()
        self.__api.getTools_Utils().set_environment("AUDIODEV", f'plughw:{id_cart}')


    def post_configure(self):
        import pygame as _pygame
        self.__pygame = _pygame
        self.__mixer = _pygame.mixer
        self.__music = _pygame.mixer.music
    
    def pre_run(self):
        self.__mixer.init(frequency=44100, size=-16, channels=1)

    def load_music(self, filename, namehint = ""):
        self.__music.load(filename, namehint)

    def play_music(self, loops=0,start=0.0, fade_ms=0):
        self.__music.play(loops,start, fade_ms)

    def get_busy_music(self):
        return self.__music.get_busy()
    
    def get_busy_mixer(self):
        return self.__mixer.get_busy()
    
    def stop_music(self):
        return self.__music.stop()
    
    def make_sound(self, wave):
        #print(self.__pygame)
        return self.__pygame.sndarray.make_sound(wave)
    
    def clean(self):
        self.__mixer.quit()

def init(api):
    return Mixer(api)