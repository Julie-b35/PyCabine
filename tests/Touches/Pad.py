#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

import time
from threading import Thread

class Keypad:
    def __init__(self, GPIO, keypad, row_pins, col_pins):
        self._handlers = {
            "up" :  [],
            "down" : []
        }
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.keypad = keypad
        self.running = True
        self.pressed_keys = set()  # Garder une trace des touches actuellement pressées
        self.polling_thread = None
        self.GPIO = GPIO

    def setup(self):
        # Configurer les lignes comme INPUT (avec résistance pull-up)
        for pin in self.row_pins:
            self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        # Configurer les colonnes comme OUTPUT (initialement HIGH)
        for pin in self.col_pins:
            self.GPIO.setup(pin, self.GPIO.OUT)
            self.GPIO.output(pin, self.GPIO.HIGH)

    def scan_keys(self):
        """Scanner les touches et détecter les pressions et relâchements."""
        for col_index, col_pin in enumerate(self.col_pins):
            # Activer une colonne (LOW) et désactiver les autres (HIGH)
            self.GPIO.output(col_pin, self.GPIO.LOW)
            time.sleep(0.01)  # Pause pour stabilisation

            for row_index, row_pin in enumerate(self.row_pins):
                key = self.keypad[row_index][col_index]
                if not self.GPIO.input(row_pin):  # Si la ligne est activée (LOW)
                    if key not in self.pressed_keys:  # Nouvelle pression
                        self.pressed_keys.add(key)
                        for handler in self._handlers['down']:
                            handler(key)
                else:  # Si la ligne est désactivée (HIGH)
                    if key in self.pressed_keys:  # Clé précédemment pressée
                        self.pressed_keys.remove(key)
                        for handler in self._handlers['up']:
                            handler(key)

            # Désactiver la colonne actuelle
            self.GPIO.output(col_pin, self.GPIO.HIGH)

    def start_polling(self):
        """Démarrer le thread de polling des touches."""
        if not self.polling_thread or not self.polling_thread.is_alive():
            self.polling_thread = Thread(target=self.poll_keys)
            self.polling_thread.start()
            self.running = True

    def poll_keys(self):
        """Boucle de détection des touches."""
        while self.running:
            self.scan_keys()
            time.sleep(0.01)  # Pause entre les scans

    def stop(self):
        """Arrêter le polling et nettoyer les GPIO."""
        print("arrêt")
        self.running = False
        if self.polling_thread:
            self.polling_thread.join()  # Attendre que le thread termine proprement

    def registerKeyPressHandler(self, handler_up, handler_down):
        self._handlers['up'].append(handler_up)
        self._handlers['down'].append(handler_down)

    def unregisterKeyPressHandler(self, handler_up, handler_down):
        self._handlers['up'].remove(handler_up)
        self._handlers['down'].remove(handler_down)

    def clearKeyPressHandlers(self):
        self._handlers = {
            "up" :  [],
            "down" : []
        }

class Pad:
    def __init__(self, api):
        # Associer la fonction de gestion des touches au clavier
        self.__api = api

    def configure(self):
        self.__GPIO = self.__api.getTools_GPIO()
        self.__GPIO.setmode(self.__GPIO.BCM)

    def init_keypad(self, keypad, row_pins, col_pin):
        print("Touches : Initialisation du clavier matriciel : init_keypad")
        self.__keypad = Keypad(self.__GPIO, keypad, row_pins, col_pin)
        self.__keypad.setup()
        self.__keypad.start_polling()

    def registerKeyPressHandler(self, handler_up, handler_down):
        self.__keypad.registerKeyPressHandler(handler_up, handler_down)

    def unregisterKeyPressHandler(self, handler_up, handler_down):
        self.__keypad.unregisterKeyPressHandler(handler_up, handler_down)

    def cleanup(self):
        self.__keypad.stop()
        self.__GPIO.cleanup()

def init(api):
    return Pad(api)