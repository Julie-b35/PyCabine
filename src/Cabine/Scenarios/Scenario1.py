#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("This script is not executable.")

from time import sleep

from enum import Enum
class State(Enum):
    RACCROCHER=1
    DECROCHER=2
    CHOICE_PUBLICATION_OK=3
del Enum

#Condition afin de savoir quel touches du clavier matriciel sont accepter.
CHOICE_PUBLICATION_ACCEPTED = [1, 2]

class Scenario1() :
    # Attribut de classe pour stocker l'unique instance
    _instance = None

    def __new__(self, _, *args, **kwargs):
        # Vérifie si une instance existe déjà
        # merci Chat GPT
        if not self._instance:
            self._instance = super(Scenario1, self).__new__(self, *args, **kwargs)
            pass
        return self._instance
    
    def __init__(self, api):
         # A initialiser qu'une seule fois.
         if not hasattr(self, "_initialized"):
            self._initialized = True
            self.__api = api
            self.choice_publication = None
            self.state = State.RACCROCHER
            
    def configure(self):
        self.__combi = self.__api.GetCls_Combiner()
        self.__son = self.__api.GetCls_Son()
        self.__touches = self.__api.GetCls_Touches()
        self.__enregistrement = self.__api.GetCls_Enregistrement()
        #print(self) 

    def exec(self):
        if self.state == State.RACCROCHER :
            #Condition si le téléphone n'est pas décrocher, alors j'envoie l'annonce d'acceuil
            if not self.attenteDecrochage() :
                #raise Exception("Erreur inconnue : Je n'ai pas reçue l'état du téléphone\nIl est censé renvoyé toujours True")
                return False
        elif self.state == State.DECROCHER :
            self.__touches.load()
            # Le téléphone est décrocher.

            #Envoie de l'annonce de bienvenue
            # Dans ce scénarion j'envoie un son de bienvenue 
            # avec la demande pour choisir le type de publication
            # TODO : J'ai mis une pause, a terme modifier la bande son
            sleep(2)
            self.sendWelcomeAnnounceAndChoicePublication()
        elif self.state == State.CHOICE_PUBLICATION_OK:
            self.__touches.wait_is_button_pressed()
            self.__touches.unload()
            self.__enregistrement.setFile(self.choice_publication)
            self.__son.play(self.__son.ANNONCE_ENREGISTREMENT)
            self.__son.wait()
            self.__enregistrement.saveVocalMsg()

            # Le choix de publication à été fait, on peut poursuivre.
            if self.choice_publication == 1 :
                print("La publication sur internet est choisie")
                # TODO : Je lance l'enregistrement sur internet.
                self.__api.getTools_Utils().call_process("/usr/bin/cabine_upload")
            elif self.choice_publication == 2 :
                print("Mode secret activé.")


            # A des fin de test.
            # laisse à laps de temps pour raccrocher.
            print("Pause maximal 5 seconde, cela devrais laisser le temps de raccrocher.")
            secondes = 0
            while secondes <= 5:
                sleep(1)
                secondes +=1
                if self.__combi.combiRaccrocher():
                    break
            self.state = State.RACCROCHER
            
        if self.state == State.RACCROCHER :
            # Fin du scénario
            #Déchargement des touches du clavier
            self.__touches.unload()
            self.state = State.RACCROCHER
            self.choice_publication = None
        
    def getVocalMessage(self):
        pass
    def sendWelcomeAnnounceAndChoicePublication(self):
            # Lancement du message de bienvenue.
            # TODO : J'envoie l'annonce de bienvenue.
            self.__son.play(self.__son.WELCOME_AND_CHOICE_PUBLICATION)

            while not self.choice_publication:
                sleep(0.1)

                #Si 1 ou 2 à été appuyer alor
                # s'assurer que le son est arrêté
                # puis définir le choix de publication
                # traiter les erreurs si mauvaise touche appuyer, puis recommencer.
                touche = self.__touches.getSelectedKey()
                if self.__combi.combiRaccrocher():
                    # Cas 1 : Le téléphone est raccrocher.
                    self.__son.stop()
                    self.state = State.RACCROCHER #On reprend à 0
                    print("Choix publication : Téléphone raccrocher.")
                    break
                elif not self.__son.get_busy() and not self.__touches.getButtonPressed():
                    # Le son est finis alors je lance à nouveau la demande pour faire un choix
                    print("Choix publication : Le délai est dépassé.")
                    self.__touches.wait_is_button_pressed()
                    self.__son.play(self.__son.ERROR_UNKNOW_CHOICE_PUBLICATION)
                elif touche in CHOICE_PUBLICATION_ACCEPTED :
                    self.__touches.wait_is_button_pressed()
                    self.choice_publication = self.__enregistrement.ChoicePublication(touche)
                    self.__son.stop()
                    self.state = State.CHOICE_PUBLICATION_OK
                    print("Choix publication : un choix à été fait.")
                elif touche != None and not touche in CHOICE_PUBLICATION_ACCEPTED :
                    self.__touches.wait_is_button_pressed()
                    # Mauvais choix, je lance à nouveau la demande.
                    print("Choix publication : Mauvais Choix.")
                    self.__son.play(self.__son.ERROR_CHOICE_PUBLICATION)
        # Fin de méthode : sendWelcomeAnnounceAndChoicePublication

    # TODO Si le téléphone est décrocher le programme boucle jusqu'à ce qu'il sois raccrocher
    def attenteDecrochage(self, _sleep : int|None= None):
        if (self.__combi.combiDeccrocher()) : 
            print(_("The phone is already off the hook, waiting for him to hang up."))
            # Une pause demander avant de relancer l'annonce
            #  (uniquement dans le cas où la fonction est rappeler dans la condition.)
            if _sleep :
                sleep(_sleep)
            # Lance une annonce vocale (téléphone décrocher)
            self.__son.play(self.__son.DEMANDE_RACCROCHER)
            #On attend la fin de la lectue ou que la personne raccroche.
            self.__son.wait()

            #Le téléphone est toujours décrocher, on retourne dans la même fonction avec une pause de 2 secondes
            self.attenteDecrochage(2)
        
        print("En service, le programme attend qu'une personne décroche.")
        # Boucle while jusq'à ce que le combinée soit décrocher
        while True: #Point de départ du programme en temps normal.
            sleep(0.1)# économie du temps CPU
            combinee_decrocher = self.__combi.getStateCombi()
            if combinee_decrocher == True :
                print("Téléphone décrocher : Retour au scénario.")
                self.state = State.DECROCHER
                return combinee_decrocher

def lancement_bis(api, module):
    scenar = module.Scenario1()
    scenar.exec()

def init(api):
    global _
    _ = api._
    return Scenario1(api)