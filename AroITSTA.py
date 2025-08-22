# NOTAS:

# 1) Las posiciones de los LEDs son:
#    Circunferencia: 1-180 (0-179)
#    Linea izquierda: 184-237 (183-236)
#    Linea izquierda: 238-291 (237-290)

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

# 5) Pasos para borra el contenido del ESP32 (si no se puede con Thonny)
#    (https://randomnerdtutorials.com/esp32-erase-flash-memory/)

#    a) Instalar:

#      sudo pip install esptool
#      sudo pip install setuptools

#    a) Correr:

#       python3 esptool --chip esp32 erase_flash

import machine
from machine import Pin
import neopixel
import time

import BlynkLib     # https://github.com/vshymanskyy/blynk-library-python/blob/master/examples/03_sync_virtual.py
from BlynkTimer_lmms import BlynkTimer
import network
from ota_lmms import OTAUpdater
import random

from machine import WDT

#///////////////////////////////////////////////////////////////////////////////
#/                               CONSTANTES                                   //
#///////////////////////////////////////////////////////////////////////////////
WIFI_SSID = ['INFINITUM2426_2.4','Electronica Hotspot PC','TP-Link_lmmsegura']
WIFI_PASS = ['CNnC917MDE','electronica23','lmario28']
SSID=''
PASSWD=''
BLYNK_AUTH = 'apvVB1KTve_HC0uEb8ltb7tME6GhWIBs'

NUMERO_LEDs_RELOJ=284
NUMERO_LEDS_SOLO_ARO=180                                                       # 6. Navidad 1, 7. Navidad 2
NUMERO_LEDs_PANTALLA=576                                                       # Filas: 24, Columnas: 24
PERIODO_FLASH_LED=1000
LEDs_HORA=15
LEDs_MINUTO=3
# 16,15,15,15,15,15,15,15,15,15,15,17 LEDs
#define NUMERO_INTENTOS 5

#define MAXIMUN_RETRIES_TO_CONNECT_BLYNK 20                                    //
#define MAXIMUN_ATTEMPTS_TO_RECONNECT_WIFI 18                                  // Intentos maximos para conectarse a la red WiFi
#define TIEMPO_ESPERA_RECONECTAR_BLYNK 30000L                                  // Tiempo de espera par intentar reconectare a Blynk (milliseconds)

