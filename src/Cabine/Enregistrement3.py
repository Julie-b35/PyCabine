
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

from enum import Enum
import sounddevice as sd

class Enregistrement():    
    _instance = None
    Int16 = 2
    Int32 = 4
    TAUX_ECHANTILLONNAGE = 48000

    class ChoicePublication(Enum):
        INTERNET = 1
        PRIVER = 2

    def __new__(cls, _, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Enregistrement, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, api):
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
       # self.device = self.__getDevice("snd_rpi", kind="input")
        #self.format_song = self.Int32
        #if self.device is None:
        #    raise Exception("Aucun périphérique d'enregistrement trouvé.")
        self.directoryVocalMsg = self.__api.getTools_Utils().getWorkDir() + "/upload/"
        pass

    def pre_run(self):
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
        print("saveVocalMsg : Enregistrement en cours (via pyalsaaudio).")
        print(self.saveWaveFile)

        import alsaaudio
        import wave
        from time import sleep

        try:
            inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device='plughw:0',
                                channels=1, rate=self.TAUX_ECHANTILLONNAGE,
                                format=alsaaudio.PCM_FORMAT_S32_LE,
                                periodsize=160)

            underrun_count = 0

            with wave.open(self.saveWaveFile, 'wb') as fichier_wave:
                fichier_wave.setnchannels(1)
                fichier_wave.setsampwidth(4)
                fichier_wave.setframerate(self.TAUX_ECHANTILLONNAGE)

                while True:
                    try:
                        length, data = inp.read()
                        if length < 0:
                            print(f"Erreur ALSA : underrun (code {length})")
                            underrun_count += 1
                            if underrun_count > 3:
                                print("Trop d’erreurs, abandon.")
                                break
                            continue
                        underrun_count = 0  # reset

                    except Exception as e:
                        print(f"Erreur lecture micro : {e}")
                        break

                    print(f"Lecture : {length} frames")
                    print(f"Data : {len(data)} octets")
                    if length:
                        print(f"Reçu {length} frames")
                        fichier_wave.writeframes(data)
                    else:
                        print("Aucune donnée captée.")

                    if self.__combi.combiRaccrocher():
                        break

                   # sleep(0.001)  # plus court pour éviter underrun

            inp.close()
            print(f"Enregistrement terminé. Fichier enregistré sous {self.saveWaveFile}")

        except Exception as e:
            print(f"Erreur pendant l'enregistrement : {e}")
        finally:
            print("saveVocalMsg : Fin de l'enregistrement.")

    def amplify_wav(self, gain = 2.0):
        import wave
        import numpy as np
        input_file = self.saveWaveFile
        output_file = self.saveWaveAmplifiedFile
        with wave.open(input_file, 'rb') as wav_in:
            params = wav_in.getparams()
            sample_width = params.sampwidth
            audio_frames = wav_in.readframes(params.nframes)
            if sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                raise ValueError(f"Format échantillon inconnu : {sample_width}")
            audio_array = np.frombuffer(audio_frames, dtype=dtype)
            amplified_audio = audio_array * gain
            amplified_audio = np.clip(amplified_audio, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)

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
            print("converteWaveToMp3 : conversion wav --> mp3 effectué avec succès.")
            self.deleteFileWave()

    def deleteFileWave(self):
        from pathlib import Path
        for path in [self.saveWaveFile, self.saveWaveAmplifiedFile]:
            try:
                Path(path).unlink()
                print(f"Le fichier {path} à bien été supprimé.")
            except Exception as e:
                print(f"Erreur suppression {path} : {e}")

def init(api):
    global _
    _ = api._
    return Enregistrement(api)
