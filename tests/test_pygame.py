import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Peut être utilisé pour forcer un test ou diagnostic
os.environ['SDL_LOG_PRIORITY'] = 'debug'
import pygame
pygame.init()

# Récupérer et afficher le pilote SDL utilisé
sdl_audio_driver = pygame.mixer.get_init()
# Liste les pilotes SDL
drivers = pygame.get_sdl_audio_drivers()
print(f"Pilote audio SDL utilisé : {drivers}")