# ANIMACIONES
NUMERO_ANIMACIONES=14
#                             RGB Loop      Fade In-Out      Strobe       Halloween Eyes  Cylon Bounce
BANDERA_ANIMACION_ACTIVA = [   False,         False,          False,           False,          False,     \
#                             New KITT       Twinkle     Twinkle Random      Sparkle      Snow Sparkle
#                             (Navidad)                     (Navidad)                       (Navidad)
                               True,          False,          True,           False,          True,      \
#                           Running Lights  Color Wipe    Rainbow Cycle    Theater Chase
#                             (Navidad)                     (Navidad)        (Navidad)
                               True,          False,          True,           True                       \
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

#///////////////////////////////////////////////////////////////////////////////
#/                               OBJETOS                                    //
#///////////////////////////////////////////////////////////////////////////////
led = machine.Pin(2,machine.Pin.OUT)
pixels = neopixel.NeoPixel(Pin(16, Pin.OUT), NUMERO_LEDs_RELOJ)
pixelPantalla = neopixel.NeoPixel(Pin(17, Pin.OUT), NUMERO_LEDs_PANTALLA)
from machine import RTC
(year, month, mday, weekday, hour, minute, second, milisecond)=RTC().datetime()                
if (WATCHDOG):
  wdt = WDT(timeout = 30000)

#///////////////////////////////////////////////////////////////////////////////
#/                               VARIABLES                                    //
#///////////////////////////////////////////////////////////////////////////////
tiempoLocal=''
banderaSalida=False
redActiva=0
fechaHoraInicio=''
ahorita=''
diaInicial=''
#timerReloj=''
banderaHoraRecuperadaBlynk=False
opcionSeleccionadaAzar=0
i=1
j=1
k=0
incrementoDecremento=1
contadorAnimaciones=0

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
#   for (ssid, bssid, channel, RSSI, authmode, hidden) in redesWiFiDisponibles:
#     print("* {:s}".format(ssid))
#     print("   - Auth: {} {}".format(authmodes[authmode], '(hidden)' if hidden else ''))
#     print("   - Channel: {}".format(channel))
#     print("   - RSSI: {}".format(RSSI))
#     print("   - BSSID: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*bssid))
#     print()

  rssiMasFuerte = 999
  for redWiFi in redesWiFiDisponibles:
    #print ("> " + str(redWiFi[0],"utf-8"))
    #print ("> " + str(redWiFi[3]))
    ssid = str(redWiFi[0],"utf-8")
    try:
      indiceRed = WIFI_SSID.index(ssid)
    except ValueError:
      continue

    SSID = ssid
    PASSWD = WIFI_PASS[indiceRed]
    redActiva = indiceRed + 1
      
    if rssiMasFuerte!=999:
      rssi = str(redWiFi[3])
      if rssi<rssiMasFuerte:
        rssiMasFuerte = rssi
    print("Mejor red disponible:",redActiva,"|",SSID,"|",PASSWD)

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
      pixels.fill((0,10,0))
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
  # Inicio del ciclo infinito
  elif(tipLla==4):
    for i in range(1):
      pixels.fill((255,255,0))
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
  print("pixeles[0]:",pixels[0])
  pixels.fill((255,0,0))
  pixels.write()
  print(" pixeles[0]:",pixels[0])

#-------------------------------------------------------------------------------
def desplegarEsqueleto():
#-------------------------------------------------------------------------------
  # MINUTO MINUTO MINUTO
  for i in range(60):
    pixels[3*i] = (0,2,0)

  # HORA HORA HORA
  pixels[182] = (5,0,5)                                                         # LED 183
  pixels[0] = (5,0,5)
  pixels[1] = (5,0,5)
  for i in range(11):
    pixels[15*i-1] = (5,0,5)
    pixels[15*i] = (5,0,5)
    pixels[15*i+1] = (5,0,5)

#-------------------------------------------------------------------------------
def desplegarHoraHora():
#-------------------------------------------------------------------------------
  hora = RTC().datetime()[4]
  if(hora>=12):
    hora -= 12
  ledHoraActual = map(3600 * hora + 60 * RTC().datetime()[5] + RTC().datetime()[6], 0, \
                      43200, 0, NUMERO_LEDS_SOLO_ARO) + 1;
  pixels[ledHoraActual-1] = (255,0,0)
  pixels[ledHoraActual] = (255,0,0)
  pixels[ledHoraActual+1] = (255,0,0)

  pixels[LEDs_HORA*redActiva + 2] = (1,1,1)

#-------------------------------------------------------------------------------
def map(x, in_min, in_max, out_min, out_max):
#-------------------------------------------------------------------------------
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min;

def desplegarImagen():
  rojo=random.randint(0,255)
  verde=random.randint(0,255)
  azul=random.randint(0,255)
  for i in range(NUMERO_LEDs_PANTALLA):
    pixelPantalla[i] = (rojo,verde,azul)
  print(rojo,"  ",verde,"   ",azul)

#-------------------------------------------------------------------------------
def desplegarHoraMinuto():
#-------------------------------------------------------------------------------
  ledMinutoActual = RTC().datetime()[5] * LEDs_MINUTO
  pixels[ledMinutoActual-1] = (0,255,0)
  pixels[ledMinutoActual] = (0,255,0)

#-------------------------------------------------------------------------------
def desplegarHoraSegundo():
#-------------------------------------------------------------------------------
  ledSegundoActual = RTC().datetime()[6] * LEDs_MINUTO
  pixels[ledSegundoActual] = (255,255,0)
  #if(ledSegundoActual==0):
   #desplegarImagen()

#///////////////////////////////////////////////////////////////////////////////
#/ PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO   PROCESO        //
#///////////////////////////////////////////////////////////////////////////////
def proceso():
  pass

seleccionarMejorRedWiFiDisponible()
print("Connecting to WiFi network '{}'".format(SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID,PASSWD)
while not wifi.isconnected():
  desplegarMensajeVisual(1)
  time.sleep(5)
  if (WATCHDOG):
    wdt.feed()
  print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])
