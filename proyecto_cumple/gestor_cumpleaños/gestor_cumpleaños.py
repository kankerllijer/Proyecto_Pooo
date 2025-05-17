
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Tuple
from .contacto import Contacto
from .almacenamiento import Almacenamiento

class GestorCumpleaños:

    """Maneja el almacenamiento y cálculo de fechas de cumpleaños.

    Responsable de:
    - Cargar/guardar contactos desde/hacia CSV
    - Calcular próximos cumpleaños
    - Ordenar eventos por proximidad
    """

    def __init__(self, almacenamiento: Almacenamiento):
        self.almacenamiento = almacenamiento
        self.contactos = self.almacenamiento.cargar_contactos()

    def agregar_contacto(self, contacto: Contacto):
        self.contactos.append(contacto)
        self.almacenamiento.guardar_contactos(self.contactos)

    def obtener_proximo_cumpleaños(self, contacto: Contacto) -> date:

        """Calcula la próxima fecha de cumpleaños para un contacto.
        Args:
            contacto (Contacto): Contacto para calcular su cumpleaños.
        Returns:
            date: Próxima fecha de cumpleaños ajustada al año actual.
        Nota:
            Maneja casos especiales como 29 de febrero, ajustando a 28/02 en años no bisiestos.
        """

        hoy = date.today()
        año_actual = hoy.year

        try:
            proximo_cumple = contacto.fecha_nacimiento.replace(year=año_actual)

            # Manejo especial para 29 de febrero
            if proximo_cumple.month == 2 and proximo_cumple.day == 29:
                # Ajustar a 28/02 si el año actual no es bisiesto
                if not self._es_año_bisiesto(año_actual):
                    proximo_cumple = date(año_actual, 3, 1)  # Mover a 1 de marzo
        except ValueError:
            proximo_cumple = date(año_actual, 3, 1)

        if proximo_cumple < hoy:
            proximo_cumple = proximo_cumple.replace(year=año_actual + 1)
            if proximo_cumple.month == 2 and proximo_cumple.day == 29:
                if not self._es_año_bisiesto(año_actual + 1):
                    proximo_cumple = date(año_actual + 1, 3, 1)

        return proximo_cumple

    def _es_año_bisiesto(self, año: int) -> bool:
        """Determina si un año es bisiesto según el calendario gregoriano.

        Args:
            año: Año a validar (entero positivo).

        Returns:
            bool: True si es bisiesto, False en caso contrario.
        """

        return año % 4 == 0 and (año % 100 != 0 or año % 400 == 0)


    def obtener_proximos_cumpleaños(self) -> List[Tuple[Contacto, int]]:

        """Genera lista de cumpleaños ordenados por proximidad.

        Returns:
            List[Tuple[Contacto, int]]: Lista de tuplas (Contacto, días restantes),
            ordenada ascendentemente por días.
        """

        hoy = date.today()
        proximos = []
        for contacto in self.contactos:
            proximo_cumple = self.obtener_proximo_cumpleaños(contacto)
            dias_restantes = (proximo_cumple - hoy).days
            if dias_restantes < 0:  # Nunca debería ocurrir, pero por seguridad
                proximo_cumple = proximo_cumple.replace(year=hoy.year + 1)
                dias_restantes = (proximo_cumple - hoy).days
            proximos.append((contacto, dias_restantes))
        return sorted(proximos, key=lambda x: x[1])

    # En gestor_cumpleaños.py
    def es_cumpleaños_hoy(self, contacto: Contacto) -> bool:
            proximo = self.obtener_proximo_cumpleaños(contacto)
            return proximo == date.today()

