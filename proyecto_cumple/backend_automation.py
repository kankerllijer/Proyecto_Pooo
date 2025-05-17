#
#
import os
import logging
logging.basicConfig(filename="app.log", level=logging.INFO)
from datetime import datetime
import time
import schedule
import random
import csv
from datetime import date
import pytz

from gestor_cumpleaños.almacenamiento import AlmacenamientoCSV
from gestor_cumpleaños.gestor_cumpleaños import GestorCumpleaños
from gestor_cumpleaños.enviar_correos import EnviarCorreos

def obtener_fecha_actual():

     # Configuración dinámica de zona horaria para comparar fechas
     zona_horaria = pytz.timezone("America/Mexico_City")
     return datetime.now(zona_horaria).date()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def enviar_felicitaciones_automaticas():
     try:
         # Validar archivos esenciales
         if not all([os.path.exists("smtp_config.csv"), os.path.exists("mensajes.csv")]):
             print("Error: Archivos de configuración faltantes")
             return

         # Cargar configuración SMTP
         with open("smtp_config.csv", "r") as f:
             server, port, user, pwd = next(csv.reader(f))

         almacenamiento = AlmacenamientoCSV()
         gestor = GestorCumpleaños(almacenamiento)
         enviador = EnviarCorreos(server, int(port), user, pwd)

         # Cargar mensajes
         with open("mensajes.csv", "r") as f:
             mensajes = [line.strip() for line in f]
             if not mensajes:
                 print("Error: No hay mensajes en mensajes.csv")
             if not mensajes:
                print("Error: El archivo mensajes.csv está vacío")
                return

         # Verificar cumpleaños
         hoy = obtener_fecha_actual()
         for contacto in gestor.contactos:
             prox_cumple = gestor.obtener_proximo_cumpleaños(contacto)
             if prox_cumple == hoy:
                 mensaje = random.choice(mensajes).format(nombre=contacto.nombre)
                 if enviador.enviar_correo(contacto.correo, "🎉 ¡Feliz Cumpleaños!", mensaje):
                     logging.info(f"✅ Correo enviado a {contacto.nombre}")
                 else:
                     logging.error(f"🚨 Error crítico: {str(e)}")

     except FileNotFoundError as e:
            logging.critical(f"Archivo faltante: {str(e)}")
     except smtplib.SMTPException as e:
            logging.error(f"Fallo en SMTP: {str(e)}")


# Programar tarea
schedule.every().day.at("08:00").do(enviar_felicitaciones_automaticas)

if __name__ == "__main__":
     while True:
         schedule.run_pending()
         time.sleep(60)
