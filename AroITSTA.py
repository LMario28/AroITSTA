# NOTAS:

# 1) Las posiciones de los LEDs son:
#    Circunferencia: 1-180 (0-179)
#    Linea izquierda: 232-290 (231-289)
#    Linea derecha: 181-231 (180-230)

# 2) El orden en los datos del tiempo (tupla) es:
#    Año, mes (1-12), día del mes (1-31), hora (0-23), minuto (0-59), segundo (0-59), día de
#    la semana (0-6 de lunes a domingo), día de año (1-366)

# 3) Pasos para actualizar el sketch en el ESP32

#    Requisitos: 1) Debe estar en donde está la aplicación el sketch ota.py;
#                2) En GitHub, repositorio Aro debe existir  un arhivo con nombre version.json con las lineas:
#                   {
#                     "version":2
#                   }
#                   el número de la versión debe ser mayor que el mismo archivo en el ESP32

#    a) Abrir www.github.com
#    b) lmmsegura@hotmail.com / le...24
#    c) Copiar la nueva versión del sketch a GitHub, repositorio Aro

# 4) Los timers no se borran (pendiente corregir)

# 5) Correr con al menos MicroPython v.1.27

import machine
from machine import Pin
import neopixel
import time

import BlynkLib_deepseek     # https://github.com/vshymanskyy/blynk-library-python/blob/master/examples/03_sync_virtual.py
from BlynkTimer_lmms import BlynkTimer
import network
from ota_deepseek import OTAUpdater
import random
import math

from machine import WDT

#///////////////////////////////////////////////////////////////////////////////
#/                               CONSTANTES                                   //
#///////////////////////////////////////////////////////////////////////////////
WIFI_SSID = ['INFINITUM2426_2.4','Electronica Hotspot PC','Xperia XZ2','TP-Link_LMario_DHCP']
WIFI_PASS = ['CNnC917MDE','electronica26','lmario28','lmario28']
STATIC_IP_CONFIG = ('192.168.40.222', '255.255.255.0', '192.168.40.1', '4.2.2.2 8.8.8.8')
SSID=''
PASSWD=''
BLYNK_AUTH = 'apvVB1KTve_HC0uEb8ltb7tME6GhWIBs'

NUMERO_LEDs_RELOJ=291
NUMERO_LEDS_SOLO_ARO=180
NUMERO_FILAS_PANTALLA=24
NUMERO_COLUMNAS_PANTALLA=24
NUMERO_LEDs_PANTALLA=576                                                       # Filas: 24, Columnas: 24
PERIODO_FLASH_LED=1000
LEDs_HORA=15
LEDs_MINUTO=3

# Rangos de LEDs
CIRCULO_INICIO = 0
CIRCULO_FIN = 179
LINEA_IZQUIERDA_ARRIBA = 289
LINEA_IZQUIERDA_ABAJO = 231
LINEA_DERECHA_ARRIBA = 180
LINEA_DERECHA_ABAJO = 230
INTERVALO_BASE_ENTRE_TICKS=200                                                      # ms

NUMERO_PALETAS_COLORES=4

# COLORES RELOJ
# Facinación
COLOR_RELOJ_HORAS_INACTIVAS_FASCINACION=(20,0,20)
COLOR_RELOJ_MINUTOS_INACTIVOS_FASCINACION=(0,4,0)
COLOR_RELOJ_HORA_ACTIVA_FASCINACION=(255,0,0)
COLOR_RELOJ_MINUTO_ACTIVO_FASCINACION=(0,255,0)
COLOR_RELOJ_SEGUNDO_ACTIVO_FASCINACION=(255,255,0)
#Nebula
COLOR_RELOJ_HORAS_INACTIVAS_NEBULA=(0,0,20)
COLOR_RELOJ_MINUTOS_INACTIVOS_NEBULA=(4,4,4)
COLOR_RELOJ_HORA_ACTIVA_NEBULA=(255,255,255)
COLOR_RELOJ_MINUTO_ACTIVO_NEBULA=(0,255,180)
COLOR_RELOJ_SEGUNDO_ACTIVO_NEBULA=(254,50,0)
#Minimalista
COLOR_RELOJ_HORAS_INACTIVAS_MINIMALISTA=(0,0,0)
COLOR_RELOJ_MINUTOS_INACTIVOS_MINIMALISTA=(0,0,0)
COLOR_RELOJ_HORA_ACTIVA_MINIMALISTA=(255,0,0)
COLOR_RELOJ_MINUTO_ACTIVO_MINIMALISTA=(0,255,0)
COLOR_RELOJ_SEGUNDO_ACTIVO_MINIMALISTA=(255,255,255)

