import requests
from requests.auth import HTTPBasicAuth
import os
import shutil

def upload_file_to_wordpress(file_path, wordpress_url, username, password):
	# VÉRIFICATION DE L'EXISTENCE DU FICHIER
	if not os.path.isfile(file_path):
		print(f"Erreur: Le fichier {file_path} n'existe pas.")
		return None

	# Construction de l'URL de l'API WordPress pour les médias
	api_url = f"{wordpress_url}/wp-json/wp/v2/media"
	
	try:
		# ENVOI DU FICHIER VERS WORDPRESS
		with open(file_path, 'rb') as file:
			response = requests.post(
				api_url,
				auth=HTTPBasicAuth(username, password),
				files={'file': (os.path.basename(file_path), file)},
				headers={'Content-Disposition': f'attachment; filename={os.path.basename(file_path)}'},
				verify=False
			)
		
		# TRAITEMENT DE LA RÉPONSE
		if response.status_code == 201:
			print(f"Fichier {os.path.basename(file_path)} envoyé avec succès!")
			return response.json()
		else:
			print(f"Erreur lors de l'envoi du fichier {os.path.basename(file_path)}. Code: {response.status_code}")
			print(f"Message d'erreur: {response.text}")
			return None
			
	except Exception as e:
		print(f"Une erreur s'est produite avec {os.path.basename(file_path)}: {str(e)}")
		return None

if __name__ == "__main__":
	# CONFIGURATION
	WORDPRESS_URL = "https://sandbox.mqlt.fr"
	USERNAME = "quentin"
	PASSWORD = "qgLV 47pR bbgn tFgz mxpq FRsy"
	
	# Chemins vers les dossiers
	script_dir = os.path.dirname(os.path.abspath(__file__))
	audio_dir = os.path.join(script_dir, "audio")
	private_dir = os.path.join(script_dir, "privé")
	backup_dir = os.path.join(script_dir, "backup")

	# Créer les dossiers s'ils n'existent pas
	for folder in [private_dir, backup_dir]:
		if not os.path.exists(folder):
			os.makedirs(folder)

	# Vérifier si le dossier audio existe
	if not os.path.exists(audio_dir):
		print(f"Erreur: Le dossier {audio_dir} n'existe pas.")
		exit()

	# Lister tous les fichiers dans le dossier audio
	wav_files = [f for f in os.listdir(audio_dir) if os.path.isfile(os.path.join(audio_dir, f))]
	
	if not wav_files:
		print("Aucun fichier trouvé dans le dossier audio.")
		exit()

	# Traiter chaque fichier
	for wav_file in wav_files:
		file_path = os.path.join(audio_dir, wav_file)
		
		# Vérifier si le fichier commence par "2"
		if wav_file.startswith('2'):
			try:
				# Copier vers backup
				backup_path = os.path.join(backup_dir, wav_file)
				shutil.copy2(file_path, backup_path)
				
				# Copier vers privé
				private_path = os.path.join(private_dir, wav_file)
				shutil.copy2(file_path, private_path)

				# Supprimer l'original
				os.remove(file_path)
				
			except Exception as e:
				print(f"Erreur lors du traitement du fichier {wav_file}: {str(e)}")
			continue

		if wav_file.endswith('.wav'):
			os.remove(file_path)
		
		# Pour les autres fichiers, procéder à l'upload dans le WordPress
		result = upload_file_to_wordpress(file_path, WORDPRESS_URL, USERNAME, PASSWORD)
		
		if result:
			print("Détails du fichier uploadé:")
			print(f"ID: {result.get('id')}")
			print(f"URL: {result.get('source_url')}")
			print(f"Titre: {result.get('title', {}).get('rendered', '')}")
