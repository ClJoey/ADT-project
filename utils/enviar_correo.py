import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

def enviar_reporte():
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    destinatarios = ["joseph.cervantes@inacapmail.cl"] 

    if not remitente or not password:
        print(" Error: Faltan EMAIL_USER o EMAIL_PASS en los Secretos de GitHub.")
        return

    fecha = datetime.now().strftime("%d/%m/%Y")
    
    msg = EmailMessage()
    msg['Subject'] = f' Auditoría DT Completada - {fecha}'
    msg['From'] = remitente
    msg['To'] = ", ".join(destinatarios)
    msg.set_content(f"Hola,\n\nSe adjunta el reporte consolidado de auditoría generado hoy {fecha}.\n\nSaludos,\nBot de Auditoría Automática.")

    # --- BUSCADOR ULTRA-FLEXIBLE ---
    archivo_zip = None
    print(" Buscando el archivo ZIP...")

    # Revisamos la raíz y la carpeta de reportes
    for ruta in [".", "reports"]:
        if os.path.exists(ruta):
            for f in os.listdir(ruta):
                nombre_f = f.lower()
                #  Coincide si es ZIP y contiene "paquete" O "auditoria"
                if nombre_f.endswith(".zip") and ("paquete" in nombre_f or "auditoria" in nombre_f):
                    archivo_zip = os.path.join(ruta, f)
                    break
        if archivo_zip: break

    if archivo_zip:
        print(f" Archivo detectado: {archivo_zip}")
        try:
            with open(archivo_zip, 'rb') as f:
                msg.add_attachment(
                    f.read(),
                    maintype='application',
                    subtype='zip',
                    filename=os.path.basename(archivo_zip)
                )

            print(" Conectando a Outlook (smtp.office365.com)...")
            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)
            server.quit()
            print(" ¡EL CORREO SE ENVIÓ CORRECTAMENTE!")
            
        except Exception as e:
            print(f" Error al enviar el correo: {e}")
            print("💡 Tip: Si el error es de 'Authentication', revisa tu App Password en Outlook.")
    else:
        print(" Error: No se encontró ningún archivo ZIP con 'Paquete' o 'Auditoria'.")

if __name__ == "__main__":
    enviar_reporte()