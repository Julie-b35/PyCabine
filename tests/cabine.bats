#!/usr/bin/env bats

# Crée un répertoire temporaire
TMPDIR=$(mktemp -d)
export TMPDIR

setup() { 
    # Crée et active un environnement virtuel
    python3 -m venv $TMPDIR/venv
    source $TMPDIR/venv/bin/activate

    # obtenir le répertoire contenant ce fichier
    # utiliser $BATS_TEST_FILENAME au lieu de ${BASH_SOURCE[0]} ou $0,
    # car ceux-ci pointeront respectivement vers l'emplacement de l'exécutable bats ou vers le fichier prétraité
    DIR="$( cd "$( dirname "$( dirname "$BATS_TEST_FILENAME" )")" >/dev/null 2>&1 && pwd )"

    #copier les fichiers nécessaire dans le répertoire temporaire
    # il faut vérier si le scripte est lancé depuis un container docker ou depuis un environnement local

    cp -r "$DIR"/* $TMPDIR/
}

teardown() { 
    # Désactive l'environnement virtuel et supprime le répertoire temporaire
    deactivate
    #rm -rf $TMPDIR
}
@test "Test si le script de cabine fonctionne" {
    run $TMPDIR/bin/cabine
    echo $output
    [ "$status" -eq 0 ]
}