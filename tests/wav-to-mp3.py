import os
import wave
import numpy as np
from pathlib import Path
from pydub import AudioSegment

# === Configuration ===
UPLOAD_DIR = Path("/home/rpi/PyCabine/upload/")  # ← à adapter
RMS_SEUIL = 100000  # seuil minimum pour considérer qu'il y a une voix

# === Fonctions utilitaires ===
def analyse_volume(file_path: Path) -> float:
    try:
        with wave.open(str(file_path), 'rb') as wf:  # ← forcé en str
            sampwidth = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
        dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sampwidth)
        if not dtype:
            raise ValueError(f"Échantillon inconnu : {sampwidth} octets")
        audio_array = np.frombuffer(frames, dtype=dtype)
        rms = np.sqrt(np.mean(audio_array.astype(np.float64) ** 2))
        return rms
    except Exception as e:
        print(f"  ⚠️ Erreur analyse volume {file_path.name} : {e}")
        return -1


def convertir_wav_en_mp3(file_path: Path):
    try:
        audio = AudioSegment.from_wav(file_path)
        mp3_path = file_path.with_suffix('.mp3')
        audio.export(mp3_path, format="mp3")
        print(f"  ✅ Converti en MP3 : {mp3_path.name}")
    except Exception as e:
        print(f"  ❌ Erreur conversion {file_path.name} : {e}")

def supprimer_fichier(file_path: Path):
    try:
        file_path.unlink()
        print(f"  🗑️ Supprimé : {file_path.name}")
    except Exception as e:
        print(f"  ⚠️ Erreur suppression {file_path.name} : {e}")

# === Fonction principale ===
def traiter_tous_les_wav(directory: Path):
    if not directory.exists():
        print(f"Dossier introuvable : {directory}")
        return

    # Inclut tous les fichiers .wav (classiques et .ampli.wav)
    wav_files = list(directory.glob("*.wav")) + list(directory.glob("*.ampli.wav"))
    wav_files = list(set(wav_files))  # enlever les doublons si jamais

    if not wav_files:
        print("Aucun fichier WAV trouvé.")
        return

    for wav_file in wav_files:
        print(f"\n🔍 Analyse de {wav_file.name}...")
        rms = analyse_volume(wav_file)
        print(f"    ➤ RMS : {int(rms)}")

        if rms >= RMS_SEUIL:
            convertir_wav_en_mp3(wav_file)
        else:
            print("    ⛔ Pas de voix détectée (volume trop bas).")

        supprimer_fichier(wav_file)

    print("\n✅ Traitement terminé pour tous les fichiers.")

if __name__ == "__main__":
    traiter_tous_les_wav(UPLOAD_DIR)