# COLORES NAVIDEÑOS
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
BLANCO = (255, 255, 255)
DORADO = (255, 215, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
MARRON = (139, 69, 19)                                                         # Color para el tronco
CAFE = (128, 64, 0)                                                            # Color para el tronco

DENSIDAD_COPOS_NIEVE=40

# 16,15,15,15,15,15,15,15,15,15,15,17 LEDs
#define NUMERO_INTENTOS 5

#define MAXIMUN_RETRIES_TO_CONNECT_BLYNK 20                                    //
#define MAXIMUN_ATTEMPTS_TO_RECONNECT_WIFI 18                                  // Intentos maximos para conectarse a la red WiFi
#define TIEMPO_ESPERA_RECONECTAR_BLYNK 30000L                                  // Tiempo de espera par intentar reconectare a Blynk (milliseconds)

# ANIMACIONES
NUMERO_ANIMACIONES=14
#                              Arbol      Copos de     Rotación       Halloween Eyes  Cylon Bounce
#                             navideño     nieve       Navidad
BANDERA_ANIMACION_ACTIVA = [   True,       True,        True,           False,          False,     \
#                             New KITT       Twinkle     Twinkle Random      Sparkle      Snow Sparkle
#                             (Navidad)                     (Navidad)                       (Navidad)
                               False,          False,          False,           False,          False,      \
#                           Running Lights  Color Wipe    Rainbow Cycle    Theater Chase
#                             (Navidad)                     (Navidad)        (Navidad)
                               False,          False,          False,           False                       \
                           ]

#ANIMACION=5                                                                   # 1: Flash LED, 2: Todo blanco, 3: Reloj, 4: Bandera, 5. Fiestas patrias,
ZONA_MEXICO=-6                                                                 # 6. Navidad 1, 7. Navidad 2
WATCHDOG=False
DURACION_CUADRO_ANIMACIONES=5
#NUMERO_ANIMACIONES=5

STROBE_NUMERO_FLASHES=10
STROBE_DURACION_FLASH=50

NEWKITT_ROJO=0
NEWKITT_VERDE=255
NEWKITT_AZUL=0
NEWKITT_TAMANO_OJO=8
NEWKITT_VELOCIDAD_ANIMACION=10
NEWKITT_PAUSA_AL_FINAL=50

# LOGO
LOGO_ELECTRONICA_RGB=[
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (0, 48, 103),
    (0, 48, 103),
    (0, 48, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 1
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (0, 48, 103),
    (0, 48, 103),
    (0, 48, 103),
    (1, 49, 102),
    (0, 48, 103),
    (0, 47, 103),
    (0, 48, 103),
    (1, 49, 102),
    (0, 48, 103),
    (0, 48, 103),
    (0, 48, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 2
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 102),
    (0, 48, 103),
    (0, 48, 103),
    (0, 48, 103),
    (3, 51, 101),
    (17, 72, 90),
    (26, 87, 82),
    (15, 68, 92),
    (3, 50, 102),
    (0, 48, 103),
    (0, 48, 103),
    (0, 48, 103),
    (1, 49, 102),
    (0, 48, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 3
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (3, 52, 101),
    (14, 68, 92),
    (21, 79, 86),
    (17, 68, 92),
    (23, 79, 87),
    (51, 128, 60),
    (72, 160, 42),
    (51, 127, 61),
    (22, 77, 88),
    (17, 68, 92),
    (20, 78, 87),
    (15, 68, 92),
    (3, 50, 102),
    (0, 48, 103),
    (1, 49, 102),
    (1, 49, 102),
    (1, 49, 102),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 4
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (0, 48, 103),
    (0, 48, 103),
    (13, 67, 93),
    (48, 122, 64),
    (69, 155, 45),
    (65, 148, 49),
    (66, 150, 48),
    (72, 161, 42),
    (75, 164, 40),
    (72, 161, 42),
    (67, 151, 47),
    (64, 147, 50),
    (65, 148, 49),
    (48, 119, 65),
    (25, 77, 87),
    (18, 62, 95),
    (18, 62, 95),
    (13, 58, 97),
    (4, 51, 101),
    (1, 49, 102),
    (1, 49, 103),
    # Fila 5
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 102),
    (0, 48, 103),
    (0, 48, 103),
    (19, 76, 88),
    (57, 135, 56),
    (75, 165, 40),
    (68, 153, 46),
    (61, 137, 55),
    (67, 130, 60),
    (78, 130, 60),
    (68, 130, 60),
    (60, 136, 56),
    (67, 150, 48),
    (86, 147, 50),
    (135, 154, 47),
    (175, 177, 34),
    (180, 179, 33),
    (180, 179, 33),
    (146, 154, 46),
    (59, 91, 80),
    (3, 50, 101),
    (1, 49, 103),
    # Fila 6
    (1, 49, 103),
    (1, 49, 103),
    (3, 52, 101),
    (14, 68, 92),
    (27, 89, 81),
    (49, 125, 62),
    (67, 152, 48),
    (67, 136, 56),
    (105, 139, 55),
    (172, 175, 35),
    (210, 203, 19),
    (221, 211, 14),
    (212, 204, 18),
    (169, 175, 35),
    (102, 138, 55),
    (68, 122, 64),
    (106, 143, 53),
    (151, 167, 41),
    (151, 167, 41),
    (147, 161, 43),
    (117, 134, 58),
    (48, 83, 85),
    (3, 50, 101),
    (1, 49, 103),
    # Fila 7
    (1, 49, 103),
    (1, 49, 103),
    (13, 67, 93),
    (47, 120, 64),
    (71, 160, 43),
    (70, 157, 44),
    (72, 136, 56),
    (138, 157, 44),
    (226, 214, 13),
    (253, 234, 2),
    (246, 229, 5),
    (239, 223, 9),
    (245, 228, 6),
    (253, 234, 2),
    (224, 213, 14),
    (133, 154, 45),
    (63, 124, 61),
    (61, 142, 52),
    (66, 150, 48),
    (45, 117, 66),
    (12, 65, 94),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 8
    (1, 49, 103),
    (0, 48, 103),
    (18, 75, 89),
    (57, 135, 56),
    (75, 165, 40),
    (70, 140, 53),
    (130, 153, 45),
    (226, 214, 13),
    (228, 216, 12),
    (155, 161, 42),
    (79, 105, 72),
    (54, 87, 82),
    (81, 107, 71),
    (153, 160, 43),
    (228, 216, 12),
    (224, 213, 14),
    (133, 157, 45),
    (71, 142, 53),
    (74, 164, 40),
    (54, 132, 57),
    (16, 73, 90),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 9
    (1, 49, 103),
    (0, 48, 103),
    (8, 59, 97),
    (43, 114, 67),
    (65, 149, 49),
    (98, 145, 51),
    (196, 193, 25),
    (223, 212, 15),
    (123, 138, 55),
    (26, 66, 93),
    (12, 56, 98),
    (44, 80, 87),
    (37, 75, 90),
    (25, 66, 93),
    (119, 135, 56),
    (223, 212, 14),
    (192, 191, 26),
    (95, 141, 53),
    (63, 146, 50),
    (42, 114, 68),
    (6, 57, 98),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 10
    (1, 49, 103),
    (3, 50, 101),
    (18, 73, 89),
    (51, 127, 60),
    (70, 139, 53),
    (133, 155, 44),
    (224, 213, 14),
    (169, 172, 37),
    (46, 81, 86),
    (3, 51, 101),
    (68, 99, 76),
    (123, 143, 53),
    (58, 96, 77),
    (5, 52, 101),
    (54, 87, 82),
    (175, 176, 34),
    (222, 211, 15),
    (126, 158, 44),
    (63, 141, 53),
    (52, 128, 60),
    (17, 72, 90),
    (3, 50, 101),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 11
    (1, 49, 103),
    (15, 71, 91),
    (49, 124, 62),
    (69, 157, 45),
    (69, 138, 54),
    (145, 164, 39),
    (224, 213, 14),
    (129, 142, 53),
    (19, 61, 96),
    (51, 85, 83),
    (167, 170, 36),
    (214, 205, 18),
    (169, 173, 36),
    (145, 156, 45),
    (158, 165, 41),
    (208, 201, 20),
    (236, 222, 9),
    (148, 165, 38),
    (69, 137, 54),
    (70, 157, 44),
    (48, 122, 63),
    (15, 70, 91),
    (0, 48, 103),
    (1, 49, 103),
    # Fila 12
    (1, 49, 103),
    (21, 81, 85),
    (60, 142, 53),
    (74, 164, 40),
    (75, 141, 53),
    (152, 167, 38),
    (219, 209, 16),
    (118, 134, 56),
    (36, 73, 89),
    (120, 136, 56),
    (223, 212, 14),
    (249, 231, 4),
    (241, 226, 6),
    (233, 219, 9),
    (233, 219, 9),
    (233, 219, 9),
    (217, 208, 16),
    (137, 157, 43),
    (69, 137, 54),
    (75, 165, 40),
    (59, 139, 54),
    (20, 78, 87),
    (0, 47, 103),
    (1, 49, 103),
    # Fila 13
    (1, 49, 103),
    (8, 60, 96),
    (34, 98, 76),
    (63, 144, 52),
    (70, 140, 53),
    (141, 161, 42),
    (226, 213, 15),
    (144, 153, 47),
    (38, 75, 88),
    (51, 83, 86),
    (143, 151, 50),
    (180, 180, 33),
    (104, 125, 62),
    (59, 91, 80),
    (59, 91, 80),
    (59, 91, 80),
    (54, 88, 82),
    (44, 94, 78),
    (55, 133, 57),
    (65, 145, 50),
    (34, 96, 77),
    (6, 57, 98),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 14
    (1, 49, 103),
    (0, 48, 103),
    (10, 62, 95),
    (46, 118, 65),
    (64, 144, 51),
    (113, 150, 48),
    (215, 206, 18),
    (195, 193, 25),
    (68, 100, 76),
    (24, 65, 93),
    (90, 113, 68),
    (83, 108, 71),
    (12, 56, 98),
    (2, 49, 102),
    (19, 62, 96),
    (26, 67, 93),
    (10, 56, 98),
    (24, 83, 84),
    (57, 137, 55),
    (45, 118, 65),
    (9, 60, 96),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 15
    (1, 49, 103),
    (1, 49, 103),
    (11, 64, 94),
    (46, 119, 65),
    (69, 156, 45),
    (83, 142, 53),
    (168, 177, 34),
    (238, 223, 8),
    (176, 176, 33),
    (75, 102, 75),
    (27, 67, 93),
    (8, 54, 99),
    (3, 51, 101),
    (20, 63, 95),
    (54, 84, 86),
    (75, 98, 80),
    (50, 90, 83),
    (43, 114, 68),
    (68, 153, 46),
    (44, 117, 66),
    (9, 60, 96),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 16
    (1, 49, 103),
    (1, 49, 103),
    (18, 75, 88),
    (57, 135, 56),
    (77, 168, 38),
    (66, 147, 49),
    (96, 139, 55),
    (193, 191, 26),
    (249, 231, 4),
    (221, 211, 15),
    (165, 169, 39),
    (137, 148, 50),
    (115, 131, 60),
    (82, 105, 75),
    (78, 101, 79),
    (74, 100, 78),
    (60, 111, 71),
    (65, 147, 50),
    (77, 168, 38),
    (56, 134, 56),
    (16, 73, 90),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 17
    (1, 49, 103),
    (1, 49, 103),
    (8, 60, 96),
    (34, 98, 76),
    (58, 135, 57),
    (67, 152, 47),
    (64, 144, 51),
    (89, 136, 56),
    (171, 178, 33),
    (235, 222, 9),
    (254, 235, 2),
    (248, 230, 5),
    (178, 178, 33),
    (88, 111, 70),
    (63, 93, 80),
    (57, 107, 71),
    (62, 141, 53),
    (66, 150, 48),
    (56, 130, 59),
    (34, 96, 77),
    (6, 57, 98),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 18
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (3, 51, 101),
    (8, 60, 97),
    (33, 98, 76),
    (65, 149, 49),
    (67, 152, 47),
    (66, 133, 57),
    (101, 138, 55),
    (140, 158, 45),
    (149, 162, 43),
    (108, 136, 55),
    (53, 110, 69),
    (48, 121, 64),
    (66, 150, 47),
    (65, 148, 49),
    (34, 99, 76),
    (9, 60, 96),
    (3, 52, 101),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 19
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (0, 48, 103),
    (18, 74, 89),
    (57, 135, 56),
    (78, 169, 38),
    (74, 164, 40),
    (68, 154, 46),
    (64, 146, 50),
    (63, 144, 52),
    (64, 147, 50),
    (69, 156, 45),
    (75, 165, 40),
    (78, 169, 38),
    (56, 135, 56),
    (17, 73, 90),
    (0, 47, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 20
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (8, 60, 96),
    (34, 99, 76),
    (50, 124, 63),
    (42, 112, 69),
    (48, 121, 64),
    (67, 152, 47),
    (78, 169, 38),
    (68, 153, 46),
    (48, 121, 64),
    (42, 112, 69),
    (49, 121, 64),
    (34, 96, 77),
    (6, 58, 98),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 21
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (3, 51, 101),
    (5, 53, 100),
    (3, 50, 101),
    (8, 60, 96),
    (35, 102, 74),
    (56, 132, 58),
    (34, 99, 76),
    (6, 58, 98),
    (3, 51, 101),
    (6, 55, 100),
    (3, 52, 101),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 22
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (3, 51, 101),
    (6, 55, 100),
    (3, 52, 101),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    # Fila 23
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
    (1, 49, 103),
]

#///////////////////////////////////////////////////////////////////////////////
#/                                 OBJETOS                                    //
#///////////////////////////////////////////////////////////////////////////////
pixels = neopixel.NeoPixel(Pin(48, Pin.OUT), NUMERO_LEDs_RELOJ)
pixelsPantalla = neopixel.NeoPixel(Pin(47, Pin.OUT), NUMERO_LEDs_PANTALLA)
from machine import RTC
(year, month, mday, weekday, hour, minute, second, milisecond)=RTC().datetime()                
if (WATCHDOG):
  wdt = WDT(timeout = 30000)

#///////////////////////////////////////////////////////////////////////////////
#/                               VARIABLES                                    //
#///////////////////////////////////////////////////////////////////////////////
tiempoLocal=''
redActiva=0
fechaHoraInicio=''
ahorita=''
diaInicial=''
#timerReloj=''
banderaHoraRecuperadaBlynk=False
opcion_seleccionada_azar=0
i=1
j=1
k=0
bandera_reloj=True
bandera_animacion_iniciada=False
incrementoDecremento=1
contadorAnimaciones=0

factor_ajuste_brillo_inactivos=0.5
factor_ajuste_brillo_activos=1
color_reloj_horas_inactivas=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_HORAS_INACTIVAS_FASCINACION)
color_reloj_horas_inactivas = tuple(int(d+0.5) for d in color_reloj_horas_inactivas)
color_reloj_minutos_inactivos=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_MINUTOS_INACTIVOS_FASCINACION)
color_reloj_minutos_inactivos = tuple(int(d+0.5) for d in color_reloj_minutos_inactivos)
color_reloj_hora_activa=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_HORA_ACTIVA_FASCINACION)
color_reloj_hora_activa = tuple(int(d+0.5) for d in color_reloj_hora_activa)
color_reloj_minuto_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_MINUTO_ACTIVO_FASCINACION)
color_reloj_minuto_activo = tuple(int(d+0.5) for d in color_reloj_minuto_activo)
color_reloj_segundo_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_SEGUNDO_ACTIVO_FASCINACION)
color_reloj_segundo_activo = tuple(int(d+0.5) for d in color_reloj_segundo_activo)
paletaColores=-1
bandera_ajuste_luz_ambiental=False

