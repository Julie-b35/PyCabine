from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
import os

def extract_datetime_from_filename(filename):
	"""Extrait la date et l'heure du nom de fichier audio"""
	try:
		# Supprime l'extension .mp3 si présente
		if filename.lower().endswith('.mp3'):
			filename = filename[:-4]
		
		# Supprime le premier chiffre
		parts = filename.split('_')
		if len(parts) >= 3 and parts[0].isdigit():
			filename = '_'.join(parts[1:])
		
		# Extrait la date et l'heure
		parts = filename.split('_')
		if len(parts) >= 2:
			date_part = parts[0]
			time_part = parts[1]
			
			# Convertit en objet datetime
			date_obj = datetime.strptime(date_part, '%d-%m-%Y')
			time_obj = datetime.strptime(time_part, '%H-%M-%S')
			
			return date_obj, time_obj
	except Exception as e:
		print(f"Erreur lors de l'extraction de la date/heure: {str(e)}")
	
	return datetime.now(), datetime.now()

def generate_miniature_for_audio(audio_filename, input_image_path="test.jpg"):
	# Vérifie si le fichier commence par "2" (ne pas créer d'image)
	if audio_filename.startswith('2'):
		print(f"Fichier {audio_filename} ignoré (commence par '2')")
		return None
	
	# Crée le dossier image s'il n'existe pas
	script_dir = os.path.dirname(os.path.abspath(__file__))
	image_dir = os.path.join(script_dir, "image")
	if not os.path.exists(image_dir):
		os.makedirs(image_dir)
	
	# Chemin de sortie basé sur le nom de l'audio
	output_filename = os.path.splitext(audio_filename)[0] + ".jpg"
	output_path = os.path.join(image_dir, output_filename)
	
	# Extrait la date et l'heure du nom de fichier
	date_obj, time_obj = extract_datetime_from_filename(audio_filename)
	
	# Ouvre l'image de base
	original_image = Image.open(input_image_path)
	width, height = 800, 450  # Ratio 16:9
	resized_image = ImageOps.fit(original_image, (width, height), method=Image.LANCZOS)
	
	# Crée un calque noir semi-transparent
	overlay = Image.new('RGBA', (width, height), (0, 0, 0, 160))
	resized_image.paste(overlay, (0, 0), overlay)
	
	draw = ImageDraw.Draw(resized_image)
	
	# Charge la police
	try:
		font_large = ImageFont.truetype("arialbd.ttf", 60)
	except:
		font_large = ImageFont.load_default()
	
	# Formatage de la date et heure
	mois_fr = [
		'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
		'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
	]
	
	date_str = f"{date_obj.day} {mois_fr[date_obj.month - 1]} {date_obj.year}"
	time_str = time_obj.strftime("%H:%M")
	datetime_text = f"{date_str} • {time_str}"
	
	# Position centrale
	text_width = draw.textlength(datetime_text, font=font_large)
	x_position = (width - text_width) / 2
	y_position = (height - 80) / 2
	
	# Dessin du texte avec ombre
	draw.text(
		(x_position + 2, y_position + 2),
		datetime_text,
		fill="black",
		font=font_large,
		stroke_width=4,
		stroke_fill="black"
	)
	draw.text(
		(x_position, y_position),
		datetime_text,
		fill="white",
		font=font_large,
		stroke_width=0
	)
	
	# Bordure blanche
	final_image = ImageOps.expand(resized_image, border=15, fill="white")
	
	# Sauvegarde
	final_image.save(output_path)
	print(f"Miniature générée: {output_path}")
	return output_filename

def process_audio_folder():
	script_dir = os.path.dirname(os.path.abspath(__file__))
	audio_dir = os.path.join(script_dir, "audio")
	
	if not os.path.exists(audio_dir):
		print(f"Le dossier audio n'existe pas: {audio_dir}")
		return
	
	audio_files = [f for f in os.listdir(audio_dir) if f.lower().endswith('.mp3')]
	
	if not audio_files:
		print("Aucun fichier audio trouvé dans le dossier audio.")
		return
	
	for audio_file in audio_files:
		generate_miniature_for_audio(audio_file)

if __name__ == "__main__":
	process_audio_folder()