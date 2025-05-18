import sounddevice as sd
import wave
import RPi.GPIO as GPIO
import time

"""
Fichier Reçu par pierrot le 30/11/2024 à commité.
"""
HOOK_PIN = 17  # GPIO connecté au combiné
DUREE_MAX_ENREGISTREMENT = 60  # Temps maximum d'enregistrement (en secondes)
TAUX_ECHANTILLONNAGE = 44100

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # pin 17 réglée en input

def enregistrer_audio(fichier_sortie):
    print("Enregistrement en cours...")
    audio = []
    try:
        with wave.open(fichier_sortie, 'wb') as fichier_wave:
            fichier_wave.setnchannels(1)
            fichier_wave.setsampwidth(2)
            fichier_wave.setframerate(TAUX_ECHANTILLONNAGE)
            # Démarrage de l'enregistrement en streaming
            def callback(indata, frames, time, status):
                if status:
                    print(f"Statut : {status}")
                audio.append(indata.copy())
                fichier_wave.writeframes(indata.tobytes())

            with sd.InputStream(
                samplerate=TAUX_ECHANTILLONNAGE,
                channels=0,
                dtype='int16',
                callback=callback
            ):
                while GPIO.input(HOOK_PIN) == GPIO.DOWN:
                    time.sleep(0.1)
        print(f"Enregistrement terminé. Fichier enregistré sous {fichier_sortie}")
    except Exception as e:
        print(f"Erreur pendant l'enregistrement : {e}")

try:
    print("Attente que le combiné soit décroché...")
    while True:
        if GPIO.input(HOOK_PIN) == GPIO.DOWN:
            print("Combiné décroché. Lancement de l'enregistrement.")
            enregistrer_audio("combiné.wav")
            print("Combiné raccroché. Enregistrement arrêté.")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Interruption clavier détectée. Fin du programme.")
finally:
    GPIO.cleanup()