desplegarMensajeVisual(2)
actualizarSketch()

print("Connecting to Blynk server...")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Create BlynkTimer Instance
timer = BlynkTimer()

#///////////////////////////////////////////////////////////////////////////////
#/                               FUNCIONES BLYNK
#///////////////////////////////////////////////////////////////////////////////
@blynk.on("connected")
def blynk_connected(ping):
  desplegarMensajeVisual(3)
  print('Blynk ready. Ping:', ping, 'ms')
  blynk.send_internal("utc","time")
  print('RTC sync request was sent')

@blynk.on("disconnected")
def blynk_disconnected():
    print('Blynk disconnected')
banderaSalida=False

@blynk.on("internal:utc")
def on_utc(value):
  global tiempoLocal,banderaHoraRecuperadaBlynk

  if value[0] == "time":
    ts = int(value[1])//1000
    # on embedded systems, you may need to subtract time difference between 1970 and 2000
    ts -= 946684800
    # Ajuste por zona
    ts += 3600 * ZONA_MEXICO
    tiempoLocal = time.localtime(ts)
    # Año, mes (1-12), día del mes (1-31), hora (0-23), minuto (0-59), segundo (0-59), día de
    # la semana (0-6 de lunes a domingo), día de año (1-366)
    # SINCRONIZACIÓN DEL RELOJ INTERNO E IMPRESIÓN DE FECHA Y HORA
    #RTC().init((year, month, mday, weekday, hour, minute, second, milisecond))
    RTC().init((tiempoLocal[0], tiempoLocal[1], tiempoLocal[2], tiempoLocal[6], tiempoLocal[3], \
                tiempoLocal[4], tiempoLocal[5], milisecond))
    print ("Fecha: {:02d}/{:02d}/{}".format(RTC().datetime()[2],
                                        RTC().datetime()[1],
                                        RTC().datetime()[0]))
    print ("Hora: {:02d}:{:02d}:{:02d}".format(RTC().datetime()[4],
                                           RTC().datetime()[5],
                                           RTC().datetime()[6]))

  #elif value[0] == "tz_name":
    #print("Timezone: ", value[1])

  banderaHoraRecuperadaBlynk=True

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

#HOLA
for i in range(3):
  led.off()
  time.sleep_ms(250)
  led.on()
  time.sleep_ms(250)
led.off()

diaInicial=RTC().datetime()[2]
opcionSeleccionadaAzar=0
random.seed()
banderaAnimacionEstablecida=False
banderaReloj = True

while not banderaHoraRecuperadaBlynk:
  blynk.run()
  timer.run()
blynk.disconnect()
wifi.disconnect()
time.sleep(1)
if not wifi.isconnected():
  print("Desconectado de Blynk y WiFi")
else:
  print("WiFi connected. Can't disconnect")

