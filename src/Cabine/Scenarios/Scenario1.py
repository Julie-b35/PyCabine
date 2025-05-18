#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("This script is not executable.")

from Cabine.Scenarios.Scenario import Scenario as Scenario1

def init(api):
    return Scenario1(api)