offset=0

#///////////////////////////////////////////////////////////////////////////////
#/                               FUNCIONES                                    //
#///////////////////////////////////////////////////////////////////////////////
#-------------------------------------------------------------------------------
def seleccionarMejorRedWiFiDisponible():
#-------------------------------------------------------------------------------

  global SSID
  global PASSWD
  global redActiva

  wiFi = network.WLAN(network.STA_IF)
  wiFi.active(True)

  authmodes = ['Open', 'WEP', 'WPA-PSK' 'WPA2-PSK4', 'WPA/WPA2-PSK']
  redesWiFiDisponibles = wiFi.scan()
  print(redesWiFiDisponibles)
  rssiMasFuerte = -999
  for (ssid, bssid, channel, RSSI, authmode, hidden) in redesWiFiDisponibles:
    ssidLocal="{:s}".format(ssid)
    try:
      indiceRed=WIFI_SSID.index(ssidLocal)
      rssiLocal="{}".format(RSSI)
      rssiLocal = int(rssiLocal)
    except ValueError:
      continue
    if(int(rssiLocal)>rssiMasFuerte):
      SSID = ssidLocal
      PASSWD = WIFI_PASS[indiceRed]
      redActiva = indiceRed + 1
      rssiMasFuerte = rssiLocal
        
    print(ssidLocal)
    #print("   - Auth: {} {}".format(authmodes[authmode], '(hidden)' if hidden else ''))
    #print("   - Channel: {}".format(channel))
    print("   - RSSI: {}".format(RSSI))
    #print("   - BSSID: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*bssid))
    print()

  print("Mejor red disponible:",SSID,"|",PASSWD)

