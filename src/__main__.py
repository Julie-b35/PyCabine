#!/usr/bin/env python
# -*- coding: utf-8 -*-

def actualise_locales():
    import subprocess
    import os
    directory =  os.path.realpath(os.path.dirname(__file__) + "/..") + "/src/locales/fr_FR/LC_MESSAGES/"
   
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
    #exit()

def main():
    print("Lancement de l'application...")
    from Api import initialiser_projet
    app = initialiser_projet()
    app.Run()
    
if __name__ == "__main__" :
    try:
        actualise_locales()
        main()
    except Exception as e:
        print("Une erreur est survenue : ")
        raise e

    except KeyboardInterrupt:
        print("Arrêt du programme demandé.")
    finally:
        print("Fin du programme.")
