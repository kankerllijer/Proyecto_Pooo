
import csv
from datetime import datetime
from typing import List
from .contacto import Contacto
from abc import ABC, abstractmethod

class Almacenamiento(ABC):
    """Interfaz para estrategias de almacenamiento."""

    @abstractmethod
    def cargar_contactos(self) -> List[Contacto]:

        """Carga todos los contactos desde el almacenamiento.

        Returns:
            List[Contacto]: Lista de contactos recuperados.
            Lista vacía si no hay datos o hay error.
        """

        pass

    @abstractmethod
    def guardar_contactos(self, contactos: List[Contacto]):

        """Persiste la lista completa de contactos.

        Args:
            contactos: Lista de objetos Contacto a guardar.
        """

        pass

class AlmacenamientoCSV(Almacenamiento):
    """Implementación concreta de almacenamiento en archivo CSV.

    Args:
        archivo: Ruta del archivo CSV. Por defecto: 'contactos.csv'.
    """

    def __init__(self, archivo: str = "contactos.csv"):
        self.archivo = archivo

    def cargar_contactos(self) -> List[Contacto]:
        try:
            with open(self.archivo, 'r') as f:
                return [
                    Contacto(
                        fila['nombre'],
                        datetime.strptime(fila['fecha_nacimiento'], '%Y-%m-%d').date(),
                        fila['correo']
                    ) for fila in csv.DictReader(f)
                ]
        except FileNotFoundError:
            return []

    def guardar_contactos(self, contactos: List[Contacto]):
        with open(self.archivo, 'w', newline='') as f:
            escritor = csv.DictWriter(f, fieldnames=['nombre', 'fecha_nacimiento', 'correo'])
            escritor.writeheader()
            for contacto in contactos:
                escritor.writerow({
                    'nombre': contacto.nombre,
                    'fecha_nacimiento': contacto.fecha_nacimiento.strftime('%Y-%m-%d'),
                    'correo': contacto.correo
                })