#-------------------------------------------------------------------------------
def actualizarSketch():
#-------------------------------------------------------------------------------
  global SSID
  global PASSWD

  firmware_url = "https://raw.githubusercontent.com/LMario28/AroITSTA/"

  print("*************************")
  print("ACTUALIZANDO SKETCH...")
  try:
    ota_updater = OTAUpdater(SSID, PASSWD, firmware_url, "AroITSTA.py")
    ota_updater.download_and_install_update_if_available()
  except:
    print("NO SE PUDO ACTUALIZAR EL SKETCH")
  print("*************************")

#-------------------------------------------------------------------------------
def desplegarMensajeVisual(tipLla):
#-------------------------------------------------------------------------------
  # Conexión a red WLAN fallida (un parpadeo en rojo)
  if(tipLla==1):
    for i in range(1):
      pixels.fill((255,0,0))
      pixels.write()
      time.sleep(0.25)
      pixels.fill((0,0,0))
      pixels.write()
      time.sleep(0.25)
  # Conexión a red WLAN exitosa (un parpadeo en verde opaco)
  elif(tipLla==2):
    for i in range(1):
      pixels.fill((0,100,0))
      pixels.write()
      time.sleep(0.25)
      pixels.fill((0,0,0))
      pixels.write()
      time.sleep(0.25)
  # Conexión a Blink WLAN exitosa (un parpadeo en verde brillante)
  elif(tipLla==3):
    for i in range(1):
      pixels.fill((0,255,0))
      pixels.write()
      time.sleep(0.25)
      pixels.fill((0,0,0))
      pixels.write()
      time.sleep(0.25)
      
