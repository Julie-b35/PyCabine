#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("This script is not executable.")

from time import sleep

from enum import Enum
class State(Enum):
    RACCROCHER='state_raccrocher'
    DECROCHER='state_decrocher'
    CHOICE_PUBLICATION_OK='state_publication_ok'
del Enum

#Condition afin de savoir quel touches du clavier matriciel sont accepter.
CHOICE_PUBLICATION_ACCEPTED = [1, 2]

class Scenario:

    """
    Fonction Init Chargée à l'appel de cette classe depuis La fonction issue de la classe API:
    api->__init()
    """
    def __init__(self, api):
         # A initialiser qu'une seule fois.
         if not hasattr(self, "_initialized"):
            self._initialized = True
            self._api = api
            self.__choice_publication = None
            self.Enum_State = State
            self.__state = self.Enum_State.RACCROCHER
            self._api.allow_use_gettext('cabine', 'Cabine.Scenarios.Scenario')
            self.L = None

    def callback_end_save_voice(self):
        return self._combi.combiRaccrocher()
    
    def getState(self):
        return self.__state

    def getState_Raccrocher(self):
        return self.__state == self.Enum_State.RACCROCHER
    
    def getState_Decrocher(self):
        return self.__state == self.Enum_State.DECROCHER
    
    def getState_ChoixPublication(self):
        return self.__state == self.Enum_State.CHOICE_PUBLICATION_OK
    
    def setState_Raccrocher(self):
        self.__state = self.Enum_State.RACCROCHER

    def setState_Decrocher(self):
        self.__state = self.Enum_State.DECROCHER

    def setState_ChoixPublication(self):
        self.__state = self.Enum_State.CHOICE_PUBLICATION_OK

    def get_ChoicePublication(self):
        return self.__choice_publication
    
    def set_ChoicePublication(self, value):
        self.__choice_publication = value
    def set_ChoicePublication_internet(self):
        self.__choice_publication = 1

    def set_ChoicePublication_private(self):
        self.__choice_publication = 2
    
    def del_ChoicePublication(self):
        self.__choice_publication = None

    def configure(self):
        self._combi = self._api.GetCls_Combiner()
        self._son = self._api.GetCls_Son()
        self._touches = self._api.GetCls_Touches()
        self._enregistrement = self._api.GetCls_Enregistrement()
        self.L = self._api._

    def pre_run(self):
        self._enregistrement.set_callback(self.callback_end_save_voice)
        
    def state_raccrocher(self):
        #Condition si le téléphone n'est pas décrocher, alors j'envoie l'annonce d'acceuil
        if not self.attenteDecrochage() :
            #raise Exception("Erreur inconnue : Je n'ai pas reçue l'état du téléphone\nIl est censé renvoyé toujours True")
            return False
        
    def state_decrocher(self):
        self._touches.load()
        # Le téléphone est décrocher.

        #Envoie de l'annonce de bienvenue
        # Dans ce scénarion j'envoie un son de bienvenue 
        # avec la demande pour choisir le type de publication
        # TODO : J'ai mis une pause, a terme modifier la bande son
        sleep(2)
        self.sendWelcomeAnnounceAndChoicePublication()

    def _run_enregistrement(self):
        self._enregistrement.set_callback(self.callback_end_save_voice)
        self._enregistrement.saveVocalMsg()

    def state_publication_ok(self):
        self._touches.wait_is_button_pressed()
        self._touches.unload()
        self._enregistrement.setFile(self.get_ChoicePublication())
        self._son.play(self._son.ANNONCE_ENREGISTREMENT)
        self._son.wait()
        self._touches.load()
        self._run_enregistrement()

        # Le choix de publication à été fait, on peut poursuivre.
        if self.get_ChoicePublication() == 1 :
            print("La publication sur internet est choisie")
        elif self.get_ChoicePublication() == 2 :
            print("Mode secret activé.")


        # A des fin de test.
        # laisse à laps de temps pour raccrocher.
        print("Pause maximal 5 seconde, cela devrais laisser le temps de raccrocher.")
        secondes = 0
        while secondes <= 5:
            sleep(1)
            secondes +=1
            if self._combi.combiRaccrocher():
                break
        self.setState_Raccrocher()

    def exec(self):
        #print(self.__class__)
        methode_state = getattr(self, self.__state.value)
        methode_state()

        self.cleanup()
    # TODO Si le téléphone est décrocher le programme boucle jusqu'à ce qu'il sois raccrocher
    def attenteDecrochage(self, _sleep : int|None= None):
        if (self._combi.combiDeccrocher()) : 
            print(self.L("The phone is already off the hook, waiting for him to hang up."))
            # Une pause demander avant de relancer l'annonce
            #  (uniquement dans le cas où la fonction est rappeler dans la condition.)
            if _sleep :
                sleep(_sleep)
            # Lance une annonce vocale (téléphone décrocher)
            self._son.play(self._son.DEMANDE_RACCROCHER)
            #On attend la fin de la lectue ou que la personne raccroche.
            self._son.wait()

            #Le téléphone est toujours décrocher, on retourne dans la même fonction avec une pause de 2 secondes
            self.attenteDecrochage(2)
        
        print("En service, le programme attend qu'une personne décroche.")
        # Boucle while jusq'à ce que le combinée soit décrocher
        while True: #Point de départ du programme en temps normal.
            sleep(0.1)# économie du temps CPU
            combinee_decrocher = self._combi.getStateCombi()
            if combinee_decrocher == True :
                print("Téléphone décrocher : Retour au scénario.")
                self.__state = self.Enum_State.DECROCHER
                return combinee_decrocher
            

    def sendWelcomeAnnounceAndChoicePublication(self):
            # Lancement du message de bienvenue.
            # TODO : J'envoie l'annonce de bienvenue.
            self._son.play(self._son.WELCOME_AND_CHOICE_PUBLICATION)

            while not self.get_ChoicePublication():
                sleep(0.1)

                #Si 1 ou 2 à été appuyer alor
                # s'assurer que le son est arrêté
                # puis définir le choix de publication
                # traiter les erreurs si mauvaise touche appuyer, puis recommencer.
                touche = self._touches.getSelectedKey()
                if self._combi.combiRaccrocher():
                    # Cas 1 : Le téléphone est raccrocher.
                    self._son.stop()
                    self.setState_Raccrocher()
                    print("Choix publication : Téléphone raccrocher.")
                    break
                elif not self._son.get_busy() and not self._touches.getButtonPressed():
                    # Le son est finis alors je lance à nouveau la demande pour faire un choix
                    print("Choix publication : Le délai est dépassé.")
                    self._touches.wait_is_button_pressed()
                    self._son.play(self._son.ERROR_UNKNOW_CHOICE_PUBLICATION)
                elif touche in CHOICE_PUBLICATION_ACCEPTED :
                    self._touches.wait_is_button_pressed()
                    self.set_ChoicePublication(self._enregistrement.ChoicePublication(touche))
                    self._son.stop()
                    self.setState_ChoixPublication()
                    print("Choix publication : un choix à été fait.")
                elif touche != None and not touche in CHOICE_PUBLICATION_ACCEPTED :
                    self._touches.wait_is_button_pressed()
                    # Mauvais choix, je lance à nouveau la demande.
                    print("Choix publication : Mauvais Choix.")
                    self._son.play(self._son.ERROR_CHOICE_PUBLICATION)
        # Fin de méthode : sendWelcomeAnnounceAndChoicePublication

    def cleanup(self):
        if  self.getState_Raccrocher():
            # Fin du scénario
            #Déchargement des touches du clavier
            self._touches.unload()
            self.setState_Raccrocher()
            self.del_ChoicePublication()