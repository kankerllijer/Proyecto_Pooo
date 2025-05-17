
"""Paquete para gestión de cumpleaños.

Módulos:
    contacto: Define la estructura de datos para contactos.
    gestor_cumpleaños: Lógica de negocio para manejar fechas y almacenamiento.
    enviar_correos: Funcionalidad de envío de correos electrónicos.
"""

from .contacto import Contacto
from .gestor_cumpleaños import GestorCumpleaños
from .enviar_correos import EnviarCorreos

__all__ = ["Contacto", "GestorCumpleaños", "EnviarCorreos"]