#-------------------------------------------------------------------------------
def actualizarHora():
#-------------------------------------------------------------------------------
  if(not banderaReloj):
    return

  global tiempoLocal

  pixels.fill((0,0,0))
  desplegarEsqueleto()
  desplegarHoraHora()
  desplegarHoraMinuto()
  desplegarHoraSegundo()
  pixels.write()

#-------------------------------------------------------------------------------
def desplegarEsqueleto():
#-------------------------------------------------------------------------------
  # MINUTO MINUTO MINUTO
  for i in range(60):
    pixels[3*i] = color_reloj_minutos_inactivos

  # HORA HORA HORA
  pixels[179] = color_reloj_horas_inactivas                                     # LED 183
  pixels[0] = color_reloj_horas_inactivas
  pixels[1] = color_reloj_horas_inactivas
  for i in range(1,12):
    pixels[15*i-1] = color_reloj_horas_inactivas
    pixels[15*i] = color_reloj_horas_inactivas
    pixels[15*i+1] = color_reloj_horas_inactivas
  if(RTC().datetime()[6]==0):
    print(f"Desplegada la hora: {RTC().datetime()[4]}:{RTC().datetime()[5]}:{RTC().datetime()[6]}")

#-------------------------------------------------------------------------------
def desplegarHoraHora():
#-------------------------------------------------------------------------------
  hora = RTC().datetime()[4]
  if(hora>=12):
    hora -= 12
  ledHoraActual = map(3600 * hora + 60 * RTC().datetime()[5] + RTC().datetime()[6], 0, 43200, 0, NUMERO_LEDS_SOLO_ARO) + 1;

  # Asegurar que los índices estén dentro del rango circular (0-119)
  indice1 = (ledHoraActual - 1) % NUMERO_LEDs_RELOJ
  indice2 = ledHoraActual % NUMERO_LEDs_RELOJ
  indice3 = (ledHoraActual + 1) % NUMERO_LEDs_RELOJ

  pixels[indice1] = color_reloj_hora_activa
  pixels[indice2] = color_reloj_hora_activa
  pixels[indice3] = color_reloj_hora_activa

  pixels[LEDs_HORA*redActiva + 2] = (1,1,1)

#-------------------------------------------------------------------------------
def map(x, in_min, in_max, out_min, out_max):
#-------------------------------------------------------------------------------
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min;

#-------------------------------------------------------------------------------
def desplegarImagen():
#-------------------------------------------------------------------------------
  for i in range(NUMERO_FILAS_PANTALLA):
    for j in range(NUMERO_COLUMNAS_PANTALLA):
      #print("Pantalla:",NUMERO_FILAS_PANTALLA*(NUMERO_COLUMNAS_PANTALLA-i)-j-1,"Archivo;",NUMERO_FILAS_PANTALLA*i+j)
      pixelsPantalla[NUMERO_FILAS_PANTALLA*(NUMERO_COLUMNAS_PANTALLA-i)-j-1] = LOGO_ELECTRONICA_RGB[NUMERO_FILAS_PANTALLA*i+j]
  pixelsPantalla.write()

#-------------------------------------------------------------------------------
def desplegarHoraMinuto():
#-------------------------------------------------------------------------------
  ledMinutoActual = RTC().datetime()[5] * LEDs_MINUTO
  pixels[ledMinutoActual-1] = color_reloj_minuto_activo
  pixels[ledMinutoActual] = color_reloj_minuto_activo

#-------------------------------------------------------------------------------
def desplegarHoraSegundo():
#-------------------------------------------------------------------------------
  ledSegundoActual = RTC().datetime()[6] * LEDs_MINUTO
  pixels[ledSegundoActual] = color_reloj_segundo_activo

