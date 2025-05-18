
import lgpio

# GPIO est devenu obsolète avec Raspberry Pi 5
# import RPi.GPIO as GPIO
#La ligne ci-dessous est devenue obsolète (en effet, lgpio n'utilise pas le mode BOARD)
# GPIO.setmode(GPIO.BCM)
GPIO_PIN_COMBINEE = 17
handle = lgpio.gpiochip_open(0)  # Ouvrir le premier GPIO chip
lgpio.gpio_claim_input(handle, GPIO_PIN_COMBINEE, lgpio.SET_PULL_DOWN)  # pin 17 réglée en input
#GPIO.setup(GPIO_PIN_COMBINEE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # pin 17 réglée en input
# On attend que le téléphone soit décroché

def _getGpioInput():
    import time
    time.sleep(0.01)
    return lgpio.gpio_read(handle, GPIO_PIN_COMBINEE)

# Renvoie l'état sous forme binaire
def getStateCombi(): 
    return _getGpioInput()

def combiRaccrocher():
    return getStateCombi() == True

def combiDeccrocher():
    return getStateCombi() == False

while True:
    if combiRaccrocher():
        print("Le téléphone est décroché.")

    elif combiDeccrocher():
        print("Le téléphone est raccroché.")
