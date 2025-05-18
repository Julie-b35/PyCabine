#!/bin/bash
#python CreateImage.py
SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

python "$SCRIPT_DIR/UploadFichier.py"
python "$SCRIPT_DIR/CreateArticle.py"
#read -p "Appuyez sur une touche pour continuer"