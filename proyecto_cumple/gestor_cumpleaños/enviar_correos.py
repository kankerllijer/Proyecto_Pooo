
import smtplib
from email.mime.text import MIMEText

class EnviarCorreos:
    """Maneja el envío de correos electrónicos mediante SMTP seguro (STARTTLS)."""

    def __init__(self, servidor: str, puerto: int, remitente: str, contraseña: str):

        """Configura conexión SMTP.

        Args:
            servidor (str): Dirección del servidor SMTP (ej: smtp.gmail.com).
            puerto (int): Puerto SMTP (ej: 587 para TLS).
            remitente (str): Correo del remitente.
            contraseña (str): Contraseña de aplicación o cuenta.
        """

        self.servidor = servidor
        self.puerto = puerto
        self.remitente = remitente
        self.contraseña = contraseña

    def enviar_correo(self, destino: str, asunto: str, mensaje: str) -> bool:

        """Envía un correo electrónico.

        Args:
            destino (str): Correo del destinatario.
            asunto (str): Línea de asunto.
            mensaje (str): Cuerpo del mensaje (formato texto plano).

        Returns:
            bool: True si el envío fue exitoso, False en caso contrario.

        Raises:
            SMTPException: Si ocurre un error durante el envío.
        """
        try:
            # Crear mensaje MIME
            msg = MIMEText(mensaje)
            msg["Subject"] = asunto
            msg["From"] = self.remitente
            msg["To"] = destino

            # Conexión SMTP con STARTTLS
            with smtplib.SMTP(self.servidor, self.puerto) as server:
                server.starttls()
                server.login(self.remitente, self.contraseña)
                server.sendmail(self.remitente, destino, msg.as_string())
                return True
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False
