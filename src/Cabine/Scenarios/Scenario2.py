#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

from Cabine.Scenarios.Scenario import Scenario as BaseScenario
from time import sleep
class Scenario2(BaseScenario) :

    def callback_end_save_voice(self):
        touche = self._touches.getSelectedKey()
        diese_pressed = False
        if touche == "#":
            diese_pressed = True
        return self._combi.combiRaccrocher() or diese_pressed

def init(api):
    return Scenario2(api)