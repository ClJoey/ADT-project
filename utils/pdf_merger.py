import pdfkit
import os
import json
import platform
from datetime import datetime
from PyPDF2 import PdfMerger
from utils.logger import get_logger

logger = get_logger(__name__)

_COLS = ["asistencia", "jor_diaria", "domingos", "modificaciones", "diario", "incidentes"]
_COL_LABELS = {
    "asistencia":     "Asistencia",
    "jor_diaria":     "Jornada Diaria",
    "domingos":       "Domingos / Festivos",
    "modificaciones": "Modificaciones",
    "diario":         "Diario",
    "incidentes":     "Incidentes",
}


def _generar_html_resumen(summary_data):
    fecha = datetime.now().strftime("%d/%m/%Y")

    header_cells = "".join(
        f'<th style="padding:10px 14px;background:#1a1a2e;color:white;font-size:12px;'
        f'white-space:nowrap;text-align:center;">{_COL_LABELS[c]}</th>'
        for c in _COLS
    )

    rows = ""
    for emp in summary_data:
        reportes = emp.get("reportes", {})
        cells = ""
        for col in _COLS:
            if col in reportes:
                etiqueta = reportes[col]["etiqueta"]
                bg = reportes[col]["color"]
                txt = "white" if bg != "#ffc107" else "#5c4300"
                cells += (
                    f'<td style="padding:8px 10px;background:{bg};color:{txt};'
                    f'font-weight:bold;font-size:11px;text-align:center;'
                    f'border:1px solid #dee2e6;">{etiqueta}</td>'
                )
            else:
                cells += (
                    '<td style="padding:8px 10px;background:#e9ecef;color:#6c757d;'
                    'text-align:center;font-size:11px;border:1px solid #dee2e6;">—</td>'
                )
        rows += (
            f'<tr>'
            f'<td style="padding:8px 12px;font-weight:bold;font-size:12px;'
            f'border:1px solid #dee2e6;white-space:nowrap;">{emp["empresa"]}</td>'
            f'{cells}'
            f'</tr>\n'
        )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; padding: 30px; background: #f5f7fa; margin: 0; }}
  h1 {{ color: #1a1a2e; margin-bottom: 4px; font-size: 22px; }}
  p  {{ color: #666; margin: 0 0 20px; font-size: 13px; }}
  table {{ border-collapse: collapse; width: 100%; background: white;
           box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 6px; overflow: hidden; }}
  tr:nth-child(even) td {{ background-color: #f8f9fa; }}
</style>
</head>
<body>
  <h1>Resumen de Auditoría</h1>
  <p>Generado: {fecha} &mdash; Sistema de Control de Cumplimiento de Servicios</p>
  <table>
    <thead>
      <tr>
        <th style="padding:10px 14px;background:#1a1a2e;color:white;text-align:left;
                   font-size:12px;border:1px solid #dee2e6;">Empresa</th>
        {header_cells}
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>"""


def generar_reporte_unico(directorio_reportes, nombre_salida="Reporte_Consolidado_Auditoria.pdf"):
    if platform.system() == "Windows":
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    else:
        config = pdfkit.configuration()

    merger = PdfMerger()
    pdfs_temporales = []

    logger.info("Iniciando consolidación de reportes...")

    # Prepend summary page if data exists
    summary_json = os.path.join(directorio_reportes, "summary_data.json")
    if os.path.exists(summary_json):
        try:
            with open(summary_json, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
            resumen_html = _generar_html_resumen(summary_data)
            resumen_html_path = os.path.join(directorio_reportes, "_resumen_temp.html")
            resumen_pdf_path = os.path.join(directorio_reportes, "_resumen_temp.pdf")
            with open(resumen_html_path, "w", encoding="utf-8") as f:
                f.write(resumen_html)
            pdfkit.from_file(resumen_html_path, resumen_pdf_path, configuration=config)
            merger.append(resumen_pdf_path)
            pdfs_temporales += [resumen_html_path, resumen_pdf_path]
            logger.info("Página de resumen generada y agregada al inicio.")
        except Exception as e:
            logger.warning(f"No se pudo generar página de resumen: {e}")

    archivos_html = sorted([f for f in os.listdir(directorio_reportes) if f.endswith(".html") and not f.startswith("_")])

    for archivo in archivos_html:
        ruta_html = os.path.join(directorio_reportes, archivo)
        ruta_pdf_temp = ruta_html.replace(".html", "_temp.pdf")

        try:
            pdfkit.from_file(ruta_html, ruta_pdf_temp, configuration=config)
            merger.append(ruta_pdf_temp)
            pdfs_temporales.append(ruta_pdf_temp)
            logger.info(f"Procesado: {archivo}")
        except Exception as e:
            logger.error(f"Error procesando {archivo}: {e}")

    if pdfs_temporales:
        merger.write(nombre_salida)
        merger.close()
        logger.info(f"Reporte único creado: {nombre_salida}")

        for temp in pdfs_temporales:
            if os.path.exists(temp):
                os.remove(temp)
    else:
        logger.warning("No se generaron reportes para unir.")

if __name__ == "__main__":
    ruta_final = os.path.join("reports", "Reporte_Consolidado_Auditoria.pdf")
    generar_reporte_unico("reports", nombre_salida=ruta_final)
