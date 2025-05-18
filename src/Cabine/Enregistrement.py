#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

from enum import Enum





class Enregistrement():    
    # Attribut de classe pour stocker l'unique instance
    _instance = None
    
    TAUX_ECHANTILLONNAGE = 44100
    class ChoicePublication(Enum):
        INTERNET = 1
        PRIVER = 2
    
    class State(Enum):
        READY = 1

    def __new__(self, _, *args, **kwargs):
        # Vérifie si une instance existe déjà
        # merci Chat GPT
        if not self._instance:
            self._instance = super(Enregistrement, self).__new__(self, *args, **kwargs)
            pass
        return self._instance
    def __init__(self, api): # A initialiser qu'une seule fois.
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.__api = api
            self.__utils = None
            self.saveMp3File = None
            self.saveWaveFile = None
            self.saveWaveAmplifiedFile = None
            self.callback = None
    def configure(self):
        self.directoryVocalMsg = self.__api.getTools_Utils().getWorkDir() + "/upload/"

    def pre_run(self) :
        self.__combi = self.__api.GetCls_Combiner()
        self.__utils = self.__api.getTools_Utils()

    def set_callback(self, callback):
        if not callable(callback):
            raise ValueError("La fonction de rappel doit être une fonction.")
        self.callback = callback
    def setFile(self, choice_publication: ChoicePublication = ChoicePublication.INTERNET):
        import datetime
        curent_time = datetime.datetime.now()
        tab_save_file = [
            self.directoryVocalMsg,
            choice_publication.value,
            curent_time.day,
            curent_time.month,
            curent_time.year,
            curent_time.hour,
            curent_time.minute,
            curent_time.second
        ]
        self.saveWaveFile = "%s%s_%s-%s-%s_%s-%s-%s.wav" % tuple(tab_save_file)
        self.saveWaveAmplifiedFile = "%s%s_%s-%s-%s_%s-%s-%s.ampli.wav" % tuple(tab_save_file)
        self.saveMp3File = "%s%s_%s-%s-%s_%s-%s-%s.mp3" % tuple(tab_save_file)

    def __createTmpFileSong(self):
        print("Module Enregistrement : Création Fichier Son (%s)." % self.saveWaveFile)
        import wave
        fileHandler = wave.open(self.saveWaveFile, 'wb')
        fileHandler.setnchannels(1)
        fileHandler.setsampwidth(2)
        fileHandler.setframerate(self.TAUX_ECHANTILLONNAGE)

        return fileHandler

    def __writeSong(self, fh):
        print("Module Enregistrement : Enregistrement en cours.")
        import sounddevice as sd
        from time import sleep
        # Démarrage de l'enregistrement en streaming
        def callback(indata, frames, time, status):
            if status:
                print(f"Statut : {status}")
            #audio.append(indata.copy())
            fh.writeframes(indata.tobytes())
        with sd.InputStream(
            samplerate=self.TAUX_ECHANTILLONNAGE,
            channels=1,
            dtype='int16',
            callback=callback
        ):
            while True:
                sleep(0.1) # en prévention surchage CPU.
                #print(self.__combi)
                if self.callback():
                    break
            #while GPIO.input(HOOK_PIN) == GPIO.HIGH:
            #    time.sleep(0.1)
        
    def __close(self, fh):
        print("Module Enregistrement : Fermeture Fichier Son (%s)." % self.saveWaveFile)
        fh.close()

    def saveVocalMsg(self):
        """
        Point d'entré principale pour l'enregistrement du son
        """
        tmpFileSong = None
        # 1. Création du fichier
        try:
            tmpFileSong = self.__createTmpFileSong()
        except Exception as e:
            print(f"Erreur pendant la création du fichier sonore temporaire qui contiendra l'enregistrement : ")
            raise e
        else:
            self.__writeSong(tmpFileSong)
            self.__close(tmpFileSong)
        
        # 2. Vérification de l'existance du son.
        if not self.__utils.file_exists(self.saveWaveFile):
            raise("La créeation du fichier son (%s) n'a pu être effectué." % self.saveWaveFile)
        #self.amplify_wav(5.0)


    def amplify_wav(self, gain = 2.0):
        import wave
        import numpy as np
        input_file = self.saveWaveFile
        output_file = self.saveWaveAmplifiedFile
        # Charger le fichier .wav
        with wave.open(input_file, 'rb') as wav_in:
            # Récupérer les paramètres du fichier audio
            params = wav_in.getparams()
            num_channels = params.nchannels
            sample_width = params.sampwidth
            frame_rate = params.framerate
            num_frames = params.nframes
            
            # Lire les frames audio
            audio_frames = wav_in.readframes(num_frames)

            # Convertir les frames en données numériques
            dtype = np.int16 if sample_width == 2 else np.int8
            audio_array = np.frombuffer(audio_frames, dtype=dtype)

            # Appliquer le gain pour amplifier le son
            amplified_audio = audio_array * gain
            # Limiter les valeurs pour éviter la saturation
            max_val = np.iinfo(dtype).max
            min_val = np.iinfo(dtype).min
            amplified_audio = np.clip(amplified_audio, min_val, max_val).astype(dtype)

        # Enregistrer le fichier amplifié
        with wave.open(output_file, 'wb') as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(amplified_audio.tobytes())
        print(f"Le fichier amplifié est enregistré sous : {output_file}")
        self.converteWaveToMp3()

    def converteWaveToMp3(self):
        from pydub import AudioSegment
        try:
            audio = AudioSegment.from_wav(self.saveWaveAmplifiedFile)
            audio.export(self.saveMp3File, format='mp3')
        except Exception as e:
            print(f"Erreur pendant la conversion wav --> mp3 : {e}")
        finally:
            #Supprier fichier wave
            print("converteWaveToMp3 : conversion wav --> mp3 effectué avec succès.")
            self.deleteFileWave()
            pass

    def deleteFileWave(self):
        from pathlib import Path
        file_path = Path(self.saveWaveFile)
        try:
            file_path.unlink()
            print(f"Le fichier {self.saveWaveFile} à bien été supprimé.")
        except FileNotFoundError as e: 
            print(f"{self.saveWaveFile} : n'existe pas. : {e}")
        except PermissionError as e:
            print(f"Permission refusée : {self.saveWaveFile} : {e}")
        except Exception as e:
            print(f"Un erreur est survenue : {e}")

        file_path = Path(self.saveWaveAmplifiedFile)
        try:
            file_path.unlink()
            print(f"Le fichier {self.saveWaveAmplifiedFile} à bien été supprimé.")
        except FileNotFoundError as e: 
            print(f"{self.saveWaveAmplifiedFile} : n'existe pas. : {e}")
        except PermissionError as e:
            print(f"Permission refusée : {self.saveWaveAmplifiedFile} : {e}")
        except Exception as e:
            print(f"Un erreur est survenue : {e}")
    
def init(api):
    global _
    _ = api._
    return Enregistrement(api)