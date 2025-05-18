import alsaaudio
import wave

print("Initialisation...")
inp = alsaaudio.PCM(
    type=alsaaudio.PCM_CAPTURE,
    mode=alsaaudio.PCM_NORMAL,
    device='plughw:0',
    channels=1,
    rate=48000,
    format=alsaaudio.PCM_FORMAT_S32_LE,
    periodsize=160
)

with wave.open("test.wav", 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(4)
    wf.setframerate(48000)

    print("Enregistrement...")
    for i in range(300):  # ~5 secondes
        l, data = inp.read()
        if l:
            wf.writeframes(data)

inp.close()
print("Fichier généré : test.wav")
