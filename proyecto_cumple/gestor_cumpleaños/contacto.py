from datetime import date

class Contacto:
    """Representa un contacto con información personal relevante para cumpleaños.

    Atributos:
        nombre (str): Nombre completo del contacto.
        fecha_nacimiento (date): Fecha de nacimiento en formato YYYY-MM-DD.
        correo (str): Dirección de correo electrónico del contacto.
    """

    def __init__(self, nombre: str, fecha_nacimiento: date, correo: str):
        """Inicializa un nuevo contacto.

        Args:
            nombre (str): Nombre del contacto. No puede estar vacío.
            fecha_nacimiento (date): Fecha de nacimiento válida.
            correo (str): Correo electrónico válido.
        """
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.correo = correo
