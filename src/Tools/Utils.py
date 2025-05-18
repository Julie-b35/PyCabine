#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

from Exceptions.AttributeError import AttributeError

class Utils:
    """
    La classe 'Utils' est une classe utilitaire qui soulage le codeur sur la répétion.

    --> __new__() création de l'instance
    --> __init__() Initialisation de l'instance
    --> clean() Nettoie les objets des classes crée : Voir la méthode "clean" de chaque classes.

        ---------------------------- Liste Méthodes Static gérent les nom de chemins -----------------------
        
    -->  getWorkDir() : Renvoie le répertoire de travail du projet, déclenche une Exception de type 'AttributeError'
                        si initWorkdir n'a pas été appelé.
    """
    # Attribut de classe pour stocker l'unique instance
    _instance = None


    """
    =====================================================================================================================
    ====                                                                                                             ====
    ====                           Fonction D'initialisation du projet                                               ====
    ====              Elle sont appellé une seule fois dans le programme (@see src/Tools/__init__.py)                ====
    ====                                                                                                             ====
    =====================================================================================================================
    """


    """
    Méthode qui permet de crée l'instance, cette instance sera unique.
    """
    def __new__(cls, _, *args, **kwargs):
        # Vérifie si une instance existe déjà
        if not cls._instance:
            cls._instance = super(Utils, cls).__new__(cls, *args, **kwargs)
           # print("Nouvelle instance de Factory créée.")
        else:
            #print("Instance existante de Factory utilisée.")
            pass
        return cls._instance

    """
    Méthode pour initialiser l'instance, celle-ci sera unique.
    La classe est appelé et initialisé depuis "src/Tools/__init__.py"
    """
    def __init__(self, api, *args, **kwargs):
        # Init ne s'exécute qu'une seule fois si nécessaire
        if not hasattr(self, "_initialized"):
            self._initialized = True
            super().__init__(*args, **kwargs)
            # J'ai juste besoin du module PATH
            import os as _os
            self.__os = _os
            self.__path = _os.path
            self.__api = api
            self.WorkDir = self._initWorkDir()
            
    def configure(self):
        global _
        _ = self.__api._

    def _initWorkDir(self):
        """
            Méthode privée afin de définire le répertoire principale de travail du Projet PyCabine.
            Pour cela cette méthode doit être lancée au scripte principal et évité tout problème
        """
        return self.__path.realpath(self.__path.dirname(__file__) + "/../..")

    """
    =====================================================================================================================
    ====                                                                                                             ====
    ====                                        Fonction public (Api)                                                ====
    ====                                                                                                             ====
    =====================================================================================================================
    """

    @staticmethod
    def GetCallingModule(throw : bool = False):
        """
        GetCallingModule Méthode statique
        Renvoie le nom du module précédent qui à appelé cette méthode à travers un autre module

        Exemple : La méthode 'lancement' du module 'Cabine.Scenarios.Scenario1',
            appelle la méthode '_' du module 'Api', qui appelle à son tour,
            la méthode d'ici (GetCallingModule)
        """
        import inspect
        #récupération de la frame actuel
        frame = inspect.currentframe()
        #Je récupère la frame appellante qui à appellée cette méthode depuis une méthode précédente.
        caller_frame = frame.f_back.f_back
        #Je récupère le module appelant
        caller_module = inspect.getmodule(caller_frame)
        #puis je renvoie son nom
        return caller_module.__name__ if caller_module else None

    @staticmethod
    def GetFirstNameModule(name_module: None | str):
        if not name_module : return None
        list_names_modules = name_module.split('.')
        return list_names_modules[0]

    def getFactory(self):
        if hasattr(self,'factory'):
            return self.factory
        
        raise Exception(_("The Factory class was not properly initialized"))

    """
    Cette méthode permet de nettoyer les classes, valeur.
    lèbère les ressources
    """
    def Clean(self) -> None :
        #boucle la liste des classes qui doit être nettoyé.
        for _cls in self._list_cls_to_clean :
            #Récupération de l'objet qui à été initialisé plus haut
            _o_cls = getattr(self, _cls)
            # Je m'assure que la méthode "clean" existe dans la liste des classes à nettoyé.
            if hasattr(_o_cls, "clean") :
                #Je récupère la méthode clean, puis je l'appelle.
                getattr(_o_cls, "clean")()

    """
    =====================================================================================================================
    ====                                                                                                             ====
    ====                   Définition de Méthode  utilitaire pour la gestion des noms de chemins.                    ====
    ====                                                                                                             ====
    =====================================================================================================================
    """

    def getWorkDir(self) -> str:
        """
            Récupère le répertoire de travail du projet
        Raises:
            AttributeError: initWorkdir n'a pas été appelé, un déclenchement d'erreur s'impose pour éviter des bug ultérieur

        Returns:
            str: Renvoie Utils.WorkDir définis dans la méthode statiqued initWorkdir()
        """
        if not hasattr(self, "WorkDir") :
            raise AttributeError(self.__api, "Utils.WorkDir", _("Did you call the static 'Utils.setWorkDir()' method?")) 
        return self.WorkDir
    
    
    def baseName(self, file: str, without_ext: bool | None = ...) -> str:
        basename = self.path.basename(file)

        if without_ext == True:
            basename = basename.split('.')[0]
            print(basename)
            print(without_ext)
        return basename

    def def_tmpFile_gpio(self):
        import glob
        # Chemin avec motif
        motif = "/tmp/.lgd-nfy*"

        # Trouver les fichiers correspondant au motif
        fichiers = glob.glob(motif)
        for fichier in fichiers:
            self.del_file(fichier)
            
    def file_exists(self, file):
        return self.__path.isfile(file)
    
    def copy_file(self, source, target):
        import shutil
        shutil.copy2(source, target)
    def del_file(self, file):

        fichier_a_supprimer = file

        try:
            self.__os.remove(fichier_a_supprimer)
            print(f"Le fichier '{fichier_a_supprimer}' a été supprimé avec succès.")
        except FileNotFoundError:
            print(f"Le fichier '{fichier_a_supprimer}' n'existe pas.")
        except PermissionError:
            print(f"Vous n'avez pas la permission de supprimer '{fichier_a_supprimer}'.")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def call_process(self, command: str):
        """
        Méthode pour exécuter une commande système.
        """
        import subprocess
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8')
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")
            return None
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            return None

    def set_environment(self, name: str, value: str):
        """
        Méthode pour définir une variable d'environnement.
        """
        if value is None or value == "":
            raise AttributeError(self.__api, "Utils.set_env", _("The value of the environment variable cannot be None or empty."))
        
        if not isinstance(name, str):
            raise AttributeError(self.__api, "Utils.set_env", _("The name of the environment variable must be a string."))
        if not isinstance(value, str):
            raise AttributeError(self.__api, "Utils.set_env", _("The value of the environment variable must be a string."))
        # Vérifie si la variable d'environnement existe déjà
        if name in self.__os.environ:
            # Si elle existes, on affiche un message d'avertissement
            print(f"Avertissement : La variable d'environnement '{name}' existe déjà et sera remplacée.")
        # Définit la variable d'environnement
        self.__os.environ[name] = value
"""
=====================================================================================================================
====                                                                                                             ====
====                                  Fin de la classe 'Utils'                                                   ====
====                                                                                                             ====
=====================================================================================================================
"""


def init(api):
    return Utils(api)
