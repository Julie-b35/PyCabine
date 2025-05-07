# Projet Cabine Téléphonqiue

## Étape du projet

- [ ] Initialisation du projet
  - [ ] Gestion des erreurs
  - [ ] Création de la classe utilitaire "Utils.py"
  - [ ] Gestion des Locales (Langue) "Locals.py"- il n'y a pas lieu de traduction, mais éventuellement de correction de fautes
  - [x] Gestion de l'état du Combinée (raccroché, décrocher) "Combinee.py"
  - [x] Gestion du son
  - [x] Gestion du clavier matricielle
  - [ ] Gestion de l'enregistrement
  - [ ] Mise en place de test GPIO
- [ ] Programmation des scénarios
  - [ ] Scénario 1 (témoignage simple)
  - [ ] Scénario 2 (témoignage avec possibilité de réécoute et de modification)
  - [ ] Scénario 3 (témoignage avec choix thématiques)
- [ ] Enregistrement du fichier audio
- [ ] Publication des témoignages
- [ ] Consultation des témoignages
- [ ] Nettoyage
  - [ ] Correction des fautes de frappes

---

## Utilisation de git

- Commencer par faire un fork du projet [mqlt35/PyCabine](https://github.com/mqlt35/PyCabine)
- Clonage du fork : `git clone git@github.com:Julie-b35/PyCabine.git`
- Contrôle origin du fork avec `git remote -v`. 
  - si `origine` n'y est pas, alors lancer la commande `git remote add origine URL_FORK`
- Ajouter le dépot principal du projet `git remote add upstream https://github.com/mqlt35/PyCabine`
- Récupérer les dernières info du projet `git pull upstream main`
- Créer une nouvelle branches (local) `git checkout -b develop`
  - La commande `git stash`peut être utile pour *mettre de côté* vos modification sans faire de commit
  - `git stash push -u` pour inclure les fichiers non tracker.
  - L'instruction suivante `git stash show -p stash@{0} -u > modification.patch` créer un patch depuis les modification locale.

--- 

Accès à la charte : [Charte programmation de la cabine téléphonique de témoignage](https://docs.google.com/document/d/1E6yp78fg-NJzNdO4ea2fbqAL292Jvwdpw8ky-wRRURM/edit?usp=sharing)

Voir
 [Programmation d'une cabine téléphonique anglaise - cabine de témoignages](https://www.wiki-rennes.fr/Programmation_d%27une_cabine_t%C3%A9l%C3%A9phonique_anglaise_-_cabine_de_t%C3%A9moignages)



Scénario : [Scénarios de fonctionnement de la cabine](https://docs.google.com/document/d/18E6q68mggDVUanxJHCBvNwsLgTKLPwkZbg_32MTsQv0/edit?usp=sharing)

---

## Environnement de développement

Afin d'éviter de polluer le dépôt git, j'utilise environnement de virtuelle de python

```BASH
python -m venv ./venv
```

Pour lancer l'environnement virtuelle de python faire :

```BASH
source ./venv/bin/activate
```

Pour quiter l'environnement virtuelle faire :

```BASH
deactivate
```
## Exigences

### Modules python

Pour installer les modules, lancer la commande `pip install -r requirements.txt` en particulier dans l'environnement virtuelle

#### Attention

Le module `sounddevice` nécessite l'installation du paquet `libportaudio2`
```BASH
sudo apt-get install libportaudio2
```

et aussi
```BASH
sudo apt install gettext
```