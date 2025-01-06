#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Api import initialiser_projet

SCENARIO = 1

def actualise_locales():
    import subprocess
    directory = "/home/julie/Projects/PyCabine/src/locales/fr_FR/LC_MESSAGES/"
    
    for file in (['tools', 'cabine', 'error']) :
        #  msgfmt -o tools.mo tools.po
        cmd = ['msgfmt', '-o', directory + file + '.mo', directory + file + '.po']

        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print("Erreur détectée :", e)
            print("Code de retour : ", e.returncode)
            print("Sortie erreur", e.stderr)

def main():
    pass

if __name__ == "__main__" :
    print("Hello World")
    exit()
    #print(Utils.baseName.__doc__)
    #print(L("HelloWorld"))
    #exit()
    #TODO Test de la classe Langue, le but est de renvoyer un texte
    try:
        actualise_locales()
        main()
    except Exception:
        print("Fin du programme")
    finally:
        print("Le programme à été arrêté")
