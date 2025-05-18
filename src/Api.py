#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

"""
Ce fichier agit comme un chef d’orchestre pour coordonner les modules principaux (À savoir Tools et Cabine) tout en évitant les 
importations cycliques et en centralisant les interactions inter-modules. L'objectif est de maintenir une 
structure claire, modulaire et facile à maintenir.
"""

from Tools import Gettext
from settings import MODULES, EXCEPTIONS # Import de configuration externe

class Api:
    """
    Classe de gestion principale reliant les outils (Tools) et les modules du projet principal (Cabine).
    
    Responsabilités :
        - Centraliser les interactions entre les modules.
        - Gérer les initialisations et la configuration.
        - Agir comme interface pour les appels extérieurs (API).
    """

    #Gestion des domaines pour gettext
    __list_allowed_modules_for_gettext = {}

    __tools_initialized = False

    __running = True

    def __init__(self):
        """
        Initialisation de tous les modules utilisés dans le projet.
        """
        # Initialisation de gettext
        import os
        self.__gettext = Gettext.init()
        for domain in ['cabine', 'tools', 'error']:
            self.__gettext.InitGettext(domain)

        # Autoriser les classes d'exception à utiliser gettext
        self.__allow_exceptions_use_gettext()
        
        # Charger les modules principaux et leurs éléments
        self.__tools = self.__import_all_modules(MODULES["tools"])
        self.__tools_initialized = True
        self.__mods_projects = self.__import_all_modules(MODULES["projects"])
        self.__scenarios = list(self.__import_all_modules(MODULES["scenarios"]).values())

        # Regrouper toutes les classes initialisées
        self.__list_cls_initialized = [
            self.__gettext, *self.__tools.values(),
            *self.__mods_projects.values(),
            *self.__scenarios,
        ]

    def __import_dynamic(self, module_name):
        """
        Importe dynamiquement un module à partir de son nom sous forme de chaîne.
        
        Args:
            module_name (str): Nom complet du module (e.g., 'Cabine.Scenarios.Scenario1').
        
        Returns:
            Module: Une référence au module importé.
        """
        try:
            components = module_name.split('.')
            domain = components[0].lower()
            module = __import__('.'.join(components[:-1]), fromlist=[components[-1]])
            self.allow_use_gettext(domain, module_name)
            return getattr(module, components[-1])
        except (ImportError, AttributeError) as e:
            raise ImportError(self.__("Error importing module %s : %s") % (module_name, e))
    
    def __import_all_modules(self, module_names):
        """
        Importe plusieurs modules donnés par une liste de noms et configure leurs autorisations pour gettext.
        
        Args:
            module_names (list[str]): Liste des noms complets des modules à importer.
        
        Returns:
            dict[str, Module]: Dictionnaire associant les noms courts des modules à leurs objets importés.
        """
        modules = {}
        for module_name in module_names:
            _, name = module_name.rsplit('.', 1)
            module = self.__import_dynamic(module_name)
            modules[name] = module.init(self) if hasattr(module, 'init') else module
        return modules

    def __allow_exceptions_use_gettext(self):
        """
        Ajoute une autorisation pour chaque classe d'exception présent dans le tableau 'EXCEPTIONS'
        du fichier 'setting.py'
        """
        domain = 'error'
        for name_cls_exception in EXCEPTIONS :
            name = 'Exceptions.' + name_cls_exception
            self.allow_use_gettext(domain, name)

    def __check_initiated_tools(self):
        """
        Vérifie si les outils ont été initialisés.
        
        Returns:
            bool: True si les outils ont été initialisés, False sinon.
        """
        if not self.__tools_initialized:
            raise Exception(self.__("Tools have not been initialized."))
        return True

    def allow_use_gettext(self, domain_gettext, *names_caller_modules):
        """
        Ajoute un ou plusieurs modules à la liste des modules autorisés pour un domaine gettext donné.
        
        Args:
            domain_gettext (str): Le domaine de gettext (e.g., 'cabine', 'tools').
            names_caller_modules (str): Un ou plusieurs noms de modules autorisés.
        """
        if domain_gettext not in self.__list_allowed_modules_for_gettext:
            self.__list_allowed_modules_for_gettext[domain_gettext] = []
        
        self.__list_allowed_modules_for_gettext[domain_gettext].extend(names_caller_modules)

    def _(self, message):
        """
        Encapsule la méthode '_' de la classe Gettext pour les traductions.
        
        Args:
            message (str): Texte à traduire.
        
        Returns:
            str: Texte traduit si le module appelant est autorisé, sinon le texte original.
        """
        try:
            __name_caller_module = self.getTools_Utils().GetCallingModule()
        except:
            return message
        #print(__name_caller_module)
        for domain, list_names_modules in self.__list_allowed_modules_for_gettext.items():
            if __name_caller_module in list_names_modules : 
                return self.__gettext._(domain,message)
        return message
    
    def __(self, message):
        """
        Tips : méthode interne pour forcer l'utilisation de gettext exclusivement dans ce module.
        Encapsule la méthode '_' de la classe Gettext pour les traductions.
        
        Args:
            message (str): Texte à traduire.
        
        Returns:
            str: Texte traduit.
        """
        return self.__gettext._('tools', message)
    def configure(self):
        for _cls in self.__list_cls_initialized :
            if hasattr(_cls, 'configure'):
                configure = getattr(_cls, 'configure')
                if callable(configure):
                    configure()
    
    def post_configure(self):
        for _cls in self.__list_cls_initialized :
            if hasattr(_cls, 'post_configure'):
                post_configure = getattr(_cls, 'post_configure')
                if callable(post_configure):
                    post_configure()

    def pre_run(self):
        for _cls in self.__list_cls_initialized :
            if hasattr(_cls, 'pre_run'):
                pre_run = getattr(_cls, 'pre_run')
                if callable(pre_run):
                    pre_run() 

    def GetListeAllowed(self):
        return self.__list_allowed_modules_for_gettext
    # Accesseurs pour les modules principaux  
    def GetCls_Combiner(self):
        return self.__mods_projects['Combinee']
    
    def GetCls_Son(self):
        return self.__mods_projects['Son']
    
    def GetCls_Touches(self):
        return self.__mods_projects['Touches']
    
    def GetCls_Enregistrement(self):
        return self.__mods_projects['Enregistrement']
    
    # Accesseurs pour les outils  
    def getTools_Utils(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Utils']
    
    def getTools_Check(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Check']
    
    def getTools_Argument(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Argument']
    
    def getTools_Mixer(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Mixer']
    
    def getTools_GPIO(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['GPIO']
    
    def getTools_Pad(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Pad']
    
    def getTools_Deamon(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Deamon']  
     
    def getTools_Service(self):
        if not self.__check_initiated_tools():
            return None
        return self.__tools['Service'] 
        
    
    def clean(self):
        """
        Arrête le programme proprement.
        """
        for _cls in self.__list_cls_initialized :
            if hasattr(_cls, 'clean'):
                clean = getattr(_cls, 'clean')
                if callable(clean):
                    clean()
        
    def RunScenario(self,__id_scenario):
        """
        Exécute un scénario sélectionné par son ID.
        
        Args:
            __id_scenario (int): ID du scénario (à partir de 1).
        """
        self.pre_run()
        while self.__running:
            """ 
            TODO:
            //    A terme ce programme et donc se scénario pourra être arrêté par les cas suivant: 
            //    - manuellement avec 'systemctl stop cabine'
            //    - Avec le gestionnaire cachée : Appuie sur la touche # -> 1 (arrêt programme puis système)
            //    - Lorsque l'on fait la combinaison 'Ctrl+C', met fin au programme.
            """

            try:
                self.__scenarios[__id_scenario - 1].exec()
            except KeyboardInterrupt:
                
                print("Ctrl+C à été déclancher pour mettre un terme au programme.")
                self.__running = False
        self.clean()

    def StopRunningScenario(self):
        """
        Arrête l'exécution du scénario en cours.
        """
        self.__running = False
        self.getTools_Pad().cleanup()
        

    def RunDaemon(self, options):
        """
        Exécute le programme en tant que démon.
        
        Args:
            options (Namespace): Options de la ligne de commande.
        """
        daemon = self.getTools_Deamon()
        daemon.set_options(options)
        daemon.manage_daemon()


    def RunService(self, options):
        """
        Gère l'installation du service, ainsi que sa maintenance.

        Args:
            options (Namespace): Options de la ligne de commande.
        """
        service = self.getTools_Service()
        service.set_options(options)
        service.process()

    def Run(self):
        """
        Exécute le programme principal.
        """
        argument = self.getTools_Argument()
        options = argument.get_options()
        if options.command == 'load' or options.command == None:
            from settings import SCENARIO
            scenario = SCENARIO
            if hasattr(options, 'scenario') and options.scenario != None:
                scenario = options.scenario
            self.RunScenario(scenario)
        elif options.command == 'daemon':
            self.RunDaemon(options)
        elif options.command == 'service':
            self.RunService(options)

        #Je supprime le fichier qui gère GPIO.
        self.getTools_Utils().def_tmpFile_gpio()

        

    def generate_options(self):
        """
        Génère les options de la ligne de commande.
        
        Args:
            options (dict): Dictionnaire des options à générer.
        """
        from options import OPTIONS
        argument = self.getTools_Argument()
        for key, value in OPTIONS.items():
            argument.add_args_sub_parser(key, **value)

        argument.parse_args()

    def initialise_child(self):
        """
        Initialise le processus enfant.
        """
        self.__running = True
        self.configure()
        self.post_configure()
    
# Factory pour l'initialisation du projet

def initialiser_projet():
    """
    Initialise et configure l'API du projet.

    Appeller depuis __main__.py
    Returns:
        Api: Instance configurée de la classe Api.
    """
    api = Api()
    api.configure()
    api.generate_options()
    api.post_configure()
    return api