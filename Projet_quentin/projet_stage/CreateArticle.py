import requests
from requests.auth import HTTPBasicAuth
import ssl
import os
import shutil
from datetime import datetime

site_url = "https://sandbox.mqlt.fr"
api_url = f"{site_url}/wp-json/wp/v2/posts"
categories_url = f"{site_url}/wp-json/wp/v2/categories"
tags_url = f"{site_url}/wp-json/wp/v2/tags"
media_url = f"{site_url}/wp-json/wp/v2/media"
username = "quentin"
app_password = "qgLV 47pR bbgn tFgz mxpq FRsy"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE 

session = requests.Session()
session.verify = False 

headers = {
	'User-Agent': 'Python WordPress Client',
	'Accept': 'application/json',
}

def formater_date(chaine):
	"""Formate le nom de fichier en une date lisible"""
	if chaine.endswith('.mp3'):
		chaine = chaine[:-4]
	
	# Supprime le premier chiffre si nécessaire
	parties = chaine.split('_')
	if len(parties) >= 3 and parties[0].isdigit():
		chaine = '_'.join(parties[1:])
		parties = chaine.split('_')
	
	if len(parties) < 2:
		return chaine
	
	date_part = parties[0]
	heure_part = parties[1]
	
	try:
		date_obj = datetime.strptime(date_part, '%d-%m-%Y')
		heure_obj = datetime.strptime(heure_part, '%H-%M-%S')
		
		mois_fr = [
			'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
			'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
		]
		
		jour = date_obj.day
		mois = mois_fr[date_obj.month - 1]
		annee = date_obj.year
		
		heure = heure_obj.hour
		minute = heure_obj.minute
		
		return f"{jour} {mois} {annee} à {heure}h{minute:02d}"
	except ValueError:
		return chaine

def upload_image_to_wordpress(image_path):
	try:
		with open(image_path, 'rb') as img_file:
			response = session.post(
				media_url,
				auth=HTTPBasicAuth(username, app_password),
				files={'file': (os.path.basename(image_path), img_file)},
				headers={'Content-Disposition': f'attachment; filename={os.path.basename(image_path)}'}
			)
		
		if response.status_code == 201:
			return response.json().get('id')
		else:
			print(f"Erreur lors de l'upload de l'image: {response.text}")
			return None
	except Exception as e:
		print(f"Erreur lors de l'upload de l'image: {str(e)}")
		return None

def get_or_create_category(category_name):
	params = {'search': category_name}
	response = session.get(categories_url, 
						 auth=HTTPBasicAuth(username, app_password),
						 headers=headers,
						 params=params)
	
	if response.status_code == 200:
		categories = response.json()
		for category in categories:
			if category['name'].lower() == category_name.lower():
				return category['id']
			
	data = {'name': category_name}
	response = session.post(categories_url,
						  auth=HTTPBasicAuth(username, app_password),
						  headers=headers,
						  json=data)
	
	if response.status_code == 201:
		return response.json().get('id')
	else:
		print(f"Erreur lors de la création de la catégorie: {response.text}")
		return None

def get_or_create_tag(tag_name):
	"""Fonction pour obtenir ou créer une étiquette (tag)"""
	params = {'search': tag_name}
	response = session.get(tags_url, 
						 auth=HTTPBasicAuth(username, app_password),
						 headers=headers,
						 params=params)
	
	if response.status_code == 200:
		tags = response.json()
		for tag in tags:
			if tag['name'].lower() == tag_name.lower():
				return tag['id']
			
	data = {'name': tag_name}
	response = session.post(tags_url,
						  auth=HTTPBasicAuth(username, app_password),
						  headers=headers,
						  json=data)
	
	if response.status_code == 201:
		return response.json().get('id')
	else:
		print(f"Erreur lors de la création de l'étiquette: {response.text}")
		return None

