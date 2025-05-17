
import streamlit as st
import os
import sys
import csv
import random
import smtplib
import threading
import pytz

from datetime import datetime
from datetime import date
sys.path.append(os.getcwd())
from streamlit_calendar import calendar
from gestor_cumpleaños.gestor_cumpleaños import GestorCumpleaños
from gestor_cumpleaños.contacto import Contacto
from gestor_cumpleaños.enviar_correos import EnviarCorreos
from gestor_cumpleaños.almacenamiento import AlmacenamientoCSV
from email_validator import validate_email, EmailNotValidError

def main():
    st.set_page_config(
        page_title="Gestor de Cumpleaños",
        page_icon="🎂",
        layout="wide"
    )

    # Configuración SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = ""
    smtp_pass = ""

    if os.path.exists("smtp_config.csv"):
        with open("smtp_config.csv", newline="") as f:
            server, port, user, pwd = next(csv.reader(f))
            smtp_server = server
            smtp_port = int(port)
            smtp_user = user
            smtp_pass = pwd

    # Inicializar gestor
    almacenamiento = AlmacenamientoCSV()
    gestor = GestorCumpleaños(almacenamiento)

    # --- Pestañas ---
    tab1, tab2 = st.tabs([
        "📝 Agregar Contactos / 📅 Próximos Cumpleaños",
        "📧 Gestión de Correos"
    ])

    # --- Pestaña 1 ---
    with tab1:
        col1, col2 = st.columns([2, 3])

        # Columna 1: Formulario y lista
        with col1:
            with st.form("nuevo_contacto", clear_on_submit=True):
                st.subheader("➕ Nuevo Contacto")
                nombre = st.text_input("Nombre*")

                try:
                    fecha_nac = st.date_input("Fecha de nacimiento*", min_value=date(1900, 1, 1))
                    if fecha_nac > date.today():
                        st.error("⚠️ La fecha de nacimiento no puede ser futura.")
                except ValueError as e:
                    st.error(f"Error en fecha: {str(e)}")

                correo = st.text_input("Correo*")

                if st.form_submit_button("💾 Guardar Contacto"):
                    if not nombre or not correo:
                        st.error("⚠️ Campos obligatorios faltantes")
                    else:
                        try:
                            valid = validate_email(correo)
                            correo = valid.email
                            gestor.agregar_contacto(Contacto(nombre, fecha_nac, correo))
                            gestor.almacenamiento.guardar_contactos(gestor.contactos)
                            st.rerun()
                        except EmailNotValidError as e:
                            st.error(f"⚠️ Correo inválido: {str(e)}")

            st.subheader("🎉 Próximos Cumpleaños")
            if not gestor.contactos:
                st.warning("No hay contactos registrados")
            else:
                for contacto, dias in gestor.obtener_proximos_cumpleaños():
                    st.markdown(f"""
                    **{contacto.nombre}**
                    🗓️ {contacto.fecha_nacimiento.strftime('%d/%m')}
                    📧 {contacto.correo}
                    ⏳ **{dias}** días restantes
                    """)

        # Columna 2: Calendario
        with col2:
            st.subheader("📆 Calendario de Eventos")
            eventos = [
                {
                    "title": f"🎂 {c.nombre}",
                    "start": date.today().replace(
                        month=c.fecha_nacimiento.month,
                        day=c.fecha_nacimiento.day
                    ).isoformat(),
                    "color": "#FF6B6B"
                } for c in gestor.contactos
            ]
            calendar(
                events=eventos,
                options={
                    "initialView": "dayGridMonth",
                    "locale": "es",
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,dayGridWeek"
                    }
                }
            )

    # --- Pestaña 2 ---
    with tab2:
        config_col, msg_col = st.columns([2, 3])

        with config_col:
            with st.expander("⚙️ Configuración SMTP", expanded=True):
                with st.form("smtp_config"):
                    smtp_server_input = st.text_input("Servidor", smtp_server)
                    smtp_port_input = st.number_input("Puerto", value=smtp_port)
                    smtp_user_input = st.text_input("Correo", smtp_user)
                    smtp_pass_input = st.text_input("Contraseña", type="password", value=smtp_pass)

                    if st.form_submit_button("💾 Guardar"):
                        with open("smtp_config.csv", "w", newline="") as f:
                            f.write(f"{smtp_server_input},{smtp_port_input},{smtp_user_input},{smtp_pass_input}")
                        st.success("¡Configuración guardada!")
                        st.rerun()

            fecha_prueba = st.date_input(
                "🔧 Simular fecha",
                value=datetime.now(pytz.timezone("America/Mexico_City")).date()
            )

            st.subheader("👥 Destinatarios")
            options = [f"{c.nombre} <{c.correo}>" for c in gestor.contactos]
            selected = st.multiselect("Seleccionar:", options=options, default=options)
            correos_destino = [s.split("<")[1].replace(">", "") for s in selected]

            st.subheader("🔠 Tipo de Mensaje")
            tipo_mensaje = st.radio(
                "Modo:",
                options=["🎲 Aleatorio", "✉️ Personalizado"],
                horizontal=True
            )

            mensaje_a_enviar = ""
            if tipo_mensaje == "🎲 Aleatorio":
                try:
                    with open("mensajes.csv") as f:
                        mensajes = [line.strip() for line in f]
                    if mensajes:
                        mensaje_a_enviar = random.choice(mensajes)
                        st.success(f"📩 Seleccionado: _{mensaje_a_enviar}_")
                    else:
                        st.error("⚠️ ¡Agrega mensajes primero!")
                except FileNotFoundError:
                    st.error("❌ Archivo no encontrado")
            else:
                mensaje_a_enviar = st.text_area(
                    "Escribe tu mensaje:",
                    height=150,
                    placeholder="¡Feliz cumple {nombre}! 🎉"
                )

            if st.button("🚀 Enviar Correos", key="btn_envio"):
                if not mensaje_a_enviar.strip():
                    st.error("❌ ¡Escribe o selecciona un mensaje!")
                else:
                    success = 0
                    with st.status("Enviando...", expanded=True) as status:
                        for contacto in gestor.contactos:
                            if contacto.correo not in correos_destino:
                                continue
                            prox_cumple = gestor.obtener_proximo_cumpleaños(contacto).replace(year=fecha_prueba.year)
                            if prox_cumple == fecha_prueba:
                                mensaje_final = mensaje_a_enviar.format(nombre=contacto.nombre)
                                try:
                                    if EnviarCorreos(
                                        smtp_server, smtp_port, smtp_user, smtp_pass
                                    ).enviar_correo(
                                        contacto.correo,
                                        "🎉 ¡Feliz Cumple!",
                                        mensaje_final
                                    ):
                                        success += 1
                                        st.write(f"✅ {contacto.nombre}")
                                except Exception as e:
                                    st.error(f"⚠️ No se pudo enviar a {contacto.nombre}: {e}")
                    st.success(f"**Resultado:** ✔️ {success} exitosos | ❌ {len(correos_destino)-success} fallos")

        with msg_col:
            st.subheader("📚 Mensajes Guardados")
            nuevo_msg = st.text_input("Nuevo mensaje:")
            if st.button("💾 Guardar Mensaje"):
                if nuevo_msg.strip():
                    with open("mensajes.csv", "a") as f:
                        f.write(f"{nuevo_msg}\n")
                    st.rerun()

            try:
                with open("mensajes.csv") as f:
                    mensajes = f.readlines()
                if mensajes:
                    for i, msg in enumerate(mensajes):
                        cols = st.columns([6, 1])
                        cols[0].write(f"{i+1}. {msg.strip()}")
                        if cols[1].button("🗑️", key=f"del_{i}"):
                            del mensajes[i]
                            with open("mensajes.csv", "w") as f:
                                f.writelines(mensajes)
                            st.rerun()
            except FileNotFoundError:
                st.warning("📭 No hay mensajes")

        st.markdown("### Correo de prueba")
        dest_prueba = st.text_input("Email de prueba", key="dest_prueba")
        asun_prueba = st.text_input("Asunto de prueba", key="asun_prueba")
        msg_prueba = st.text_area("Mensaje de prueba", key="msg_prueba")
        if st.button("✉️ Enviar correo de prueba", key="btn_prueba"):
            try:
                EnviarCorreos(
                    smtp_server, smtp_port, smtp_user, smtp_pass
                ).enviar_correo(dest_prueba, asun_prueba, msg_prueba)
                st.success("✅ Correo de prueba enviado")
            except Exception as e:
                st.error(f"Error al enviar correo de prueba: {e}")

if __name__ == "__main__":
    from backend_automation import enviar_felicitaciones_automaticas
    threading.Thread(target=enviar_felicitaciones_automaticas, daemon=True).start()
    main()
