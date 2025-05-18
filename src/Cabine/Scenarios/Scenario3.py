#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

from Cabine.Scenarios.Scenario import Scenario as BaseScenario
class Scenario3(BaseScenario) :
    pass
def init(api):
    global _
    _ = api._
    return Scenario3(api)