#///////////////////////////////////////////////////////////////////////////////
#/                              LUCES NAVIDEÑAS                               //
#///////////////////////////////////////////////////////////////////////////////
def desplegar_luces_navidenas():

  if (opcion_seleccionada_azar==1):                                            # PINO NAVIDEÑO
    # Semicirculo izquierdo (Copa) (de 9PM a 12PM)
    base_inicio = int(NUMERO_LEDS_SOLO_ARO * 0.70)
    base_fin = NUMERO_LEDS_SOLO_ARO
    for i in range(base_inicio, base_fin):
      intensidad = 100 + int(50 * math.sin(i * 0.2))
      pixels[i] = (0, intensidad, 0)

    # Semicirculo derecho (Copa) (12PM a 3PM)
    base_inicio = 0
    base_fin = int(NUMERO_LEDS_SOLO_ARO * 0.3)
    for i in range(0, int(NUMERO_LEDS_SOLO_ARO * 0.3)):
      intensidad = 100 + int(50 * math.sin(i * 0.2))
      pixels[i] = (0, intensidad, 0)

    # Línea vertical izquierda
    for i in range(LINEA_IZQUIERDA_ABAJO, LINEA_IZQUIERDA_ARRIBA+1):
      if (i>LINEA_IZQUIERDA_ABAJO+int((LINEA_IZQUIERDA_ARRIBA-LINEA_IZQUIERDA_ABAJO)*0.27)):
        intensidad = 100 + int(50 * math.sin(i * 0.2))
        pixels[i] = (0, intensidad, 0)
      else:
        pixels[i] = MARRON

    # Línea vertical derecha
    for i in range(LINEA_DERECHA_ARRIBA, LINEA_DERECHA_ABAJO+1):
      if (i<LINEA_DERECHA_ARRIBA+int((LINEA_DERECHA_ABAJO-LINEA_DERECHA_ARRIBA)*0.7)):
        intensidad = 100 + int(50 * math.sin(i * 0.2))
        pixels[i] = (0, intensidad, 0)
      else:
        pixels[i] = MARRON
        
    # DECORACIONES EN LA COPA DEL ARBOL
    # semicírculo izquierdo
    base_inicio = int(NUMERO_LEDS_SOLO_ARO * 0.70)
    base_fin = NUMERO_LEDS_SOLO_ARO
    for _ in range(12):
      posicion = random.randint(base_inicio, base_fin - 1)
      color = random.choice([ROJO, BLANCO, DORADO, AZUL, AMARILLO])
      pixels[posicion] = color
    # Línea vertical izquierda
    base_inicio = LINEA_IZQUIERDA_ABAJO + int((LINEA_IZQUIERDA_ARRIBA - LINEA_IZQUIERDA_ABAJO) * 0.27)
    base_fin = LINEA_IZQUIERDA_ARRIBA
    for _ in range(8):
      posicion = random.randint(base_inicio+1, base_fin - 1)
      color = random.choice([ROJO, BLANCO, DORADO, AZUL, AMARILLO])
      pixels[posicion] = color
    # Línea vertical derecha
    base_inicio = LINEA_DERECHA_ARRIBA + int((LINEA_DERECHA_ABAJO - LINEA_DERECHA_ARRIBA) * 0.73)
    base_fin = LINEA_DERECHA_ARRIBA
    for _ in range(8):
      posicion = random.randint(base_fin-1, base_inicio - 2)
      color = random.choice([ROJO, BLANCO, DORADO, AZUL, AMARILLO])
      pixels[posicion] = color
    # semicírculo derecho
    base_inicio = 0
    base_fin = int(NUMERO_LEDS_SOLO_ARO * 0.3)
    for _ in range(12):
      posicion = random.randint(base_inicio, base_fin - 1)
      color = random.choice([ROJO, BLANCO, DORADO, AZUL, AMARILLO])
      pixels[posicion] = color

    # Estrella en la parte superior (12 PM)
    pixels[NUMERO_LEDS_SOLO_ARO-1] = DORADO
    pixels[0] = DORADO
    pixels[1] = DORADO

    pixels.write()

  elif (opcion_seleccionada_azar==2):                                          # COPOS DE NIEVE
    apagar_todos_leds()
    for _ in range(DENSIDAD_COPOS_NIEVE):
      led = random.randint(0, NUMERO_LEDs_RELOJ - 1)
      intensidad = random.randint(50, 200)
      pixels[led] = (intensidad, intensidad, intensidad)

    pixels.write()

  elif (opcion_seleccionada_azar==3):                                          # ROTACION NAVIDADCOLORES NAVIDEÑOS
    """Rotación de colores navideños en círculo - SOLO CÍRCULO"""
    global offset

    offset = (offset + 1) % NUMERO_LEDS_SOLO_ARO
        
    for i in range(0, NUMERO_LEDS_SOLO_ARO):
      pos_circulo = i
      pos = (pos_circulo - offset) % NUMERO_LEDS_SOLO_ARO
      if pos % 4 == 0:
        pixels[i] = VERDE
      elif pos % 4 == 1:
        pixels[i] = BLANCO
      elif pos % 4 == 2:
        pixels[i] = ROJO
      else:
        pixels[i] = DORADO
        
    pixels.write()

#-------------------------------------------------------------------------------
def apagar_todos_leds():
#-------------------------------------------------------------------------------
  for i in range(NUMERO_LEDs_RELOJ):
    pixels[i] = (0, 0, 0)
  pixels.write()

#///////////////////////////////////////////////////////////////////////////////
#/ PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO        //
#///////////////////////////////////////////////////////////////////////////////
#-------------------------------------------------------------------------------
def proceso():
#-------------------------------------------------------------------------------
  pass

print("Versión del programa: 1")

# import os
# stats = os.stat('AroITSTA.py')
# print(f"El sketch ocupa: {stats[6]} bytes")
# print(f"Memoria libre: {gc.mem_free()} bytes")