def create_post(audio_filename, image_filename=None, categorie=None):
	# Formatage du titre et de la date
	formatted_date = formater_date(audio_filename)
	
	# Upload de l'image si elle existe
	featured_media = None
	if image_filename:
		script_dir = os.path.dirname(os.path.abspath(__file__))
		image_path = os.path.join(script_dir, "image", image_filename)
		
		if os.path.exists(image_path):
			featured_media = upload_image_to_wordpress(image_path)

	now = datetime.now()
	current_year = now.year
	current_month = now.month

	excerpt = f"Témoignage enregistré le {formatted_date}"
	
	# Contenu HTML complet pour la page de l'article
	content = f"""
	<div class="testimonial-container">
		<div class="testimonial-header">
			<a href="{site_url}/?p=%post_id%" class="testimonial-title-link">
				<h1>{formatted_date}</h1>
			</a>
		</div>
		
		<span class="listen-text">Ecouter le témoignage</span>

		<div class="audio-player-container">
			<div class="audio-player">
				<audio controls>
					<source src=[audio src="https://sandbox.mqlt.fr/wp-content/uploads/{current_year}/{current_month:02d}/{audio_filename}"] type="audio/mpeg">
					Votre navigateur ne supporte pas l'élément audio.
				</audio>
			</div>
		</div>
		
		<div class="divider"></div>
		
	</div>
	"""
	
	post_data = {
		"title": f"Témoignage du {formatted_date}",
		"content": content,
		"excerpt": excerpt,
		"status": "publish",
		"comment_status": "open"
	}
	
	if featured_media:
		post_data["featured_media"] = featured_media
	
	if categorie:
		category_id = get_or_create_category(categorie)
		if category_id:
			post_data['categories'] = [category_id]
	
	tag_id = get_or_create_tag("test")
	if tag_id:
		post_data['tags'] = [tag_id]

	try:
		response = session.post(api_url,
							auth=HTTPBasicAuth(username, app_password),
							json=post_data,
							headers=headers,
							timeout=30)
		
		if response.status_code == 201:
			post_id = response.json().get('id')
			post_link = response.json().get('link')
			
			# Mettre à jour le contenu avec le bon lien
			updated_content = content.replace('%post_id%', str(post_id))
			update_data = {
				'content': updated_content
			}
			update_response = session.post(f"{api_url}/{post_id}",
										auth=HTTPBasicAuth(username, app_password),
										json=update_data,
										headers=headers)
			
			print(f"Article créé avec succès")
			print("Lien :", post_link)
			print("ID :", post_id)
			return True
		else:
			print(f"Erreur HTTP {response.status_code}")
			print("Réponse serveur :", response.text)
			return False

	except requests.exceptions.SSLError as e:
		print(f"Erreur SSL:", str(e))
		return False
		
	except requests.exceptions.RequestException as e:
		print(f"Erreur de connexion:", str(e))
		return False

	except Exception as e:
		print(f"Erreur inattendue:", type(e).__name__, "-", str(e))
		return False

def process_files():
	script_dir = os.path.dirname(os.path.abspath(__file__))
	audio_dir = os.path.join(script_dir, "audio")
	image_dir = os.path.join(script_dir, "image")
	backup_dir = os.path.join(script_dir, "backup")
	private_dir = os.path.join(script_dir, "privé")

	# Vérifie les dossiers
	if not os.path.exists(audio_dir):
		print(f"Le dossier audio n'existe pas: {audio_dir}")
		return
	
	if not os.path.exists(image_dir):
		print(f"Le dossier image n'existe pas: {image_dir}")
		return
	
	# Crée les dossiers s'ils n'existent pas
	for folder in [backup_dir, private_dir]:
		if not os.path.exists(folder):
			os.makedirs(folder)

	# Liste les fichiers audio et images
	audio_files = [f for f in os.listdir(audio_dir) if f.lower().endswith('.mp3')]
	image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
	
	# Crée un dictionnaire pour faire correspondre les noms de fichiers (sans extension)
	image_dict = {os.path.splitext(f)[0]: f for f in image_files}
	
	for audio_file in audio_files:
		audio_base = os.path.splitext(audio_file)[0]
		image_file = image_dict.get(audio_base)
		
		# Pour les fichiers commençant par "2", copie vers privé avant le traitement
		if audio_file.startswith('2'):
			try:
				src_path = os.path.join(audio_dir, audio_file)
				private_path = os.path.join(private_dir, audio_file)
				shutil.copy2(src_path, private_path)
				print(f"Fichier {audio_file} copié vers privé")
			except Exception as e:
				print(f"Erreur lors de la copie vers privé: {str(e)}")
		
		success = create_post(audio_file, image_file, categorie="Cabine de témoignages")
		
		if success:
			try:
				# Déplace l'audio vers backup
				src_audio = os.path.join(audio_dir, audio_file)
				dest_audio = os.path.join(backup_dir, audio_file)
				shutil.move(src_audio, dest_audio)
				print(f"Fichier audio {audio_file} déplacé vers backup")
				
				# Supprime l'image correspondante si elle existe
				if image_file:
					image_path = os.path.join(image_dir, image_file)
					if os.path.exists(image_path):
						os.remove(image_path)
						print(f"Fichier image {image_file} supprimé")
			except Exception as e:
				print(f"Erreur lors du déplacement/suppression des fichiers: {str(e)}")

if __name__ == "__main__":
	process_files()
