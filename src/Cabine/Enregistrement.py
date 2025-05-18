#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

from enum import Enum

import sounddevice as sd




class Enregistrement():    
    # Attribut de classe pour stocker l'unique instance
    _instance = None
    
    Int16 = 2
    Int32 = 4
    TAUX_ECHANTILLONNAGE = 48000
    class ChoicePublication(Enum):
        INTERNET = 1
        PRIVER = 2
    
    def __new__(cls, _, *args, **kwargs):
        # Vérifie si une instance existe déjà
        # merci Chat GPT
        if not cls._instance:
            cls._instance = super(Enregistrement, cls).__new__(cls, *args, **kwargs)
            pass
        return cls._instance
    def __init__(self, api): # A initialiser qu'une seule fois.
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.__api = api
            self.saveMp3File = None
            self.saveWaveFile = None
            self.saveWaveAmplifiedFile = None
            self.device = None
    def __getDevice(self, name, kind="input"):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if name.lower() in dev['name'].lower():
                if (kind == 'input' and dev['max_input_channels'] > 0) or \
                (kind == 'output' and dev['max_output_channels'] > 0):
                    return i
        return None

    def configure(self):
        self.device = self.__getDevice("snd_rpi", kind="input")
        self.format_song = self.Int32
        if self.device is None:
            raise Exception("Aucun périphérique d'enregistrement trouvé.")
        self.directoryVocalMsg = self.__api.getTools_Utils().getWorkDir() + "/upload/"

    def pre_run(self) :
        self.__combi = self.__api.GetCls_Combiner()

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

    def saveVocalMsg(self):
        print("saveVocalMsg : Enregistrement en cours.")
        print (self.saveWaveFile)
        import wave
        from time import sleep
        try:
            with wave.open(self.saveWaveFile, 'wb') as fichier_wave:
                fichier_wave.setnchannels(1)
                fichier_wave.setsampwidth(4)
                fichier_wave.setframerate(self.TAUX_ECHANTILLONNAGE)
                # Démarrage de l'enregistrement en streaming
                def callback(indata, frames, time, status):
                    if status:
                        print(f"Statut : {status}")
                    #audio.append(indata.copy())
                    fichier_wave.writeframes(indata.tobytes())
                #print(self.__combi)
                with sd.InputStream(
                    device=self.device,
                    samplerate=self.TAUX_ECHANTILLONNAGE,
                    channels=1,
                    dtype='int32',
                    callback=callback
                ):
                    while True:
                        sleep(0.1) # en prévention surchage CPU.
                        #print(self.__combi)
                        if self.__combi.combiRaccrocher():
                            break
                    #while GPIO.input(HOOK_PIN) == GPIO.HIGH:
                    #    time.sleep(0.1)
            print(f"Enregistrement terminé. Fichier enregistré sous {self.saveWaveFile}")
        except Exception as e:
            print(f"Erreur pendant l'enregistrement : {e}")
        finally:
            print("saveVocalMsg : Fin de l'enregistrement.")
            self.amplify_if_needed()
            self.converteWaveToMp3()


    def analyse_volume(self, file_path):
        import wave
        import numpy as np
        with wave.open(file_path, 'rb') as wf:
            sampwidth = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
        dtype = {1: np.int8, 2: np.int16, 4: np.int32}[sampwidth]
        audio_array = np.frombuffer(frames, dtype=dtype)
        rms = np.sqrt(np.mean(audio_array.astype(np.float64)**2))
        return rms

    def amplify_if_needed(self):
        rms = self.analyse_volume(self.saveWaveFile)
        print(f"Volume RMS mesuré : {rms}")
        if rms < 100000:  # seuil à ajuster selon tests
            print("Volume trop bas, amplification x5...")
            self.amplify_wav(5.0)
        else:
            print("Volume correct, pas d'amplification.")
            self.saveWaveAmplifiedFile = self.saveWaveFile  # copie logique
            
    def amplify_wav(self, gain = 2.0):
        raise NotImplementedError("La méthode amplify_wav n'est pas encore implémentée.")
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
            if sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                raise ValueError(f"Format échantillon inconnu : {sample_width}")
            # Convertir les frames en données numériques
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
        #self.converteWaveToMp3()

    def converteWaveToMp3(self):
        from pydub import AudioSegment
        try:
            audio = AudioSegment.from_wav(self.saveWaveAmplifiedFile)
            audio = audio.set_sample_width(2)  # passe à 16-bit
            print(audio.frame_rate, audio.channels, audio.sample_width)
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

        if self.saveWaveAmplifiedFile != self.saveWaveFile:
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