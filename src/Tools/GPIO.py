#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

import time
from time import sleep
LED_GREN = 25

class GPIO:

    BCM = 0
    HIGH = 1
    LOW = 0

    def __init__(self, api):
        #import RPi.GPIO as GPIO
        import lgpio
        #import RPi.GPIO2 as GPIO  # bibliothèque pour gérer les GPIO
        # Associer la fonction de gestion des touches au clavie
        self.__api = api
        self.__handle = lgpio.gpiochip_open(0)
        self.__lgpio = lgpio

        self.OUT = 0
        self.IN = 1
        self.PUD_UP = lgpio.SET_PULL_UP
        self.PUD_DOWN = lgpio.SET_PULL_DOWN
        #self.__GPIO = GPIO

    def pre_run(self):
        #self.__GPIO.setmode(self.__GPIO.BCM)
        self.runLed()

    def setmode(self, mode):
        pass
        
    def runLed(self):
        self.setup(LED_GREN, self.OUT) #Active le contrôle du GPIO
        state = self.input(LED_GREN) #Lit l'état actuel du GPIO, vrai si allumé, faux si éteint

        if not state : #Si GPIO allumé
            self.output(LED_GREN, self.HIGH) #On l'allume
    def setup(self, pin, mode, level=LOW, IFlags=0, pull_up_down=None):
        if pull_up_down is not None:
            if pull_up_down == self.PUD_UP:
                IFlags = self.PUD_UP
            elif pull_up_down == self.PUD_DOWN:
                IFlags = self.PUD_DOWN
        if mode == self.OUT:
            self.__lgpio.gpio_claim_output(self.__handle, pin, level, IFlags)
        elif mode == self.IN:
            self.__lgpio.gpio_claim_input(self.__handle, pin, IFlags)
        else:
            raise ValueError("Invalid mode. Use GPIO.OUT or GPIO.IN.")


    def input(self, pin):
        sleep(0.01)
        return self.__lgpio.gpio_read(self.__handle, pin)
        #return self.__GPIO.input(pin)
    
    def output(self, pin, value):
        if value == self.HIGH:
            self.__lgpio.gpio_write(self.__handle, pin, 1)
        else:
            self.__lgpio.gpio_write(self.__handle, pin, 0)
        #self.__GPIO.output(pin, value)
    
    def add_event_detect(self, *args, **kwargs):
        self.__GPIO.add_event_detect(*args, **kwargs)

    def cleanup(self):
        self.__lgpio.gpiochip_close(self.__handle)  # Ferme le GPIO chip
        pass

    """
    def __getattr__(self, name):
        # Ignorer les attributs non solicités
        if name in ("configure", "post_configure"):  # Ajouter les attributs non solicités
            return super().__getattr__(name)
        elif name in self.__GPIO.__dict__:
           # print(name)
            return getattr(self.__GPIO, name)
        else:
            raise AttributeError(f"GPIO object has no attribute {name}")
    """
    
def init(api):
    return GPIO(api)