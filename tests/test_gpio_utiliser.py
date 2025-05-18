import lgpio

h = lgpio.gpiochip_open(0)  # ouvre /dev/gpiochip0
lines = lgpio.gpio_get_chip_info(h)
print("Nom de la puce :", lines[0])

for i in range(0, 32):  # généralement 0 à 31
    try:
        info = lgpio.gpio_get_line_info(h, i)
        print(info)
        if info[2]:  # info[2] = is_used
            print(f"GPIO {i} est utilisé par {info[1]}")
    except Exception as e:
        print(f"Erreur sur GPIO {i} :", e)

lgpio.gpiochip_close(h)