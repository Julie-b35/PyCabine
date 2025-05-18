import lgpio
import time

# Colonnes à activer (sortie)
COLONNES = {
    "B": 22,
    "D": 21,
    "F": 27,
    "H": 23,
    "J": 24,
}

# Lignes à écouter (entrée)
LIGNES = {
    "A": 5,
    "C": 6,
    "E": 13,
    "G": 4,
    "I": 26,
}

h = lgpio.gpiochip_open(0)

# Configure les colonnes en sortie (LOW par défaut)
for nom, gpio in COLONNES.items():
    lgpio.gpio_claim_output(h, gpio, 0)

# Configure les lignes en entrée avec pull-down
for nom, gpio in LIGNES.items():
    lgpio.gpio_claim_input(h, gpio, lgpio.SET_PULL_DOWN)

print("🟢 Test clavier matriciel (colonnes = BDFHJ, lignes = ACEGI)")

try:
    while True:
        for col_nom, col_gpio in COLONNES.items():
            # Active la colonne (HIGH)
            lgpio.gpio_write(h, col_gpio, 1)

            for lig_nom, lig_gpio in LIGNES.items():
                if lgpio.gpio_read(h, lig_gpio) == 1:
                    print(f"🔘 Touche détectée : colonne {col_nom} + ligne {lig_nom}")

            # Désactive la colonne (LOW)
            lgpio.gpio_write(h, col_gpio, 0)

        time.sleep(0.05)  # anti-rebond

except KeyboardInterrupt:
    print("\n🛑 Fin du test.")

finally:
    lgpio.gpiochip_close(h)
