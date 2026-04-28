import json
import os
import sys
import base64
import platform
import pdfkit
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger

logger = get_logger(__name__)

RESULTS_FILE = os.path.join("reports", "disponibilidad_results.json")
HTML_FILE    = os.path.join("reports", "disponibilidad_informe.html")
PDF_FILE     = os.path.join("reports", "disponibilidad_informe.pdf")


def _imagen_a_base64(ruta):
    try:
        if not ruta or not os.path.exists(ruta):
            return ""
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def generar_informe():
    if not os.path.exists(RESULTS_FILE):
        logger.warning("No hay resultados — no se genera informe.")
        return None

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        resultados = json.load(f)

    total     = len(resultados)
    fallos    = [r for r in resultados if r.get("estado") == "FAIL"]
    ok_count  = total - len(fallos)
    fecha     = datetime.now().strftime("%d/%m/%Y %H:%M")

    # -- Tabla resumen índice --
    filas_resumen = ""
    for r in resultados:
        color_resumen = "#28a745" if r.get("estado") == "OK" else "#dc3545"
        filas_resumen += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #eee;font-weight:bold;">{r['empresa']}</td>
            <td style="padding:10px;border-bottom:1px solid #eee;color:{color_resumen};font-weight:bold;">{r.get('estado','?')}</td>
            <td style="padding:10px;border-bottom:1px solid #eee;">
                {"Error: " + r['error'][:80] + "..." if r.get('error') and len(r.get('error','')) > 80 else r.get('error') or "Acceso verificado correctamente"}
            </td>
        </tr>"""

    resumen_tabla_html = f"""
    <div class="header" style="margin-top:20px;">
        <h2 style="color:#333;border-bottom:2px solid #eee;padding-bottom:10px;">Índice de Empresas (Resumen)</h2>
        <table style="width:100%;border-collapse:collapse;background:white;">
            <thead>
                <tr style="background:#f8f9fa;text-align:left;">
                    <th style="padding:12px;border-bottom:2px solid #dee2e6;">Empresa</th>
                    <th style="padding:12px;border-bottom:2px solid #dee2e6;">Estado</th>
                    <th style="padding:12px;border-bottom:2px solid #dee2e6;">Detalle</th>
                </tr>
            </thead>
            <tbody>{filas_resumen}</tbody>
        </table>
    </div>"""

    # -- Cards por empresa --
    bloques = ""
    for r in resultados:
        es_fail = r.get("estado") == "FAIL"
        color   = "#dc3545" if es_fail else "#28a745"
        badge   = r.get("estado", "?")

        if es_fail:
            detalle_html = f'<ul class="errores"><li>{r.get("error", "Sin detalle del error")}</li></ul>'
        else:
            detalle_html = '<ul class="errores" style="background:#d4edda;border-left-color:#28a745;"><li>Acceso a fisc_page verificado correctamente</li></ul>'

        img_data = _imagen_a_base64(r.get("captura"))
        if img_data:
            img_tag = f'<img src="data:image/png;base64,{img_data}" class="screenshot">'
        else:
            img_tag = '<p style="color:gray;padding:20px;border:1px dashed #ccc;text-align:center;">Captura no disponible</p>'

        bloques += f"""
        <div class="card" style="page-break-before:always;">
            <div class="card-header">
                <h2 style="margin:0;">{r['empresa']}</h2>
                <span class="badge" style="background:{color}">{badge}</span>
            </div>
            <div class="card-body">
                <h4 style="margin-top:0;">Resultado de Acceso</h4>
                {detalle_html}
                {img_tag}
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe de Disponibilidad — Fiscalización DT</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 20px;
            color: #333;
            page-break-after: avoid;
        }}
        .container {{ max-width: 1100px; margin: auto; page-break-after: avoid; }}
        .header {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        .summary-boxes {{ display: flex; gap: 15px; margin-top: 15px; }}
        .box {{ padding: 8px 18px; border-radius: 6px; font-weight: bold; font-size: 14px; }}
        .ok    {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .fail  {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .total {{ background: #e2e3e5; color: #383d41; border: 1px solid #d6d8db; }}
        .card {{
            background: white;
            margin-top: 40px;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.06);
            overflow: hidden;
            page-break-inside: avoid;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 25px;
            background: #fcfcfc;
            border-bottom: 1px solid #edf2f7;
        }}
        .badge {{ color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .card-body {{ padding: 25px; }}
        .errores {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 6px;
            border-left: 5px solid #ffeeba;
            list-style-position: inside;
        }}
        .screenshot {{
            margin-top: 20px;
            width: 100%;
            height: auto;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            display: block;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin:0;color:#2c3e50;">Informe de Disponibilidad — Fiscalización DT</h1>
            <p style="margin:5px 0;color:#666;"><b>Generado:</b> {fecha}</p>
            <div class="summary-boxes">
                <div class="box total">Evaluadas: {total}</div>
                <div class="box ok">OK: {ok_count}</div>
                <div class="box fail">Fallidas: {len(fallos)}</div>
            </div>
        </div>
        {resumen_tabla_html}
        {bloques}
    </div>
</body>
</html>"""

    os.makedirs("reports", exist_ok=True)
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"HTML generado: {HTML_FILE}")

    try:
        if platform.system() == "Windows":
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        else:
            config = pdfkit.configuration()

        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'no-outline': None,
            'quiet': '',
        }
        pdfkit.from_file(HTML_FILE, PDF_FILE, options=options, configuration=config)
        logger.info(f"PDF generado: {PDF_FILE}")
        return PDF_FILE
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        return None


if __name__ == "__main__":
    generar_informe()
