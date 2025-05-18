import RPi.GPIO as GPIO  # bibliothèque pour gérer les GPIO

GPIO.setmode(GPIO.BCM)  # mode de numérotation des pins
GPIO.setup(17,GPIO.IN)  # pin 17 réglée en input

import time
import pygame
pygame.init()
from pygame import mixer 

# Starting the mixer 
mixer.init() 
  
# Loading the song 
# Julie-b35 : Modification apporté par pierrot sur la modification du chemin d'accès au fichier.
#mixer.music.load("attente2.wav") 
mixer.music.load("../ressources/son/acceuil.wav") 
print("ici")  
# Setting the volume 
mixer.music.set_volume(0.7) 
decroche=False
  
# infinite loop 

while True: 

    if(GPIO.input(17)) : 
        
        # Start playing the song 
        if not decroche :
            mixer.music.play() 
            decroche=True
            print("décroché")  

        # print("Press 'p' to pause, 'r' to resume") 
        # print("Press 'e' to exit the program") 
        # query = input("  ") 
      
        # if query == 'p': 
  
        #     # Pausing the music 
        #     mixer.music.pause()      
        # elif query == 'r': 
  
        #     # Resuming the music 
        #     mixer.music.unpause() 
        # elif query == 'e': 
  
        #     # Stop the mixer 
        #     mixer.music.stop() 
        #     break

    else :
        if decroche :
            print("raccroché")
            # Stop the mixer 
            mixer.music.stop() 
            decroche=False