seleccionarMejorRedWiFiDisponible()
print("Connecting to WiFi network '{}'".format(SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# Configurar IP FIJA
if(SSID=="TP-Link_LMario_DHCP"):
  IP_FIJA = "192.168.0.51"
  MASCARA = "255.255.255.0"
  GATEWAY = "192.168.0.1"
  DNS = "192.168.0.1"
  wifi.ifconfig((IP_FIJA, MASCARA, GATEWAY, DNS))
  print(f"Conectando a WiFi con IP fija: {IP_FIJA}", end="")

wifi.connect(SSID,PASSWD)
while not wifi.isconnected():
  time.sleep(5)
  if (WATCHDOG):
    wdt.feed()
  print('WiFi connect retry ...')

if wifi.isconnected():
  print("\n✅ Conectado a WiFi")
  config = wifi.ifconfig()
  print(f"📡 IP asignada: {config[0]}")
  print(f"   Máscara: {config[1]}")
  print(f"   Gateway: {config[2]}")
  print(f"   DNS: {config[3]}")

  # Verificar que se asignó la IP fija
  if config[0] != IP_FIJA:
    print(f"⚠️ Advertencia: IP asignada ({config[0]}) diferente a IP \
         fija ({IP_FIJA})")
    print("   Posible conflicto - prueba con otra IP")
else:
  print("\n❌ No se pudo conectar a WiFi")

actualizarSketch()

desplegarImagen()

print("Connecting to Blynk server...")
blynk = BlynkLib_deepseek.Blynk(BLYNK_AUTH)

# Create BlynkTimer Instance
timer = BlynkTimer()

#///////////////////////////////////////////////////////////////////////////////
#/                               FUNCIONES BLYNK
#///////////////////////////////////////////////////////////////////////////////
@blynk.on("connected")
#-------------------------------------------------------------------------------
def blynk_connected(ping):
#-------------------------------------------------------------------------------
  blynk.sync_virtual(0,1)
  desplegarMensajeVisual(3)
  print('Blynk ready. Ping:', ping, 'ms')
  blynk.send_internal("utc","time")
  print('RTC sync request was sent')

@blynk.on("disconnected")
#-------------------------------------------------------------------------------
def blynk_disconnected():
#-------------------------------------------------------------------------------
  print('Blynk disconnected')

@blynk.on("internal:utc")
#-------------------------------------------------------------------------------
def on_utc(value):
#-------------------------------------------------------------------------------
  global tiempoLocal,banderaHoraRecuperadaBlynk

  if value[0] == "time":
    ts = int(value[1])//1000
    tiempoLocal = time.localtime(ts)
    print("Tiempo UTC:", tiempoLocal)
    # Año[0], mes[1] (1-12), día del mes[2] (1-31), hora[3] (0-23), minuto[4] (0-59), segundo[5] (0-59), día de
    # la semana[6] (0-6 de lunes a domingo), día de año[7] (1-366)
    # SINCRONIZACIÓN DEL RELOJ INTERNO E IMPRESIÓN DE FECHA Y HORA
    #RTC().init((year, month, mday, hour, minute, second, microsecond (no utilizada),tzinfo (no utilizada)))
    RTC().init((tiempoLocal[0]-30, tiempoLocal[1], tiempoLocal[2], tiempoLocal[3]+ZONA_MEXICO, tiempoLocal[4], \
                tiempoLocal[5], 0, 0))
    print("Hora RTC:",RTC().datetime())
    print ("Fecha: {:02d}/{:02d}/{}".format(RTC().datetime()[2],
                                        RTC().datetime()[1],
                                        RTC().datetime()[0]))
    print ("Hora: {:02d}:{:02d}:{:02d}".format(RTC().datetime()[4],
                                           RTC().datetime()[5],
                                           RTC().datetime()[6]))

  #elif value[0] == "tz_name":
    #print("Timezone: ", value[1])


  banderaHoraRecuperadaBlynk=True

@blynk.on("V0")
def v0_write_handler_modo(value):
  global paletaColores
  global color_reloj_horas_inactivas,color_reloj_minutos_inactivos
  global color_reloj_hora_activa,color_reloj_minuto_activo,color_reloj_segundo_activo
  paletaColores = int(value[0])
  print('Nuevo valor para la variable diseño (V0):',paletaColores)

  if(paletaColores==3):
    paletaColores = random.randint(0,NUMERO_PALETAS_COLORES-2)

  if(paletaColores==0):
    color_reloj_horas_inactivas=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_HORAS_INACTIVAS_FASCINACION)
    color_reloj_horas_inactivas = tuple(int(d+0.5) for d in color_reloj_horas_inactivas)
    color_reloj_minutos_inactivos=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_MINUTOS_INACTIVOS_FASCINACION)
    color_reloj_minutos_inactivos = tuple(int(d+0.5) for d in color_reloj_minutos_inactivos)
    color_reloj_hora_activa=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_HORA_ACTIVA_FASCINACION)
    color_reloj_hora_activa = tuple(int(d+0.5) for d in color_reloj_hora_activa)
    color_reloj_minuto_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_MINUTO_ACTIVO_FASCINACION)
    color_reloj_minuto_activo = tuple(int(d+0.5) for d in color_reloj_minuto_activo)
    color_reloj_segundo_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_SEGUNDO_ACTIVO_FASCINACION)
    color_reloj_segundo_activo = tuple(int(d+0.5) for d in color_reloj_segundo_activo)
  elif(paletaColores==1):
    color_reloj_horas_inactivas=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_HORAS_INACTIVAS_NEBULA)
    color_reloj_horas_inactivas = tuple(int(d+0.5) for d in color_reloj_horas_inactivas)
    color_reloj_minutos_inactivos=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_MINUTOS_INACTIVOS_NEBULA)
    color_reloj_minutos_inactivos = tuple(int(d+0.5) for d in color_reloj_minutos_inactivos)
    color_reloj_hora_activa=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_HORA_ACTIVA_NEBULA)
    color_reloj_hora_activa = tuple(int(d+0.5) for d in color_reloj_hora_activa)
    color_reloj_minuto_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_MINUTO_ACTIVO_NEBULA)
    color_reloj_minuto_activo = tuple(int(d+0.5) for d in color_reloj_minuto_activo)
    color_reloj_segundo_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_SEGUNDO_ACTIVO_NEBULA)
    color_reloj_segundo_activo = tuple(int(d+0.5) for d in color_reloj_segundo_activo)
  elif(paletaColores==2):
    color_reloj_horas_inactivas=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_HORAS_INACTIVAS_MINIMALISTA)
    color_reloj_horas_inactivas = tuple(int(d+0.5) for d in color_reloj_horas_inactivas)
    color_reloj_minutos_inactivos=tuple(c*factor_ajuste_brillo_inactivos for c in COLOR_RELOJ_MINUTOS_INACTIVOS_MINIMALISTA)
    color_reloj_minutos_inactivos = tuple(int(d+0.5) for d in color_reloj_minutos_inactivos)
    color_reloj_hora_activa=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_HORA_ACTIVA_MINIMALISTA)
    color_reloj_hora_activa = tuple(int(d+0.5) for d in color_reloj_hora_activa)
    color_reloj_minuto_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_MINUTO_ACTIVO_MINIMALISTA)
    color_reloj_minuto_activo = tuple(int(d+0.5) for d in color_reloj_minuto_activo)
    color_reloj_segundo_activo=tuple(c*factor_ajuste_brillo_activos for c in COLOR_RELOJ_SEGUNDO_ACTIVO_MINIMALISTA)
    color_reloj_segundo_activo = tuple(int(d+0.5) for d in color_reloj_segundo_activo)

  #print(color_reloj_horas_inactivas,color_reloj_minutos_inactivos)
  #print(color_reloj_hora_activa,color_reloj_minuto_activo,color_reloj_minuto_activo)

