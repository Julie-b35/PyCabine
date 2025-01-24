#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Déclancher une erreur si le script est exécuté directement.
if __name__ == "__main__" : 
    raise Exception("Ce scripte n'est pas exécutable.")

INSTALL = "process_install"
UNINSTALL = "process_uninstall"
REINSTALL = "process_reinstall"

DIRECTORY_SERVICE = '/etc/systemd/system/'
SYSTEMCTL = '/usr/bin/systemctl'

class Service:
    def __init__(self, api):
        from settings import NAME_SERVICE
        import subprocess
        import sys
        import os
        # Associer la fonction de gestion des touches au clavier
        self.__api = api
        self.__mode = None
        self.__name_service = NAME_SERVICE + '.service'
        self.__subprocess = subprocess
        self.__sys = sys
        self.__os = os
        self.__directory_ressources = None
        
        print("Services")
        #print(CONTENTE)

    def configure(self):
        self.__directory_ressources = self.__api.getTools_Utils().getWorkDir() + "/ressources/"
        self.__content_service_file = self.genere_service()


    def genere_service(self):
        _utils = self.__api.getTools_Utils()
        uid, group, username = self.get_user()
        content =  _utils.get_content_file(self.__directory_ressources + self.__name_service).format(
            USER = username,
            GROUP = group,
            UID = uid
        )
        return content

    def get_user(self):
        import os
        import grp
        import getpass
        uid, group, username = "", "", ""
        if os.geteuid() == 0:
            # Je suis en mode root, donc jouer avec la variable d'environnement.
            uid = int(os.getenv('SUDO_UID'))
            username = os.getenv('SUDO_USER')
            group = grp.getgrgid(int(os.getenv('SUDO_GID'))).gr_name
        else:
            uid = os.getuid()
            username = getpass.getuser()
            group = grp.getgrgid(os.getgid()).gr_name

        return uid, group, username

    def set_options(self, options):
        if (options.install) : 
            self.__mode = INSTALL
        elif (options.uninstall) : 
            self.__mode = UNINSTALL
        elif (options.reinstall) : 
            self.__mode = REINSTALL

    def check_root(self):
        if self.__os.geteuid() != 0:
            print("Ce programme doit être exécuté en tant que root. Tentative d'élévation...")
            resultat = self.exec(['sudo', '-E', self.__sys.executable] + self.__sys.argv)
            print(resultat.stdout)
        else :
            return True

    def check_service(self):
        return self.exec([SYSTEMCTL, 'status', self.__name_service], raise_error = False)

    def process_install(self):
        _utils = self.__api.getTools_Utils()
        if not _utils.file_exists(DIRECTORY_SERVICE + self.__name_service) : 
            _utils.write_file(DIRECTORY_SERVICE + self.__name_service, self.__content_service_file)
            print(self.__content_service_file)

        if not self.check_service():
            self.daemon_reload()
            self.exec([SYSTEMCTL, 'enable', self.__name_service])
            print("Le service {} à été installé avec succès.".format(self.__name_service))
            
        else :
            print("Le service {} à déja été installé.".format(self.__name_service))
        
    def process_uninstall(self):
        _utils = self.__api.getTools_Utils()
        if self.check_service():
            #S'assurer que le service est désactiver
            self.exec([SYSTEMCTL, 'disable', self.__name_service])
            if _utils.file_exists(DIRECTORY_SERVICE + self.__name_service):
                self.__api.getTools_Utils().del_file(DIRECTORY_SERVICE + self.__name_service)
            self.daemon_reload()
        else :
            print("Le service {} à déja été supprimé.".format(self.__name_service))
        
    def process_reinstall(self):
        self.process_uninstall()
        self.process_install()
        
    def daemon_reload(self) :
        self.exec([SYSTEMCTL, 'daemon-reload']) 

    def exec(self, cmd, raise_error = True) :
            try:
                result = self.__subprocess.run(cmd, check=True, text=True, capture_output=True)
            except self.__subprocess.CalledProcessError as e:
                if raise_error :
                    print(f"Erreur lors de l'exécution : {e.stderr}")
                    raise e
                else :
                    return False
            if raise_error:
                return result
            else :
                return True

    def process(self):
        if self.check_root():
            getattr(self, self.__mode)()
def init(api):
    return Service(api)