# CICLO INFINITO EN ESPERA POR EVENTOS
print("Bandera reloj",banderaReloj)
horaInicial=time.ticks_ms()-1000
print("Hora inicial en milisegundos",horaInicial)
desplegarMensajeVisual(4)
while banderaSalida==False:
  try:
    # Posiciones en RTC(): 0. Año; 1: Mes; 2: Día; 4: Hora; 5: Minuto; 6: Segundo
    if (RTC().datetime()[2]!=diaInicial):
      banderaAnimacionEstablecida=false
      opcionSeleccionadaAzar=0
      diaInicial = RTC().datetime()[2]

    if (RTC().datetime()[1]==9):                                                # Septiembre
      if (RTC().datetime()[5]%5!=0):
        if (not banderaReloj):
          #timerReloj = timer.set_interval(1,actualizarHora)
          banderaReloj = True
          banderaAnimacionEstablecida = False
      else:
        if (not banderaAnimacionEstablecida):
          #timer._delete(timerReloj)
          #print("Timer del reloj borrado")
          banderaReloj = False
          if (opcionSeleccionadaAzar==0):
            opcionSeleccionadaAzar = random.randint(1,1)
          if (opcionSeleccionadaAzar==1):
            bandera()
          banderaAnimacionEstablecida = True
    elif (RTC().datetime()[1]==12):                                            # Diciembre
    #elif (RTC().datetime()[1]==11 and RTC().datetime()[2]==29):                   # Pruebas
      if (RTC().datetime()[5]%3!=0):
        if (not banderaReloj):
          #timerReloj = timer.set_interval(1,actualizarHora)
          banderaReloj = True
          banderaAnimacionEstablecida = False
        if(time.ticks_ms()>horaInicial):
          actualizarHora()
          horaInicial = time.ticks_ms()
      else:
        if (not banderaAnimacionEstablecida):
          banderaReloj = False
          opcionSeleccionadaAzar = random.randint(6,6)
          while(not BANDERA_ANIMACION_ACTIVA[opcionSeleccionadaAzar-1]):
            opcionSeleccionadaAzar = random.randint(6,6)
          #print("opcionSeleccionadaAzar:",opcionSeleccionadaAzar)
          if(opcionSeleccionadaAzar==1 or opcionSeleccionadaAzar==2):
            j = 0
            k = 0
            incrementoDecremento = 1
            contadorAnimaciones = 0
          elif(opcionSeleccionadaAzar==3):
            j = 0
          elif(opcionSeleccionadaAzar==6):
            i = 1
            j = NUMERO_LEDS_SOLO_ARO - NEWKITT_TAMANO_OJO - 2
          horaInicial=time.ticks_ms()
          banderaAnimacionEstablecida = True
        else:
          if (opcionSeleccionadaAzar==0):
            opcionSeleccionadaAzar = random.randint(1,3)
            while(BANDERA_ANIMACION_ACTIVA[opcionSeleccionadaAzar-1]):
              opcionSeleccionadaAzar = random.randint(1,3)
            print("opcionSeleccionadaAzar:",opcionSeleccionadaAzar)
          lucesDecembrinas(opcionSeleccionadaAzar)
    else:                                                                       # Otros meses
      if(time.ticks_ms()-horaInicial>1000):
        actualizarHora()
        horaInicial = time.ticks_ms()
#         else:
#           fuegosArtificiales()
#     elif mes==12 or mes == 1:
#       if (opcionSeleccionadaAzar==0):
#         opcionSeleccionadaAzar = random(1,3)
#     }
#     if (opcionSeleccionadaAzar == 1)
#     {
#       if (!banderaAnimacionEstablecida)
#       {
#         bandera();
#         banderaAnimacionEstablecida = true;
#       }
#     }
#     else
#       fuegosArtificiales();
#   }
#   else
#     desplegarHora();
# 
#   // Esperar que pase 1 segundo
#   while (segundo == segundoAnterior)
#     segundo = second();
#   segundoAnterior = segundo;
# }
  except KeyboardInterrupt:
    banderaSalida = True

  if (WATCHDOG):
    wdt.feed()

#ADIOS
for i in range(2):
  led.off()
  time.sleep_ms(250)
  led.on()
  time.sleep_ms(250)
led.off()

print("Programa terminado")

#///////////////////////////////////////////////////////////////////////////////
#/ PROVISIONAL   PROVISIONAL   PROVISIONAL   PROVISIONAL   PROVISIONAL        //
#///////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////
#/ FIN PROVISIONAL
#///////////////////////////////////////////////////////////////////////////////