@blynk.on("V1")
def v1_write_handler_modo(value):
  global brillo

  brillo = float(value[0])

  print('Nuevo valor para la variable brillo (V1):',brillo)

#///////////////////////////////////////////////////////////////////////////////
#/                             FIN FUNCIONES BLYNK
#///////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////
#/                                   TIMERS
#///////////////////////////////////////////////////////////////////////////////
#timerReloj=timer.set_interval(1,actualizarHora)
#timer.set_interval(60,actualizarSketch)
#///////////////////////////////////////////////////////////////////////////////
#/                                FIN DE TIMERS
#///////////////////////////////////////////////////////////////////////////////
def proceso2():
  pass

diaInicial=RTC().datetime()[2]
opcionSeleccionadaAzar=0
random.seed()
banderaAnimacionEstablecida=False
banderaReloj = True

while not banderaHoraRecuperadaBlynk:
  blynk.run()
  timer.run()
# blynk.disconnect()
# wifi.disconnect()
# time.sleep(1)
# if not wifi.isconnected():
#   print("Desconectado de Blynk y WiFi")
# else:
#   print("WiFi connected. Can't disconnect")

# CICLO INFINITO EN ESPERA POR EVENTOS
hora_inicial_tarea=time.ticks_ms()-1000
while True:

  blynk.run()
  timer.run()

  try:
    # Posiciones en RTC(): 0. Año; 1: Mes; 2: Día; 4: Hora; 5: Minuto; 6: Segundo
    if (RTC().datetime()[2]!=diaInicial):                                       # Actualizar día
      bandera_animacion_iniciada=False
      opcion_seleccionada_azar=0
      diaInicial = RTC().datetime()[2]

    if (RTC().datetime()[1]==9):                                                # Septiembre
      if (RTC().datetime()[5]%5!=0):
        if (not bandera_reloj):
          #timerReloj = timer.set_interval(1,actualizarHora)
          bandera_reloj = True
          bandera_animacion_iniciada = False
      else:
        if (not bandera_animacion_iniciada):
          #timer._delete(timerReloj)
          #print("Timer del reloj borrado")
          bandera_reloj = False
          if (opcion_seleccionada_azar==0):
            opcion_seleccionada_azar = random.randint(1,1)
          if (opcion_seleccionada_azar==1):
            bandera()
          bandera_animacion_iniciada = True
    elif (RTC().datetime()[1]==12):                                              # Diciembre|Enero
      if (RTC().datetime()[5]%2!=0):
        if (not bandera_reloj):                                                  # Reloj
          #timerReloj = timer.set_interval(1,actualizarHora)
          bandera_reloj = True
          bandera_animacion_iniciada = False
          print("Desplegando la hora")
        if(time.ticks_ms()-hora_inicial_tarea>1000):
          actualizarHora()
          hora_inicial_tarea = time.ticks_ms()
      else:                                                                    # Animaciones Navideñas
        if (not bandera_animacion_iniciada):
          bandera_reloj = False
          opcion_seleccionada_azar = random.randint(1,3)
          while(not BANDERA_ANIMACION_ACTIVA[opcion_seleccionada_azar-1]):
            opcion_seleccionada_azar = random.randint(1,3)
          apagar_todos_leds()
          hora_inicial_tarea = time.ticks_ms()
          hora_inicial_tick = time.ticks_ms()
          print("Desplegando animaciones navideñas (efecto:",opcion_seleccionada_azar,")")
          if(opcion_seleccionada_azar==1 or opcion_seleccionada_azar==2):
            pass
          elif(opcion_seleccionada_azar==3):
            offset = 0
          desplegar_luces_navidenas()
          bandera_animacion_iniciada = True
        else:
          if(opcion_seleccionada_azar==1 or opcion_seleccionada_azar==2):
            if(time.ticks_ms()-hora_inicial_tick>INTERVALO_BASE_ENTRE_TICKS):
              desplegar_luces_navidenas()
              hora_inicial_tick = time.ticks_ms()
          elif(opcion_seleccionada_azar==3):
            if(time.ticks_ms()-hora_inicial_tick>50):
              desplegar_luces_navidenas()
              hora_inicial_tick = time.ticks_ms()
    else:                                                                       # Otros meses (sólo reloj)
      if(time.ticks_ms()-hora_inicial_tarea>1000):
        actualizarHora()
        hora_inicial_tarea = time.ticks_ms()

  except KeyboardInterrupt:
    print("Deteniendo programa...")
    apagar_todos_leds()
    wifi.disconnect()
    time.sleep(1)
    if not wifi.isconnected():
      print("Desconectado de Blynk y WiFi")
    else:
      print("WiFi connected. Can't disconnect")
    break

  if (WATCHDOG):
    wdt.feed()

#///////////////////////////////////////////////////////////////////////////////
#/ PROVISIONAL   PROVISIONAL   PROVISIONAL   PROVISIONAL   PROVISIONAL        //
#///////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////
#/ FIN PROVISIONAL
#///////////////////////////////////////////////////////////////////////////////
