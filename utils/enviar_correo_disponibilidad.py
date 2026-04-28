import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_BA.jpg")
RESULTS_FILE = os.path.join("reports", "disponibilidad_results.json")
PDF_FILE = os.path.join("reports", "disponibilidad_informe.pdf")

DESTINATARIOS = [
    "joseph.cervantes@iplusd.cl",
    "nicolas.perez@baplicada.cl",
    "nicolas.santana@baplicada.cl",
    "cristian.zamora@baplicada.cl",
]

HTML_TEMPLATE = """\
<html>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f4f4;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:30px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">

        <tr>
          <td style="background:#7b1c1c;padding:28px 36px;">
            <p style="margin:0;color:#ffffff;font-size:22px;font-weight:bold;">
              &#9888; ALERTA &mdash; Disponibilidad Fiscalización DT
            </p>
            <p style="margin:6px 0 0;color:#f0a0a0;font-size:13px;">{fecha}</p>
          </td>
        </tr>

        <tr>
          <td style="padding:32px 36px;">
            <p style="margin:0 0 16px;color:#333333;font-size:15px;">Buenos días,</p>
            <p style="margin:0 0 20px;color:#555555;font-size:14px;line-height:1.7;">
              Se detectaron <strong>{n_fallos} empresa(s)</strong> que no pudieron acceder
              al portal de Fiscalización DT en la verificación automática del día de hoy.
            </p>
            <table width="100%" cellpadding="12" cellspacing="0"
                   style="background:#fff5f5;border-radius:6px;border-left:4px solid #c62828;margin-bottom:24px;">
              <tr><td>
                <p style="margin:0;color:#333;font-size:13px;line-height:1.8;">
                  <strong>&#128197; Fecha:</strong> {fecha}<br>
                  <strong>&#10060; Empresas con fallo:</strong> {n_fallos}<br>
                  <strong>&#9989; Empresas OK:</strong> {n_ok}
                </p>
              </td></tr>
            </table>
            <p style="margin:0 0 8px;color:#555;font-size:13px;">
              Se adjunta el informe PDF con el detalle completo y capturas de pantalla de cada empresa.
              Por favor revisar y atender los casos de sistemas caídos.
            </p>
            <p style="margin:20px 0 0;color:#888888;font-size:12px;">
              Este mensaje es generado automáticamente.
            </p>
          </td>
        </tr>

        <tr>
          <td style="background:#f0f0f0;padding:24px 36px;border-top:1px solid #e0e0e0;text-align:center;">
            <img src="cid:logo_ba" alt="Biometría Aplicada" width="180"
                 style="display:block;margin:0 auto 12px;"/>
            <p style="margin:0;color:#888888;font-size:11px;">
              &copy; {year} Biometría Aplicada SPA &mdash; Sistema de Monitoreo de Disponibilidad
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def enviar_alerta_disponibilidad():
    if not os.path.exists(RESULTS_FILE):
        logger.warning("No se encontró el archivo de resultados — no se envía correo.")
        return

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        try:
            resultados = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo resultados: {e}")
            return

    fallos = [r for r in resultados if r.get("estado") == "FAIL"]

    if not fallos:
        logger.info(f"Todas las empresas OK ({len(resultados)}/{len(resultados)}) — no se envía correo.")
        return

    logger.info(f"{len(fallos)} empresa(s) con fallo — enviando alerta...")

    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not remitente or not password:
        logger.error("Faltan EMAIL_USER o EMAIL_PASS en las variables de entorno.")
        return

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    year = datetime.now().year
    n_ok = len(resultados) - len(fallos)

    msg = MIMEMultipart("related")
    msg["Subject"] = f"ALERTA Disponibilidad DT — {len(fallos)} empresa(s) sin acceso — {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"] = remitente
    msg["To"] = ", ".join(DESTINATARIOS)

    html_body = HTML_TEMPLATE.format(
        fecha=fecha, year=year, n_fallos=len(fallos), n_ok=n_ok
    )
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as img_file:
            logo = MIMEImage(img_file.read())
            logo.add_header("Content-ID", "<logo_ba>")
            logo.add_header("Content-Disposition", "inline", filename="logo_BA.jpg")
            msg.attach(logo)

    if os.path.exists(PDF_FILE):
        with open(PDF_FILE, "rb") as f:
            adjunto = MIMEBase("application", "pdf")
            adjunto.set_payload(f.read())
            encoders.encode_base64(adjunto)
            adjunto.add_header("Content-Disposition", "attachment", filename="disponibilidad_informe.pdf")
            msg.attach(adjunto)
        logger.info("PDF adjuntado al correo.")
    else:
        logger.warning("No se encontró el PDF — se enviará el correo sin adjunto.")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remitente, password)
            server.send_message(msg)
        logger.info("Alerta enviada correctamente.")
    except Exception as e:
        logger.error(f"Error al enviar la alerta: {e}")


if __name__ == "__main__":
    enviar_alerta_disponibilidad()
